import hashlib
import json
import time
from collections.abc import Callable

from src.llm.base import LLMProvider, LLMRequest, ProviderResponse
from src.llm.cache import SQLiteLLMCache

SAFE_FALLBACK_RESPONSE = (
    "I could not generate a reliable response right now. "
    "Please review the retrieved similar cases and respond manually."
)


class ProviderRouter:
    def __init__(
        self,
        providers: dict[str, LLMProvider],
        priority: list[str],
        cache: SQLiteLLMCache,
        max_retries: int,
        backoff_seconds: float,
        provider_models: dict[str, str] | None = None,
        task_provider_models: dict[str, dict[str, str]] | None = None,
        safe_fallback_enabled: bool = True,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.providers = providers
        self.priority = priority
        self.cache = cache
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.provider_models = provider_models or {}
        self.task_provider_models = task_provider_models or {}
        self.safe_fallback_enabled = safe_fallback_enabled
        self.sleep = sleep

    def generate(
        self,
        request: LLMRequest,
        preferred_provider: str | None = None,
    ) -> ProviderResponse:
        provider_order = self._provider_order(preferred_provider)
        for provider_index, provider_name in enumerate(provider_order):
            provider = self.providers.get(provider_name)
            if provider is None:
                continue
            model = self._model_for(provider_name, preferred_provider, request)
            provider_request = request.with_model(model)
            cache_key = self._cache_key(provider_name, provider_request)
            cached = self.cache.get(cache_key)
            if cached is not None:
                return ProviderResponse(
                    text=cached["text"],
                    provider=cached["provider"],
                    model=cached["model"],
                    cached=True,
                    degraded_mode=False,
                    fallback_used=provider_index > 0,
                    latency_ms=0,
                )

            for attempt in range(self.max_retries + 1):
                try:
                    started = time.perf_counter()
                    response = provider.generate(provider_request)
                    latency_ms = (time.perf_counter() - started) * 1000
                    result = ProviderResponse(
                        text=response.text,
                        provider=response.provider,
                        model=response.model,
                        cached=False,
                        degraded_mode=False,
                        fallback_used=provider_index > 0,
                        latency_ms=latency_ms,
                    )
                    self.cache.set(
                        cache_key,
                        {"text": result.text, "provider": result.provider, "model": result.model},
                    )
                    return result
                except Exception:
                    if attempt < self.max_retries:
                        self.sleep(self.backoff_seconds * (2**attempt))

        if self.safe_fallback_enabled:
            return ProviderResponse(
                text=SAFE_FALLBACK_RESPONSE,
                provider="safe_fallback",
                model="none",
                degraded_mode=True,
                fallback_used=True,
            )
        raise RuntimeError("All configured LLM providers failed")

    def _provider_order(self, preferred_provider: str | None) -> list[str]:
        ordered = [preferred_provider, *self.priority]
        return list(dict.fromkeys(item for item in ordered if item))

    def _model_for(
        self,
        provider_name: str,
        preferred_provider: str | None,
        request: LLMRequest,
    ) -> str:
        if provider_name == preferred_provider:
            return request.model
        return self.task_provider_models.get(request.task, {}).get(
            provider_name,
            self.provider_models.get(provider_name, request.model),
        )

    @staticmethod
    def _cache_key(provider: str, request: LLMRequest) -> str:
        payload = json.dumps(
            {
                "provider": provider,
                "model": request.model,
                "task": request.task,
                "workflow_instructions": request.workflow_instructions,
                "user_ticket": request.user_ticket,
                "candidate_response": request.candidate_response,
                "evidence": [item.to_provider_payload() for item in request.evidence],
                "temperature": request.temperature,
                "max_output_tokens": request.max_output_tokens,
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
