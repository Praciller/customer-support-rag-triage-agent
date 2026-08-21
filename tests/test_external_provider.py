import httpx
import pytest

from src.llm.base import LLMRequest
from src.llm.external import ExternalProvider


def test_external_provider_sends_neutral_contract_and_uses_bearer_key() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["authorization"] = request.headers.get("Authorization")
        captured["payload"] = request.read().decode("utf-8")
        return httpx.Response(200, json={"text": "grounded answer", "model": "remote-general"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = ExternalProvider(
        "https://inference.example/v1/generate",
        api_key="server-secret",
        client=client,
    )

    result = provider.generate(
        LLMRequest(
            task="generate_response",
            prompt="draft a reply",
            context="retrieved evidence",
            model="general",
            temperature=0.1,
            max_output_tokens=256,
        )
    )

    assert result.provider == "external"
    assert result.model == "remote-general"
    assert result.text == "grounded answer"
    assert captured["authorization"] == "Bearer server-secret"
    assert '"task":"generate_response"' in str(captured["payload"]).replace(" ", "")
    assert '"context":"retrievedevidence"' in str(captured["payload"]).replace(" ", "")


def test_external_provider_rejects_invalid_response_shape() -> None:
    client = httpx.Client(
        transport=httpx.MockTransport(lambda _: httpx.Response(200, json={"text": ""}))
    )
    provider = ExternalProvider("https://inference.example/v1/generate", client=client)

    with pytest.raises(ValueError, match="non-empty text"):
        provider.generate(LLMRequest(task="classify_intent", prompt="hello", model="general"))
