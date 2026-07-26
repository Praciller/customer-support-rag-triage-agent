from pathlib import Path

from fastapi.testclient import TestClient

from src.api.main import create_app
from src.api.services import ApplicationServices, build_services
from src.config.settings import Settings


def test_key_free_demo_bootstraps_and_runs_full_workflow(tmp_path: Path) -> None:
    settings = Settings(
        _env_file=None,
        demo_mode=True,
        mock_llm_mode=True,
        qdrant_mode="memory",
        embedding_provider="hashing",
        retrieval_min_score=0,
        llm_cache_dir=tmp_path / "cache",
    )
    services = build_services(settings)

    with TestClient(create_app(services=services, settings=settings)) as client:
        ready = client.get("/ready")
        triage = client.post(
            "/triage",
            json={"message": "My card has not arrived and I travel tomorrow", "top_k": 5},
        )

    assert ready.status_code == 200
    assert ready.json()["index"]["records"] == 27
    assert triage.status_code == 200
    payload = triage.json()
    assert payload["provider_used"] == "mock"
    assert payload["retrieved_cases"]
    assert len(payload["trace"]) == 7
    assert payload["next_action"] == "ask_for_order_id"


def test_demo_dataset_info_ignores_stale_full_dataset_metadata(
    tmp_path: Path,
    monkeypatch,
) -> None:
    metadata = tmp_path / "data" / "processed" / "dataset_metadata.json"
    metadata.parent.mkdir(parents=True)
    metadata.write_text('{"records": 1000}', encoding="utf-8")
    fixture = Path(__file__).parents[1] / "data" / "demo" / "support_cases.json"
    monkeypatch.chdir(tmp_path)
    settings = Settings(
        _env_file=None,
        demo_mode=True,
        qdrant_mode="memory",
        embedding_provider="hashing",
        demo_fixture_path=fixture,
        llm_cache_dir=tmp_path / "cache",
    )
    services = build_services(settings)
    services.bootstrap_demo()

    assert services.dataset_info()["records"] == 27
    assert services.dataset_info()["status"] == "demo_fixture"


def test_demo_provider_health_reports_active_mock_routes(tmp_path: Path) -> None:
    settings = Settings(
        _env_file=None,
        demo_mode=True,
        mock_llm_mode=True,
        qdrant_mode="memory",
        embedding_provider="hashing",
        llm_cache_dir=tmp_path / "cache",
    )
    status = build_services(settings).provider_health()

    assert status["primary_provider"] == "mock"
    assert status["fallback_order"] == ["mock"]
    assert {route["provider"] for route in status["routes"].values()} == {"mock"}
    assert status["live_provider_calls_enabled"] is False


def test_readiness_requires_reachable_qdrant() -> None:
    class OfflineClient:
        def get_collections(self) -> None:
            raise ConnectionError

    class OfflineRetriever:
        client = OfflineClient()

    services = ApplicationServices(
        Settings(_env_file=None),
        OfflineRetriever(),
        workflow=None,
        provider_names=["mock"],
    )
    services.bootstrap_status["ready"] = True

    assert services.health()["readiness"] == "not_ready"
