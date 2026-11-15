import json
import re
import time
from collections.abc import Callable, Collection
from pathlib import Path
from typing import Any

from langgraph.graph import END, START, StateGraph

from src.evidence import RetrievedEvidence
from src.graph.state import TriageState
from src.llm.base import LLMRequest
from src.llm.router import ProviderRouter
from src.policy import SAFE_ABSTENTION_RESPONSE, ProposalVerifier, review_proposals
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
        approved_policy_references: Collection[str] = (),
        policy_verifier: ProposalVerifier | None = None,
    ) -> None:
        self.router = router
        self.retriever = retriever
        self.task_routes = task_routes or {}
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.max_context_chars = max_context_chars
        self.clock = clock
        self.approved_policy_references = frozenset(approved_policy_references)
        self.policy_verifier = policy_verifier
        self.graph = self._build_graph()

    def run(self, message: str, top_k: int) -> dict[str, Any]:
        started = self.clock()
        initial: TriageState = {
            "message": message,
            "top_k": top_k,
            "trace": [],
            "retrieved_cases": [],
            "retrieved_evidence": (),
            "candidate_proposals": [],
            "proposal_checks": [],
            "verified_proposals": [],
            "policy_status": "no_approved_policy",
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
            ("policy_gate", self._policy_gate),
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
        if not isinstance(intent, str) or intent not in INTENTS:
            intent = "other"
        return {
            "intent": intent,
            "degraded_mode": state.get("degraded_mode", False) or response.degraded_mode,
            "fallback_used": state.get("fallback_used", False) or response.fallback_used,
            "trace": self._trace(
                state,
                "classify_intent",
                started,
                input_summary=f"normalized_length={len(state['normalized_message'])}",
                output_summary=f"intent={intent}",
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
        if not isinstance(urgency, str) or urgency not in URGENCIES:
            urgency = "medium"
        escalate = payload.get("escalate") is True or urgency in {"high", "critical"}
        reason = str(payload.get("escalation_reason", ""))
        return {
            "urgency": urgency,
            "escalate": escalate,
            "escalation_reason": reason,
            "degraded_mode": state.get("degraded_mode", False) or response.degraded_mode,
            "fallback_used": state.get("fallback_used", False) or response.fallback_used,
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
        intent = state.get("intent")
        results = self.retriever.search(
            state["normalized_message"],
            top_k=state["top_k"],
            intent=intent,
        )
        unfiltered_fallback = False
        if not results and intent and intent != "other":
            results = self.retriever.search(
                state["normalized_message"], top_k=state["top_k"], intent=None
            )
            unfiltered_fallback = True
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
            "similar_case_references": [item.reference_id for item in evidence],
            "trace": self._trace(
                state,
                "retrieve_similar_cases",
                started,
                input_summary=f"intent={state.get('intent', 'other')}; top_k={state['top_k']}",
                output_summary=(
                    f"retrieved={len(evidence)}; "
                    f"unfiltered_fallback={str(unfiltered_fallback).lower()}"
                ),
                component="qdrant",
                retrieved_document_count=len(evidence),
                similar_case_references=[item.reference_id for item in evidence],
            ),
        }

    def _generate_support_response(self, state: TriageState) -> dict[str, Any]:
        started = self.clock()
        response = self._call(
            "generate_response",
            workflow_instructions=self._prompt(
                "generate_response",
                intent=state["intent"],
                urgency=state["urgency"],
            ),
            user_ticket=state["normalized_message"],
        )
        payload = self._json(response.text)
        raw_proposals = payload.get("proposals")
        proposal_parse_failed = False
        if isinstance(raw_proposals, list):
            if len(raw_proposals) > 8 or any(
                not isinstance(proposal, str) or not proposal.strip() or len(proposal) > 500
                for proposal in raw_proposals
            ):
                proposals: list[str] = []
                proposal_parse_failed = True
            else:
                proposals = [proposal.strip() for proposal in raw_proposals]
        elif isinstance(payload.get("suggested_response"), str):
            # Older providers return prose; keep it as one withheld candidate.
            proposals = [payload["suggested_response"].strip()]
            proposal_parse_failed = not proposals[0]
        else:
            proposals = []
            proposal_parse_failed = bool(response.text.strip())

        suggested = SAFE_ABSTENTION_RESPONSE
        return {
            "suggested_response": suggested,
            "candidate_proposals": proposals,
            "proposal_parse_failed": proposal_parse_failed,
            "provider_used": response.provider,
            "model_used": response.model,
            "cached": response.cached,
            "fallback_used": state.get("fallback_used", False) or response.fallback_used,
            "degraded_mode": state.get("degraded_mode", False) or response.degraded_mode,
            "trace": self._trace(
                state,
                "generate_support_response",
                started,
                input_summary=f"intent={state['intent']}; no_policy_evidence=true",
                output_summary=f"candidate_proposal_count={len(proposals)}",
                component="llm_router",
                response=response,
            ),
        }

    def _policy_gate(self, state: TriageState) -> dict[str, Any]:
        started = self.clock()
        review = review_proposals(
            state.get("candidate_proposals", []),
            approved_policy_references=self.approved_policy_references,
            verifier=self.policy_verifier,
            proposal_parse_failed=state.get("proposal_parse_failed", False),
            generation_degraded=state.get("degraded_mode", False)
            or state.get("fallback_used", False),
        )
        checks = [
            {
                "proposal_id": check.proposal_id,
                "status": check.status,
                "policy_references": list(check.policy_references),
                "verification_result": check.verification_result,
                "verification_method": check.verification_method,
            }
            for check in review.checks
        ]
        verified_proposals = [
            {
                "proposal_id": proposal.proposal_id,
                "text": proposal.text,
                "policy_references": list(proposal.policy_references),
                "verification_result": proposal.verification_result,
                "verification_method": proposal.verification_method,
            }
            for proposal in review.verified_proposals
        ]
        if review.status != "verified" or not verified_proposals:
            suggested = SAFE_ABSTENTION_RESPONSE
        else:
            suggested = "\n".join(proposal["text"] for proposal in verified_proposals)
        policy_references = (
            sorted({reference for check in checks for reference in check["policy_references"]})
            if review.status == "verified"
            else []
        )
        return {
            "suggested_response": suggested,
            "policy_status": review.status,
            "proposal_checks": checks,
            "verified_proposals": verified_proposals,
            "policy_references": policy_references,
            "trace": self._trace(
                state,
                "policy_gate",
                started,
                input_summary=f"proposal_count={len(state.get('candidate_proposals', []))}",
                output_summary=f"policy_status={review.status}; checks={len(checks)}",
                component="policy_gate",
                policy_status=review.status,
                policy_references=policy_references,
            ),
        }

    def _suggest_next_action(self, state: TriageState) -> dict[str, Any]:
        started = self.clock()
        if state.get("policy_status") != "verified" or not state.get("verified_proposals"):
            action = "manual_review"
        elif state["urgency"] in {"high", "critical"} or state.get("escalate", False):
            action = "escalate_to_human"
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
                    f"policy_status={state.get('policy_status', 'no_approved_policy')}"
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
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    @staticmethod
    def _prompt(name: str, **values: str) -> str:
        template = (PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8")
        return template.format(**values)

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
        policy_status: str | None = None,
        similar_case_references: list[str] | None = None,
        policy_references: list[str] | None = None,
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
                "policy_status": policy_status,
                "similar_case_references": similar_case_references or [],
                "policy_references": policy_references or [],
                "error_category": None,
            },
        ]
