import time

from fastapi.testclient import TestClient

from src.api.main import create_app
from src.config.settings import Settings


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
            "intent_confidence": 0.91,
            "urgency": "high",
            "escalate": True,
            "escalation_reason": "Refund request",
            "suggested_response": "Please share the transaction ID.",
            "retrieved_cases": [],
            "grounded": True,
            "grounding_score": 0.9,
            "unsupported_claims": [],
            "confidence": 0.9,
            "next_action": "request_more_info",
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
    assert valid.json()["provider_used"] == "mock"


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
    assert answer.json()["suggested_response"] == "Please share the transaction ID."
    assert evaluation.json()["intent_accuracy"] == 0.9
    assert metrics.json()["intent_accuracy"] == 0.9


def test_production_ingest_requires_admin_key() -> None:
    settings = Settings(
        _env_file=None,
        app_env="production",
        admin_api_key="deploy-secret",
    )
    client = TestClient(create_app(services=FakeServices(), settings=settings))

    denied = client.post("/ingest", json={"recreate": True, "sample_size": 10})
    allowed = client.post(
        "/ingest",
        json={"recreate": True, "sample_size": 10},
        headers={"X-Admin-API-Key": "deploy-secret"},
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
