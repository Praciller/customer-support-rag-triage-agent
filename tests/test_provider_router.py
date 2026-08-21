from collections import deque
from pathlib import Path

from src.llm.base import LLMRequest, ProviderResponse
from src.llm.cache import SQLiteLLMCache
from src.llm.router import ProviderRouter


class StubProvider:
    def __init__(self, name: str, responses: list[ProviderResponse | Exception]) -> None:
        self.name = name
        self.responses = deque(responses)
        self.calls = 0
        self.requests: list[LLMRequest] = []

    def generate(self, request: LLMRequest) -> ProviderResponse:
        self.calls += 1
        self.requests.append(request)
        response = self.responses.popleft()
        if isinstance(response, Exception):
            raise response
        return response


def test_router_retries_then_uses_next_provider(tmp_path: Path) -> None:
    primary = StubProvider("primary", [TimeoutError("slow"), TimeoutError("slow")])
    fallback = StubProvider(
        "fallback",
        [ProviderResponse(text='{"intent":"billing_issue"}', provider="fallback", model="small")],
    )
    router = ProviderRouter(
        providers={"primary": primary, "fallback": fallback},
        priority=["primary", "fallback"],
        cache=SQLiteLLMCache(tmp_path / "cache.sqlite3", ttl_seconds=60),
        max_retries=1,
        backoff_seconds=0,
    )

    result = router.generate(
        LLMRequest(task="classify_intent", prompt="charged twice", model="small"),
        preferred_provider="primary",
    )

    assert result.provider == "fallback"
    assert result.degraded_mode is False
    assert primary.calls == 2
    assert fallback.calls == 1


def test_router_checks_cache_before_provider(tmp_path: Path) -> None:
    local = StubProvider(
        "local",
        [ProviderResponse(text="first", provider="local", model="small")],
    )
    router = ProviderRouter(
        providers={"local": local},
        priority=["local"],
        cache=SQLiteLLMCache(tmp_path / "cache.sqlite3", ttl_seconds=60),
        max_retries=0,
        backoff_seconds=0,
    )
    request = LLMRequest(task="generate_response", prompt="hello", model="small")

    first = router.generate(request, preferred_provider="local")
    second = router.generate(request, preferred_provider="local")

    assert first.cached is False
    assert second.cached is True
    assert local.calls == 1


def test_router_returns_safe_fallback_when_all_providers_fail(tmp_path: Path) -> None:
    local = StubProvider("local", [RuntimeError("offline")])
    router = ProviderRouter(
        providers={"local": local},
        priority=["local"],
        cache=SQLiteLLMCache(tmp_path / "cache.sqlite3", ttl_seconds=60),
        max_retries=0,
        backoff_seconds=0,
    )

    result = router.generate(
        LLMRequest(task="generate_response", prompt="hello", model="small"),
        preferred_provider="local",
    )

    assert result.degraded_mode is True
    assert result.provider == "safe_fallback"
    assert "respond manually" in result.text


def test_router_preserves_task_model_and_uses_task_specific_fallback(tmp_path: Path) -> None:
    primary = StubProvider("primary", [RuntimeError("offline")])
    fallback = StubProvider(
        "fallback",
        [ProviderResponse(text="ok", provider="fallback", model="fallback-generation")],
    )
    router = ProviderRouter(
        providers={"primary": primary, "fallback": fallback},
        priority=["primary", "fallback"],
        cache=SQLiteLLMCache(tmp_path / "cache.sqlite3", ttl_seconds=60),
        max_retries=0,
        backoff_seconds=0,
        provider_models={"primary": "primary-default", "fallback": "fallback-default"},
        task_provider_models={
            "generate_response": {"fallback": "fallback-generation"},
        },
    )

    result = router.generate(
        LLMRequest(
            task="generate_response",
            prompt="draft",
            model="primary-task-model",
        ),
        preferred_provider="primary",
    )

    assert primary.requests[0].model == "primary-task-model"
    assert fallback.requests[0].model == "fallback-generation"
    assert result.model == "fallback-generation"
