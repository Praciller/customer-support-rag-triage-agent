import time

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from src.api.main import create_app
from src.api.schemas import TriageResponse
from src.config.settings import Settings
from src.policy import SAFE_ABSTENTION_RESPONSE


class FakeServices:
    def health(self) -> dict:
        return {"status": "ok", "qdrant": "ok"}

    def dataset_info(self) -> dict:
        return {"name": "PolyAI/banking77", "records": 1000}

    def provider_health(self) -> dict:
        return {"providers": ["mock"], "cache_enabled": True}

    def triage(self, message: str, top_k: int) -> dict:
        return {
            "normalized_message": message,
            "intent": "refund_request",
            "urgency": "high",
            "escalate": True,
            "escalation_reason": "Refund request",
            "suggested_response": SAFE_ABSTENTION_RESPONSE,
            "retrieved_cases": [],
            "similar_case_references": [],
            "policy_status": "no_approved_policy",
            "proposal_checks": [],
            "verified_proposals": [],
            "policy_references": [],
            "next_action": "manual_review",
            "provider_used": "mock",
            "model_used": "deterministic-small",
            "cached": False,
            "fallback_used": False,
            "degraded_mode": False,
            "total_latency_ms": 12.5,
            "trace": [],
        }

    def search(self, message: str, top_k: int, intent: str | None) -> list[dict]:
        return []

    def ingest(self, recreate: bool, sample_size: int | None) -> dict:
        return {"indexed": 10, "collection": "support_tickets"}

    def evaluation_results(self) -> dict:
        return {"intent_accuracy": 0.9}


def test_api_validates_triage_input_and_returns_metadata() -> None:
    client = TestClient(create_app(services=FakeServices()))

    invalid = client.post("/triage", json={"message": " ", "top_k": 5})
    valid = client.post("/triage", json={"message": "refund please", "top_k": 5})

    assert invalid.status_code == 422
    assert valid.status_code == 200
    payload = valid.json()
    assert payload["provider_used"] == "mock"
    assert payload["policy_status"] == "no_approved_policy"
    assert payload["proposal_checks"] == []
    assert "grounded" not in payload
    assert "grounding_score" not in payload
    assert "confidence" not in payload


def test_api_labels_similar_cases_separately_from_approved_policy() -> None:
    class EvidenceServices(FakeServices):
        def triage(self, message: str, top_k: int) -> dict:
            result = super().triage(message, top_k)
            result["retrieved_cases"] = [
                {
                    "ticket_id": "case-1",
                    "evidence_type": "similar_past_case",
                    "approved_policy": False,
                    "message": "Synthetic evidence.",
                    "intent": "refund_request",
                    "response": "Review the transaction reference.",
                    "source": "synthetic_test",
                    "score": 0.9,
                    "created_at": None,
                    "metadata": {},
                }
            ]
            result["similar_case_references"] = ["case-1"]
            return result

    response = TestClient(create_app(services=EvidenceServices())).post(
        "/triage", json={"message": "refund please", "top_k": 5}
    )

    assert response.status_code == 200
    assert response.json()["similar_case_references"] == ["case-1"]
    assert response.json()["retrieved_cases"][0]["approved_policy"] is False


def test_api_requires_each_allowed_proposal_to_have_its_own_passing_policy_check() -> None:
    payload = FakeServices().triage("refund please", top_k=5)
    payload.update(
        policy_status="verified",
        next_action="escalate_to_human",
        policy_references=["synthetic-test-policy"],
        proposal_checks=[
            {
                "proposal_id": "proposal-1",
                "status": "supported",
                "policy_references": ["synthetic-test-policy"],
                "verification_result": "passed",
                "verification_method": "synthetic_test_verifier",
            }
        ],
        verified_proposals=[
            {
                "proposal_id": "proposal-1",
                "text": "Synthetic test action.",
                "policy_references": ["synthetic-test-policy"],
                "verification_result": "passed",
                "verification_method": "synthetic_test_verifier",
            }
        ],
        suggested_response="Synthetic test action.",
    )
    assert TriageResponse.model_validate(payload).policy_status == "verified"

    payload["verified_proposals"].append(payload["verified_proposals"][0].copy())
    with pytest.raises(ValidationError, match="exactly one verified proposal"):
        TriageResponse.model_validate(payload)
    payload["verified_proposals"].pop()

    payload["proposal_checks"][0]["verification_result"] = "uncertain"
    with pytest.raises(ValidationError, match="passing approved policy check"):
        TriageResponse.model_validate(payload)


def test_api_rejects_a_similar_case_reference_as_policy_authority() -> None:
    payload = FakeServices().triage("refund please", top_k=5)
    payload.update(
        policy_status="verified",
        next_action="reply_to_customer",
        policy_references=["synthetic-test-policy"],
        proposal_checks=[
            {
                "proposal_id": "proposal-1",
                "status": "supported",
                "policy_references": ["synthetic-test-policy"],
                "verification_result": "passed",
                "verification_method": "synthetic_test_verifier",
            }
        ],
        verified_proposals=[
            {
                "proposal_id": "proposal-1",
                "text": "Synthetic test action.",
                "policy_references": ["synthetic-test-policy"],
                "verification_result": "passed",
                "verification_method": "synthetic_test_verifier",
            }
        ],
        suggested_response="Synthetic test action.",
        similar_case_references=["synthetic-test-policy"],
        retrieved_cases=[
            {
                "ticket_id": "synthetic-test-policy",
                "message": "Synthetic similar case.",
                "intent": "refund_request",
                "response": "Synthetic prior response.",
                "source": "synthetic_test",
                "score": 0.9,
                "created_at": None,
                "metadata": {},
            }
        ],
    )

    with pytest.raises(
        ValidationError, match="similar case references cannot be policy references"
    ):
        TriageResponse.model_validate(payload)


def test_api_exposes_required_read_endpoints() -> None:
    client = TestClient(create_app(services=FakeServices()))

    assert client.get("/health").status_code == 200
    assert client.get("/dataset-info").json()["name"] == "PolyAI/banking77"
    assert client.get("/provider-health").status_code == 200
    assert client.get("/eval/results").status_code == 200


def test_api_exposes_portfolio_brief_compatibility_endpoints() -> None:
    client = TestClient(create_app(services=FakeServices()))

    answer = client.post("/answer", json={"message": "refund please", "top_k": 5})
    evaluation = client.post("/evaluate")
    metrics = client.get("/metrics/sample")

    assert answer.status_code == 200
    answer_payload = answer.json()
    assert answer_payload["suggested_response"] == SAFE_ABSTENTION_RESPONSE
    assert answer_payload["policy_status"] == "no_approved_policy"
    assert answer_payload["next_action"] == "manual_review"
    assert "grounded" not in answer_payload
    assert "grounding_score" not in answer_payload
    assert "confidence" not in answer_payload
    assert evaluation.json()["intent_accuracy"] == 0.9
    assert metrics.json()["intent_accuracy"] == 0.9


def test_production_ingest_requires_admin_key() -> None:
    settings = Settings(
        _env_file=None,
        app_env="production",
        admin_api_key="test-key",
    )
    client = TestClient(create_app(services=FakeServices(), settings=settings))

    denied = client.post("/ingest", json={"recreate": True, "sample_size": 10})
    allowed = client.post(
        "/ingest",
        json={"recreate": True, "sample_size": 10},
        headers={"X-Admin-API-Key": "test-key"},
    )

    assert denied.status_code == 403
    assert allowed.status_code == 200
    assert allowed.json()["indexed"] == 10


def test_public_ingest_is_disabled_by_default() -> None:
    settings = Settings(_env_file=None, app_env="development", allow_public_ingest=False)
    client = TestClient(create_app(services=FakeServices(), settings=settings))

    response = client.post("/ingest", json={"sample_size": 10})

    assert response.status_code == 403
    assert response.json() == {"detail": "Ingestion is disabled"}


def test_triage_rate_limit_returns_retry_after() -> None:
    settings = Settings(
        _env_file=None,
        triage_rate_limit_requests=1,
        triage_rate_limit_window_seconds=60,
    )
    client = TestClient(create_app(services=FakeServices(), settings=settings))

    first = client.post("/triage", json={"message": "refund please", "top_k": 5})
    blocked = client.post("/triage", json={"message": "refund please", "top_k": 5})

    assert first.status_code == 200
    assert blocked.status_code == 429
    assert blocked.headers["Retry-After"] == "60"


def test_slow_triage_returns_controlled_timeout() -> None:
    class SlowServices(FakeServices):
        def triage(self, message: str, top_k: int) -> dict:
            time.sleep(0.05)
            return super().triage(message, top_k)

    settings = Settings(_env_file=None, request_timeout_seconds=0.01)
    client = TestClient(
        create_app(services=SlowServices(), settings=settings),
        raise_server_exceptions=False,
    )

    response = client.post("/triage", json={"message": "refund please", "top_k": 5})

    assert response.status_code == 504
    assert response.json() == {"detail": "Request timed out"}
