from dataclasses import dataclass, replace
from typing import Protocol


@dataclass(frozen=True)
class LLMRequest:
    task: str
    prompt: str
    model: str
    context: str = ""
    temperature: float = 0.2
    max_output_tokens: int = 512

    def with_model(self, model: str) -> "LLMRequest":
        return replace(self, model=model)


@dataclass(frozen=True)
class ProviderResponse:
    text: str
    provider: str
    model: str
    cached: bool = False
    degraded_mode: bool = False
    fallback_used: bool = False
    latency_ms: float = 0


class LLMProvider(Protocol):
    name: str

    def generate(self, request: LLMRequest) -> ProviderResponse: ...
