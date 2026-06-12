import json
import re
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from langgraph.graph import END, START, StateGraph

from src.graph.state import TriageState
from src.llm.base import LLMRequest
from src.llm.router import ProviderRouter
from src.retrieval.retriever import QdrantRetriever

INTENTS = {
    "delivery_issue",
    "refund_request",
    "billing_issue",
    "technical_issue",
    "account_access",
    "product_question",
    "complaint",
    "cancellation",
    "other",
}
URGENCIES = {"low", "medium", "high", "critical"}
PROMPT_DIR = Path(__file__).resolve().parents[2] / "prompts"


class TriageWorkflow:
    def __init__(
        self,
        router: ProviderRouter,
        retriever: QdrantRetriever,
        task_routes: dict[str, tuple[str, str]] | None = None,
        temperature: float = 0.2,
        max_output_tokens: int = 512,
        max_context_chars: int = 4000,
        clock: Callable[[], float] = time.perf_counter,
    ) -> None:
        self.router = router
        self.retriever = retriever
        self.task_routes = task_routes or {}
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.max_context_chars = max_context_chars
        self.clock = clock
        self.graph = self._build_graph()

    def run(self, message: str, top_k: int) -> dict[str, Any]:
        initial: TriageState = {
            "message": message,
            "top_k": top_k,
            "trace": [],
            "retrieved_cases": [],
            "unsupported_claims": [],
            "cached": False,
            "degraded_mode": False,
        }
        return dict(self.graph.invoke(initial))

    def _build_graph(self):
        graph = StateGraph(TriageState)
        nodes = [
            ("normalize_message", self._normalize_message),
            ("classify_intent", self._classify_intent),
            ("detect_urgency", self._detect_urgency),
            ("retrieve_similar_cases", self._retrieve_similar_cases),
            ("generate_support_response", self._generate_support_response),
            ("grounding_check", self._grounding_check),
            ("suggest_next_action", self._suggest_next_action),
        ]
        for name, node in nodes:
            graph.add_node(name, node)
        graph.add_edge(START, nodes[0][0])
        for current, following in zip(nodes, nodes[1:], strict=False):
            graph.add_edge(current[0], following[0])
        graph.add_edge(nodes[-1][0], END)
        return graph.compile()

    def _normalize_message(self, state: TriageState) -> dict[str, Any]:
        started = self.clock()
        normalized = re.sub(r"\s+", " ", state["message"]).strip()
        return {
            "normalized_message": normalized,
            "trace": self._trace(state, "normalize_message", started, "Message normalized"),
        }

    def _classify_intent(self, state: TriageState) -> dict[str, Any]:
        started = self.clock()
        response = self._call(
            "classify_intent",
            self._prompt("classify_intent", message=state["normalized_message"]),
        )
        payload = self._json(response.text)
        intent = payload.get("intent", "other")
        if intent not in INTENTS:
            intent = "other"
        confidence = float(payload.get("confidence", 0))
        return {
            "intent": intent,
            "intent_confidence": confidence,
            "trace": self._trace(
                state,
                "classify_intent",
                started,
                f"Intent: {intent} ({confidence:.0%})",
            ),
        }

    def _detect_urgency(self, state: TriageState) -> dict[str, Any]:
        started = self.clock()
        response = self._call(
            "detect_urgency",
            self._prompt("detect_urgency", message=state["normalized_message"]),
        )
        payload = self._json(response.text)
        urgency = payload.get("urgency", "medium")
        if urgency not in URGENCIES:
            urgency = "medium"
        escalate = bool(payload.get("escalate", urgency in {"high", "critical"}))
        reason = str(payload.get("escalation_reason", ""))
        return {
            "urgency": urgency,
            "escalate": escalate,
            "escalation_reason": reason,
            "trace": self._trace(
                state,
                "detect_urgency",
                started,
                f"Urgency: {urgency}; escalate: {str(escalate).lower()}",
            ),
        }

    def _retrieve_similar_cases(self, state: TriageState) -> dict[str, Any]:
        started = self.clock()
        results = self.retriever.search(
            state["normalized_message"],
            top_k=state["top_k"],
            intent=state.get("intent"),
        )
        cases = [result.to_dict() for result in results]
        return {
            "retrieved_cases": cases,
            "trace": self._trace(
                state,
                "retrieve_similar_cases",
                started,
                f"Retrieved {len(cases)} similar cases",
            ),
        }

    def _generate_support_response(self, state: TriageState) -> dict[str, Any]:
        started = self.clock()
        context = self._context(state["retrieved_cases"])
        response = self._call(
            "generate_response",
            self._prompt(
                "generate_response",
                message=state["normalized_message"],
                intent=state["intent"],
                urgency=state["urgency"],
            ),
            context=context,
        )
        payload = self._json(response.text)
        suggested = str(payload.get("suggested_response", response.text)).strip()
        case_ids = [case["ticket_id"] for case in state["retrieved_cases"]]
        if case_ids:
            suggested = f"{suggested}\n\nInternal evidence: {', '.join(case_ids)}"
        return {
            "suggested_response": suggested,
            "provider_used": response.provider,
            "model_used": response.model,
            "cached": response.cached,
            "degraded_mode": response.degraded_mode,
            "trace": self._trace(
                state,
                "generate_support_response",
                started,
                f"Response generated by {response.provider}/{response.model}",
            ),
        }

    def _grounding_check(self, state: TriageState) -> dict[str, Any]:
        started = self.clock()
        context = self._context(state["retrieved_cases"])
        response = self._call(
            "grounding_check",
            self._prompt(
                "grounding_check",
                response=state["suggested_response"],
            ),
            context=context,
        )
        payload = self._json(response.text)
        score = float(payload.get("grounding_score", 0))
        return {
            "grounded": bool(payload.get("grounded", False)),
            "grounding_score": score,
            "unsupported_claims": list(payload.get("unsupported_claims") or []),
            "confidence": float(payload.get("confidence", score)),
            "degraded_mode": state.get("degraded_mode", False) or response.degraded_mode,
            "trace": self._trace(
                state,
                "grounding_check",
                started,
                f"Grounding score: {score:.0%}",
            ),
        }

    def _suggest_next_action(self, state: TriageState) -> dict[str, Any]:
        started = self.clock()
        message = state["normalized_message"].lower()
        if not state.get("grounded", False):
            action = "manual_review"
        elif state["intent"] == "delivery_issue" and "order id" not in message:
            action = "ask_for_order_id"
        elif state["urgency"] == "critical" or (
            state.get("escalate")
            and state["intent"] in {"complaint", "refund_request"}
        ):
            action = "escalate_to_human"
        elif state["intent"] in {"technical_issue", "account_access", "other"}:
            action = "request_more_info"
        else:
            action = "reply_to_customer"
        return {
            "next_action": action,
            "trace": self._trace(
                state,
                "suggest_next_action",
                started,
                f"Next action: {action}",
            ),
        }

    def _call(self, task: str, prompt: str, context: str = ""):
        provider, model = self.task_routes.get(task, ("mock", "mock-small"))
        return self.router.generate(
            LLMRequest(
                task=task,
                prompt=prompt,
                model=model,
                context=context,
                temperature=self.temperature,
                max_output_tokens=self.max_output_tokens,
            ),
            preferred_provider=provider,
        )

    @staticmethod
    def _json(text: str) -> dict[str, Any]:
        candidate = text.strip()
        if candidate.startswith("```"):
            candidate = re.sub(r"^```(?:json)?\s*|\s*```$", "", candidate)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def _prompt(name: str, **values: str) -> str:
        template = (PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8")
        return template.format(**values)

    def _context(self, cases: list[dict[str, Any]]) -> str:
        context = "\n\n".join(
            (
                f"Case {case['ticket_id']}\n"
                f"Intent: {case['intent']}\n"
                f"Message: {case['message']}\n"
                f"Past response: {case['response'] or 'Not provided'}\n"
                f"Source: {case['source']}"
            )
            for case in cases
        )
        return context[: self.max_context_chars]

    def _trace(
        self,
        state: TriageState,
        node: str,
        started: float,
        detail: str,
    ) -> list[dict[str, Any]]:
        return [
            *state.get("trace", []),
            {
                "node": node,
                "detail": detail,
                "duration_ms": round((self.clock() - started) * 1000, 2),
                "status": "completed",
            },
        ]
