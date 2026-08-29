import json

import httpx
import pytest

from src.evidence import RetrievedEvidence
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
        api_key="k",
        client=client,
    )

    result = provider.generate(
        LLMRequest(
            task="generate_response",
            workflow_instructions="Draft a concise reply.",
            user_ticket="My payment needs review.",
            model="general",
            evidence=(
                RetrievedEvidence(
                    reference_id="case-1",
                    message="retrieved evidence",
                    intent="billing_issue",
                    response="Ask for the transaction reference.",
                    source="synthetic_test",
                    score=0.9,
                ),
            ),
            temperature=0.1,
            max_output_tokens=256,
        )
    )

    assert result.provider == "external"
    assert result.model == "remote-general"
    assert result.text == "grounded answer"
    assert captured["authorization"] == "Bearer k"
    payload = json.loads(str(captured["payload"]))
    assert payload["task"] == "generate_response"
    assert payload["workflow_instructions"] == "Draft a concise reply."
    assert payload["user_ticket"] == "My payment needs review."
    assert payload["evidence"][0]["reference_id"] == "case-1"
    assert payload["evidence"][0]["content"] == "retrieved evidence"
    assert "system" not in payload
    assert "developer" not in payload


def test_external_provider_rejects_invalid_response_shape() -> None:
    client = httpx.Client(
        transport=httpx.MockTransport(lambda _: httpx.Response(200, json={"text": ""}))
    )
    provider = ExternalProvider("https://inference.example/v1/generate", client=client)

    with pytest.raises(ValueError, match="non-empty text"):
        provider.generate(
            LLMRequest(
                task="classify_intent",
                workflow_instructions="Classify the ticket.",
                user_ticket="hello",
                model="general",
            )
        )
