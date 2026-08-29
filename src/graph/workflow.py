import json
import re
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from langgraph.graph import END, START, StateGraph

from src.evidence import RetrievedEvidence
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
        started = self.clock()
        initial: TriageState = {
            "message": message,
            "top_k": top_k,
            "trace": [],
            "retrieved_cases": [],
            "retrieved_evidence": (),
            "unsupported_claims": [],
            "cached": False,
            "fallback_used": False,
            "degraded_mode": False,
        }
        result = dict(self.graph.invoke(initial))
        result["total_latency_ms"] = round((self.clock() - started) * 1000, 2)
        return result

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
            "trace": self._trace(
                state,
                "normalize_message",
                started,
                input_summary=f"message_length={len(state['message'])}",
                output_summary=f"normalized_length={len(normalized)}",
                component="local",
            ),
        }

    def _classify_intent(self, state: TriageState) -> dict[str, Any]:
        started = self.clock()
        response = self._call(
            "classify_intent",
            workflow_instructions=self._prompt("classify_intent"),
            user_ticket=state["normalized_message"],
        )
        payload = self._json(response.text)
        intent = payload.get("intent", "other")
        if intent not in INTENTS:
            intent = "other"
        confidence = self._unit_interval(payload.get("confidence", 0))
        return {
            "intent": intent,
            "intent_confidence": confidence,
            "trace": self._trace(
                state,
                "classify_intent",
                started,
                input_summary=f"normalized_length={len(state['normalized_message'])}",
                output_summary=f"intent={intent}; confidence={confidence:.2f}",
                component="llm_router",
                response=response,
            ),
        }

    def _detect_urgency(self, state: TriageState) -> dict[str, Any]:
        started = self.clock()
        response = self._call(
            "detect_urgency",
            workflow_instructions=self._prompt("detect_urgency"),
            user_ticket=state["normalized_message"],
        )
        payload = self._json(response.text)
        urgency = payload.get("urgency", "medium")
        if urgency not in URGENCIES:
            urgency = "medium"
        escalate = bool(payload.get("escalate", False)) or urgency in {"high", "critical"}
        reason = str(payload.get("escalation_reason", ""))
        return {
            "urgency": urgency,
            "escalate": escalate,
            "escalation_reason": reason,
            "trace": self._trace(
                state,
                "detect_urgency",
                started,
                input_summary=f"intent={state['intent']}",
                output_summary=f"urgency={urgency}; escalate={str(escalate).lower()}",
                component="llm_router",
                response=response,
            ),
        }

    def _retrieve_similar_cases(self, state: TriageState) -> dict[str, Any]:
        started = self.clock()
        results = self.retriever.search(
            state["normalized_message"],
            top_k=state["top_k"],
            intent=state.get("intent"),
        )
        evidence = tuple(
            RetrievedEvidence(
                reference_id=result.ticket_id,
                message=result.message,
                intent=result.intent,
                response=result.response,
                source=result.source,
                score=result.score,
                created_at=result.created_at,
                metadata=result.metadata,
            )
            for result in results
        )
        return {
            "retrieved_evidence": evidence,
            "retrieved_cases": [item.to_public_dict() for item in evidence],
            "trace": self._trace(
                state,
                "retrieve_similar_cases",
                started,
                input_summary=f"intent={state.get('intent', 'other')}; top_k={state['top_k']}",
                output_summary=f"retrieved={len(evidence)}",
                component="qdrant",
                retrieved_document_count=len(evidence),
                evidence_references=[item.reference_id for item in evidence],
            ),
        }

    def _generate_support_response(self, state: TriageState) -> dict[str, Any]:
        started = self.clock()
        evidence = tuple(state.get("retrieved_evidence", ()))
        response = self._call(
            "generate_response",
            workflow_instructions=self._prompt(
                "generate_response",
                intent=state["intent"],
                urgency=state["urgency"],
            ),
            user_ticket=state["normalized_message"],
            evidence=evidence,
        )
        payload = self._json(response.text)
        suggested = str(payload.get("suggested_response", response.text)).strip()
        references, citation_integrity = self._validate_evidence_references(
            payload.get("evidence_references"), evidence
        )
        if citation_integrity and references:
            suggested = f"{suggested}\n\nInternal evidence: {', '.join(references)}"
        return {
            "suggested_response": suggested,
            "evidence_references": references,
            "citation_integrity": citation_integrity,
            "provider_used": response.provider,
            "model_used": response.model,
            "cached": response.cached,
            "fallback_used": response.fallback_used,
            "degraded_mode": response.degraded_mode,
            "trace": self._trace(
                state,
                "generate_support_response",
                started,
                input_summary=f"intent={state['intent']}; evidence_count={len(evidence)}",
                output_summary=f"draft_length={len(suggested)}",
                component="llm_router",
                response=response,
                evidence_references=references,
            ),
        }

    def _grounding_check(self, state: TriageState) -> dict[str, Any]:
        started = self.clock()
        evidence = tuple(state.get("retrieved_evidence", ()))
        response = self._call(
            "grounding_check",
            workflow_instructions=self._prompt("grounding_check"),
            user_ticket=state["normalized_message"],
            candidate_response=state["suggested_response"],
            evidence=evidence,
        )
        payload = self._json(response.text)
        score = self._unit_interval(payload.get("grounding_score", 0))
        confidence = self._unit_interval(payload.get("confidence", score))
        has_evidence = bool(evidence)
        citation_integrity = bool(state.get("citation_integrity", True))
        degraded = state.get("degraded_mode", False) or response.degraded_mode
        grounded = (
            bool(payload.get("grounded", False))
            and has_evidence
            and citation_integrity
            and bool(state.get("evidence_references"))
            and not degraded
        )
        raw_unsupported_claims = payload.get("unsupported_claims") or []
        unsupported_claims = (
            [str(claim) for claim in raw_unsupported_claims]
            if isinstance(raw_unsupported_claims, list)
            else []
        )
        if not has_evidence and "No retrieved cases were available." not in unsupported_claims:
            unsupported_claims.append("No retrieved cases were available.")
        if degraded and "Generation used a degraded provider fallback." not in unsupported_claims:
            unsupported_claims.append("Generation used a degraded provider fallback.")
        if not citation_integrity:
            unsupported_claims.append("Unknown retrieved evidence references were rejected.")
        if not grounded:
            score = min(score, 0.25)
            confidence = min(confidence, 0.4)
        return {
            "grounded": grounded,
            "grounding_score": score,
            "unsupported_claims": unsupported_claims,
            "confidence": confidence,
            "degraded_mode": degraded,
            "fallback_used": state.get("fallback_used", False) or response.fallback_used,
            "trace": self._trace(
                state,
                "grounding_check",
                started,
                input_summary=f"draft_length={len(state['suggested_response'])}",
                output_summary=(f"grounded={grounded}; score={score:.2f}"),
                component="llm_router",
                response=response,
                grounding_result=grounded,
                evidence_references=list(state.get("evidence_references", [])),
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
            state.get("escalate") and state["intent"] in {"complaint", "refund_request"}
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
                input_summary=(
                    f"intent={state['intent']}; urgency={state['urgency']}; "
                    f"grounded={state.get('grounded', False)}"
                ),
                output_summary=f"next_action={action}",
                component="rules",
            ),
        }

    def _call(
        self,
        task: str,
        workflow_instructions: str,
        user_ticket: str,
        evidence: tuple[RetrievedEvidence, ...] = (),
        candidate_response: str = "",
    ):
        provider, model = self.task_routes.get(task, ("mock", "mock-small"))
        return self.router.generate(
            LLMRequest(
                task=task,
                workflow_instructions=workflow_instructions,
                user_ticket=user_ticket,
                model=model,
                evidence=evidence,
                candidate_response=candidate_response,
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
    def _unit_interval(value: Any, default: float = 0.0) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            numeric = default
        return min(1.0, max(0.0, numeric))

    @staticmethod
    def _prompt(name: str, **values: str) -> str:
        template = (PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8")
        return template.format(**values)

    @staticmethod
    def _validate_evidence_references(
        raw_references: Any,
        evidence: tuple[RetrievedEvidence, ...],
    ) -> tuple[list[str], bool]:
        allowed = {item.reference_id for item in evidence}
        if raw_references is None:
            references = [item.reference_id for item in evidence]
        elif isinstance(raw_references, list) and all(
            isinstance(reference, str) and reference.strip() for reference in raw_references
        ):
            references = list(dict.fromkeys(reference.strip() for reference in raw_references))
        else:
            return [], False
        if any(reference not in allowed for reference in references):
            return [], False
        if evidence and not references:
            return [], False
        return references, True

    def _trace(
        self,
        state: TriageState,
        node: str,
        started: float,
        input_summary: str,
        output_summary: str,
        component: str,
        response: Any | None = None,
        retrieved_document_count: int = 0,
        grounding_result: bool | None = None,
        evidence_references: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        provider = getattr(response, "provider", None)
        model = getattr(response, "model", None)
        cache_hit = bool(getattr(response, "cached", False))
        fallback = bool(getattr(response, "fallback_used", False))
        degraded = bool(getattr(response, "degraded_mode", False))
        return [
            *state.get("trace", []),
            {
                "node": node,
                "detail": output_summary,
                "duration_ms": round((self.clock() - started) * 1000, 2),
                "status": "completed",
                "input_summary": input_summary,
                "output_summary": output_summary,
                "component": component,
                "provider": provider,
                "model": model,
                "cache_hit": cache_hit,
                "fallback": fallback,
                "degraded_mode": degraded,
                "retrieved_document_count": retrieved_document_count,
                "grounding_result": grounding_result,
                "evidence_references": evidence_references or [],
                "error_category": None,
            },
        ]
