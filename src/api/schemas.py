from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.config.settings import get_settings


class TriageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str
    top_k: int = Field(default=5, ge=1)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("message must not be empty")
        if len(value) > get_settings().max_message_chars:
            raise ValueError("message exceeds configured length limit")
        return value

    @field_validator("top_k")
    @classmethod
    def validate_top_k(cls, value: int) -> int:
        if value > get_settings().max_top_k:
            raise ValueError("top_k exceeds configured limit")
        return value


class SearchRequest(TriageRequest):
    intent: str | None = None


class IngestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recreate: bool = False
    sample_size: int | None = Field(default=None, ge=1, le=1000)


class TraceStepResponse(BaseModel):
    node: str
    detail: str
    duration_ms: float = Field(ge=0)
    status: str
    input_summary: str
    output_summary: str
    component: str
    provider: str | None = None
    model: str | None = None
    cache_hit: bool
    fallback: bool
    degraded_mode: bool
    retrieved_document_count: int = Field(ge=0)
    grounding_result: bool | None = None
    error_category: str | None = None


class SimilarCaseResponse(BaseModel):
    ticket_id: str
    message: str
    intent: str
    response: str
    source: str
    score: float
    created_at: str | None = None
    metadata: dict[str, Any]


class TriageResponse(BaseModel):
    normalized_message: str
    intent: str
    intent_confidence: float = Field(ge=0, le=1)
    urgency: str
    escalate: bool
    escalation_reason: str
    suggested_response: str
    retrieved_cases: list[SimilarCaseResponse]
    grounded: bool
    grounding_score: float
    unsupported_claims: list[str] = Field(default_factory=list)
    confidence: float
    next_action: str
    provider_used: str
    model_used: str
    cached: bool
    fallback_used: bool
    degraded_mode: bool
    total_latency_ms: float = Field(ge=0)
    trace: list[TraceStepResponse]
