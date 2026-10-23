"""Regression guards for the public demo's JSON-only, text-only API boundary.

This is not a proof that transitive dependencies cannot decode images internally.
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import create_app
from src.config.settings import Settings


@pytest.fixture
def public_client() -> TestClient:
    settings = Settings(
        _env_file=None,
        app_env="production",
        demo_mode=True,
        allow_public_ingest=False,
        admin_api_key="",
    )
    # Invalid requests must be rejected before any service method is called.
    return TestClient(create_app(services=object(), settings=settings))


@pytest.mark.parametrize("endpoint", ["/triage", "/answer", "/search-similar"])
def test_text_endpoints_reject_unexpected_image_field(
    public_client: TestClient, endpoint: str
) -> None:
    response = public_client.post(
        endpoint,
        json={
            "message": "My card has not arrived",
            "top_k": 5,
            "image": {"filename": "sample.png", "content": "not-an-image"},
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize("endpoint", ["/triage", "/answer", "/search-similar"])
@pytest.mark.parametrize("content_type", ["image/png", "application/octet-stream"])
def test_text_endpoints_reject_binary_request_bodies(
    public_client: TestClient, endpoint: str, content_type: str
) -> None:
    response = public_client.post(
        endpoint,
        content=b"\x89PNG\r\n\x1a\nnot-a-real-image",
        headers={"Content-Type": content_type},
    )

    assert response.status_code == 422


def test_public_image_ingest_is_not_authorized(public_client: TestClient) -> None:
    response = public_client.post(
        "/ingest",
        json={"recreate": False, "sample_size": 10, "image": "sample.png"},
    )

    # The request does not reach ingestion: the schema rejects unknown fields.
    assert response.status_code == 422
