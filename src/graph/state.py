from typing import Any, TypedDict


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
    suggested_response: str
    grounded: bool
    grounding_score: float
    unsupported_claims: list[str]
    confidence: float
    next_action: str
    provider_used: str
    model_used: str
    cached: bool
    degraded_mode: bool
    trace: list[dict[str, Any]]
