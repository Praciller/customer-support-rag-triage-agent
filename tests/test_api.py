from fastapi.testclient import TestClient

from src.api.main import create_app


class FakeServices:
    def health(self) -> dict:
        return {"status": "ok", "qdrant": "ok"}

    def dataset_info(self) -> dict:
        return {"name": "PolyAI/banking77", "records": 1000}

    def provider_health(self) -> dict:
        return {"providers": ["gemini", "groq", "cerebras"], "cache_enabled": True}

    def triage(self, message: str, top_k: int) -> dict:
        return {
            "intent": "refund_request",
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
            "model_used": "mock-small",
            "cached": False,
            "degraded_mode": False,
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
