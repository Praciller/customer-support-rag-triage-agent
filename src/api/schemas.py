from typing import Any

from pydantic import BaseModel, Field, field_validator

from src.config.settings import get_settings


class TriageRequest(BaseModel):
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
    recreate: bool = False
    sample_size: int | None = Field(default=None, ge=1, le=50_000)


class TriageResponse(BaseModel):
    intent: str
    urgency: str
    escalate: bool
    escalation_reason: str
    suggested_response: str
    retrieved_cases: list[dict[str, Any]]
    grounded: bool
    grounding_score: float
    unsupported_claims: list[str] = Field(default_factory=list)
    confidence: float
    next_action: str
    provider_used: str
    model_used: str
    cached: bool
    degraded_mode: bool
    trace: list[dict[str, Any]]
