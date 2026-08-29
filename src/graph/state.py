from typing import Any, TypedDict

from src.evidence import RetrievedEvidence


class TriageState(TypedDict, total=False):
    message: str
    normalized_message: str
    top_k: int
    intent: str
    intent_confidence: float
    urgency: str
    escalate: bool
    escalation_reason: str
    retrieved_cases: list[dict[str, Any]]
    retrieved_evidence: tuple[RetrievedEvidence, ...]
    suggested_response: str
    evidence_references: list[str]
    citation_integrity: bool
    grounded: bool
    grounding_score: float
    unsupported_claims: list[str]
    confidence: float
    next_action: str
    provider_used: str
    model_used: str
    cached: bool
    fallback_used: bool
    degraded_mode: bool
    total_latency_ms: float
    trace: list[dict[str, Any]]
