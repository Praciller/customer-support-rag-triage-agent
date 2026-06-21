import asyncio
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api.rate_limit import InMemoryRateLimiter
from src.api.schemas import (
    IngestRequest,
    SearchRequest,
    SimilarCaseResponse,
    TriageRequest,
    TriageResponse,
)
from src.api.services import ApplicationServices, build_services
from src.config.settings import get_settings


def create_app(
    services: ApplicationServices | Any | None = None,
    settings: Any | None = None,
    rate_limiter: InMemoryRateLimiter | None = None,
) -> FastAPI:
    settings = settings or get_settings()
    service = services or build_services(settings)
    limiter = rate_limiter or InMemoryRateLimiter()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if hasattr(service, "bootstrap_demo"):
            service.bootstrap_demo()
        yield

    app = FastAPI(
        title="Customer Support RAG Triage Agent",
        version="1.0.0",
        description="Retrieval-grounded support triage workflow with provider fallback.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def enforce_request_timeout(request: Request, call_next):
        try:
            return await asyncio.wait_for(
                call_next(request),
                timeout=settings.request_timeout_seconds,
            )
        except TimeoutError:
            return JSONResponse(status_code=504, content={"detail": "Request timed out"})

    @app.exception_handler(Exception)
    async def controlled_error_response(_: Request, __: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"detail": "Request could not be completed"},
        )

    def rate_limit(limit: int, window_seconds: int):
        def enforce(request: Request) -> None:
            client_host = request.client.host if request.client else "unknown"
            decision = limiter.check(
                f"{request.url.path}:{client_host}",
                limit=limit,
                window_seconds=window_seconds,
            )
            if not decision.allowed:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded",
                    headers={"Retry-After": str(decision.retry_after_seconds)},
                )

        return enforce

    triage_limit = rate_limit(
        settings.triage_rate_limit_requests,
        settings.triage_rate_limit_window_seconds,
    )
    search_limit = rate_limit(
        settings.search_rate_limit_requests,
        settings.search_rate_limit_window_seconds,
    )
    ingest_limit = rate_limit(
        settings.ingest_rate_limit_requests,
        settings.ingest_rate_limit_window_seconds,
    )

    @app.get("/health")
    def health() -> dict[str, Any]:
        return service.health()

    @app.get("/ready")
    def readiness() -> dict[str, Any]:
        status = service.health()
        if status.get("readiness") != "ready":
            raise HTTPException(status_code=503, detail="Service is not ready")
        return status

    @app.get("/dataset-info")
    def dataset_info() -> dict[str, Any]:
        return service.dataset_info()

    @app.get("/provider-health")
    def provider_health() -> dict[str, Any]:
        return service.provider_health()

    @app.post("/ingest", dependencies=[Depends(ingest_limit)])
    def ingest(
        request: IngestRequest,
        x_admin_api_key: Annotated[str | None, Header()] = None,
    ) -> dict[str, Any]:
        valid_key = bool(settings.admin_api_key) and bool(x_admin_api_key)
        if valid_key:
            valid_key = secrets.compare_digest(x_admin_api_key, settings.admin_api_key)
        local_public_ingest = (
            settings.app_env.lower() in {"development", "test"}
            and settings.allow_public_ingest
        )
        if not valid_key and not local_public_ingest:
            detail = (
                "Admin API key required"
                if settings.admin_api_key
                else "Ingestion is disabled"
            )
            raise HTTPException(status_code=403, detail=detail)
        return service.ingest(request.recreate, request.sample_size)

    @app.post(
        "/triage",
        response_model=TriageResponse,
        dependencies=[Depends(triage_limit)],
    )
    def triage(request: TriageRequest) -> dict[str, Any]:
        return service.triage(request.message, request.top_k)

    @app.post(
        "/search-similar",
        response_model=list[SimilarCaseResponse],
        dependencies=[Depends(search_limit)],
    )
    def search_similar(request: SearchRequest) -> list[dict[str, Any]]:
        return service.search(request.message, request.top_k, request.intent)

    @app.get("/eval/results")
    def evaluation_results() -> dict[str, Any]:
        return service.evaluation_results()

    frontend_dist = Path("frontend/dist")
    if frontend_dist.is_dir():
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

    return app


app = create_app()
