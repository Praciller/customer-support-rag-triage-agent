from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RetrievedEvidence:
    """A retrieved record that is data-only input to an inference request."""

    reference_id: str
    message: str
    intent: str
    response: str = ""
    source: str = "unknown"
    score: float = 0.0
    created_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_provider_payload(self) -> dict[str, Any]:
        return {
            "reference_id": self.reference_id,
            "content": self.message,
            "intent": self.intent,
            "prior_response": self.response,
            "source": self.source,
            "score": self.score,
            "created_at": self.created_at,
            "metadata": dict(self.metadata),
        }

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "ticket_id": self.reference_id,
            "message": self.message,
            "intent": self.intent,
            "response": self.response,
            "source": self.source,
            "score": self.score,
            "created_at": self.created_at,
            "metadata": dict(self.metadata),
        }
