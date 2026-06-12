from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.schemas import IngestRequest, SearchRequest, TriageRequest, TriageResponse
from src.api.services import ApplicationServices, build_services
from src.config.settings import get_settings


def create_app(services: ApplicationServices | Any | None = None) -> FastAPI:
    settings = get_settings()
    service = services or build_services(settings)
    app = FastAPI(
        title="Customer Support RAG Triage Agent",
        version="1.0.0",
        description="Retrieval-grounded support triage workflow with provider fallback.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, Any]:
        return service.health()

    @app.get("/dataset-info")
    def dataset_info() -> dict[str, Any]:
        return service.dataset_info()

    @app.get("/provider-health")
    def provider_health() -> dict[str, Any]:
        return service.provider_health()

    @app.post("/ingest")
    def ingest(request: IngestRequest) -> dict[str, Any]:
        return service.ingest(request.recreate, request.sample_size)

    @app.post("/triage", response_model=TriageResponse)
    def triage(request: TriageRequest) -> dict[str, Any]:
        return service.triage(request.message, request.top_k)

    @app.post("/search-similar")
    def search_similar(request: SearchRequest) -> list[dict[str, Any]]:
        return service.search(request.message, request.top_k, request.intent)

    @app.get("/eval/results")
    def evaluation_results() -> dict[str, Any]:
        return service.evaluation_results()

    return app


app = create_app()
