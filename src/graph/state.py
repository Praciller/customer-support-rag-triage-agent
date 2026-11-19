from typing import Any, TypedDict

from src.evidence import RetrievedEvidence


class TriageState(TypedDict, total=False):
    message: str
    normalized_message: str
    top_k: int
    intent: str
    urgency: str
    escalate: bool
    escalation_reason: str
    retrieved_cases: list[dict[str, Any]]
    retrieved_evidence: tuple[RetrievedEvidence, ...]
    suggested_response: str
    candidate_proposals: list[str]
    proposal_parse_failed: bool
    proposal_checks: list[dict[str, Any]]
    verified_proposals: list[dict[str, Any]]
    policy_status: str
    similar_case_references: list[str]
    policy_references: list[str]
    next_action: str
    provider_used: str
    model_used: str
    cached: bool
    fallback_used: bool
    degraded_mode: bool
    total_latency_ms: float
    trace: list[dict[str, Any]]
