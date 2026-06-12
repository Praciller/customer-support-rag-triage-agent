import json

from src.llm.base import LLMRequest
from src.llm.mock import MockProvider


def test_mock_classifier_ignores_instruction_labels() -> None:
    request = LLMRequest(
        task="classify_intent",
        model="mock-small",
        prompt=(
            "Allowed labels: delivery_issue, refund_request, billing_issue.\n"
            "Message:\nI forgot my password and cannot sign in"
        ),
    )

    payload = json.loads(MockProvider().generate(request).text)

    assert payload["intent"] == "account_access"


def test_mock_urgency_ignores_instruction_risk_terms() -> None:
    request = LLMRequest(
        task="detect_urgency",
        model="mock-small",
        prompt="Escalate fraud or urgent cases.\nMessage:\nHow do I update my profile?",
    )

    payload = json.loads(MockProvider().generate(request).text)

    assert payload["urgency"] == "low"


def test_mock_classifier_prioritizes_risk_and_failure_context() -> None:
    provider = MockProvider()
    cases = {
        "The mobile payment feature is not working": "technical_issue",
        "This transaction is not mine and my card may be stolen": "complaint",
        "Which countries support this card": "product_question",
    }

    for message, expected in cases.items():
        request = LLMRequest(
            task="classify_intent",
            model="mock-small",
            prompt=f"Allowed labels include billing_issue.\nMessage:\n{message}",
        )
        assert json.loads(provider.generate(request).text)["intent"] == expected
