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
    gemini = StubProvider("gemini", [TimeoutError("slow"), TimeoutError("slow")])
    groq = StubProvider(
        "groq",
        [ProviderResponse(text='{"intent":"billing_issue"}', provider="groq", model="small")],
    )
    router = ProviderRouter(
        providers={"gemini": gemini, "groq": groq},
        priority=["gemini", "groq"],
        cache=SQLiteLLMCache(tmp_path / "cache.sqlite3", ttl_seconds=60),
        max_retries=1,
        backoff_seconds=0,
    )

    result = router.generate(
        LLMRequest(task="classify_intent", prompt="charged twice", model="small"),
        preferred_provider="gemini",
    )

    assert result.provider == "groq"
    assert result.degraded_mode is False
    assert gemini.calls == 2
    assert groq.calls == 1


def test_router_checks_cache_before_provider(tmp_path: Path) -> None:
    gemini = StubProvider(
        "gemini",
        [ProviderResponse(text="first", provider="gemini", model="small")],
    )
    router = ProviderRouter(
        providers={"gemini": gemini},
        priority=["gemini"],
        cache=SQLiteLLMCache(tmp_path / "cache.sqlite3", ttl_seconds=60),
        max_retries=0,
        backoff_seconds=0,
    )
    request = LLMRequest(task="generate_response", prompt="hello", model="small")

    first = router.generate(request, preferred_provider="gemini")
    second = router.generate(request, preferred_provider="gemini")

    assert first.cached is False
    assert second.cached is True
    assert gemini.calls == 1


def test_router_returns_safe_fallback_when_all_providers_fail(tmp_path: Path) -> None:
    gemini = StubProvider("gemini", [RuntimeError("offline")])
    router = ProviderRouter(
        providers={"gemini": gemini},
        priority=["gemini"],
        cache=SQLiteLLMCache(tmp_path / "cache.sqlite3", ttl_seconds=60),
        max_retries=0,
        backoff_seconds=0,
    )

    result = router.generate(
        LLMRequest(task="generate_response", prompt="hello", model="small"),
        preferred_provider="gemini",
    )

    assert result.degraded_mode is True
    assert result.provider == "safe_fallback"
    assert "respond manually" in result.text


def test_router_preserves_task_model_and_uses_task_specific_fallback(tmp_path: Path) -> None:
    gemini = StubProvider("gemini", [RuntimeError("offline")])
    groq = StubProvider(
        "groq",
        [ProviderResponse(text="ok", provider="groq", model="groq-generation")],
    )
    router = ProviderRouter(
        providers={"gemini": gemini, "groq": groq},
        priority=["gemini", "groq"],
        cache=SQLiteLLMCache(tmp_path / "cache.sqlite3", ttl_seconds=60),
        max_retries=0,
        backoff_seconds=0,
        provider_models={"gemini": "gemini-default", "groq": "groq-default"},
        task_provider_models={
            "generate_response": {"groq": "groq-generation"},
        },
    )

    result = router.generate(
        LLMRequest(
            task="generate_response",
            prompt="draft",
            model="gemini-task-model",
        ),
        preferred_provider="gemini",
    )

    assert gemini.requests[0].model == "gemini-task-model"
    assert groq.requests[0].model == "groq-generation"
    assert result.model == "groq-generation"
