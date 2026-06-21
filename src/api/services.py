import json
from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient

from src.bootstrap.demo_data import bootstrap_demo_index
from src.config.settings import Settings, get_settings
from src.data.clean_dataset import clean_record
from src.data.load_dataset import load_records, write_raw_dataset
from src.graph.workflow import TriageWorkflow
from src.llm.cache import SQLiteLLMCache
from src.llm.http_clients import GeminiProvider, OpenAICompatibleProvider
from src.llm.mock import MockProvider
from src.llm.router import ProviderRouter
from src.retrieval.retriever import (
    FastEmbedder,
    HashingEmbedder,
    QdrantRetriever,
    SentenceTransformerEmbedder,
    SupportDocument,
)


class ApplicationServices:
    def __init__(
        self,
        settings: Settings,
        retriever: QdrantRetriever,
        workflow: TriageWorkflow,
        provider_names: list[str],
    ) -> None:
        self.settings = settings
        self.retriever = retriever
        self.workflow = workflow
        self.provider_names = provider_names
        self.bootstrap_status: dict[str, Any] = {
            "ready": False,
            "status": "pending",
            "records": 0,
            "indexed": 0,
        }

    def bootstrap_demo(self) -> dict[str, Any]:
        if not self.settings.demo_mode or not self.settings.bootstrap_demo_data:
            self.bootstrap_status = {
                "ready": self.retriever.client.collection_exists(
                    self.settings.qdrant_collection
                ),
                "status": "disabled",
                "records": 0,
                "indexed": 0,
            }
            return self.bootstrap_status
        try:
            self.bootstrap_status = {
                **bootstrap_demo_index(
                    self.retriever,
                    self.settings.demo_fixture_path,
                ),
                "status": "ready",
            }
        except Exception as error:
            self.bootstrap_status = {
                "ready": False,
                "status": "error",
                "records": 0,
                "indexed": 0,
                "error_category": type(error).__name__,
            }
        return self.bootstrap_status

    def health(self) -> dict[str, Any]:
        try:
            self.retriever.client.get_collections()
            qdrant = "ok"
        except Exception:
            qdrant = "unavailable"
        ready = qdrant == "ok" and self.bootstrap_status.get("ready", False)
        return {
            "status": "ok",
            "liveness": "ok",
            "readiness": "ready" if ready else "not_ready",
            "qdrant": qdrant,
            "app": self.settings.app_name,
            "demo_mode": self.settings.demo_mode,
            "index": self.bootstrap_status,
        }

    def dataset_info(self) -> dict[str, Any]:
        if self.settings.demo_mode and self.settings.demo_fixture_path.exists():
            return self._demo_dataset_info()
        for path in (
            Path("data/processed/dataset_metadata.json"),
            Path("data/raw/dataset_metadata.json"),
        ):
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        if self.settings.demo_fixture_path.exists():
            return self._demo_dataset_info()
        return {
            "name": self.settings.hf_dataset_name,
            "records": 0,
            "split": self.settings.hf_dataset_split,
            "status": "not_ingested",
        }

    def _demo_dataset_info(self) -> dict[str, Any]:
        fixture = json.loads(self.settings.demo_fixture_path.read_text(encoding="utf-8"))
        records = fixture.get("records", [])
        intents: dict[str, int] = {}
        for record in records:
            intent = str(record.get("intent", "other"))
            intents[intent] = intents.get(intent, 0) + 1
        return {
            **fixture.get("dataset", {}),
            "records": len(records),
            "intents": intents,
            "status": "demo_fixture",
            "index_ready": self.bootstrap_status.get("ready", False),
        }

    def provider_health(self) -> dict[str, Any]:
        routes = {
            "intent": {
                "provider": self.settings.intent_model_provider,
                "model": self.settings.intent_model_name,
            },
            "urgency": {
                "provider": self.settings.urgency_model_provider,
                "model": self.settings.urgency_model_name,
            },
            "response": {
                "provider": self.settings.response_model_provider,
                "model": self.settings.response_model_name,
            },
            "grounding": {
                "provider": self.settings.grounding_model_provider,
                "model": self.settings.grounding_model_name,
            },
        }
        return {
            "providers": self.provider_names,
            "primary_provider": self.settings.llm_default_provider,
            "fallback_order": self.settings.provider_priority,
            "routes": routes,
            "cache_enabled": self.settings.llm_cache_enabled,
            "demo_mode": self.settings.demo_mode,
            "mock_mode": "mock" in self.provider_names,
            "live_provider_calls_enabled": "mock" not in self.provider_names,
            "embedding_model": self.settings.embedding_model,
            "embedding_provider": self.settings.embedding_provider,
            "qdrant_collection": self.settings.qdrant_collection,
            "qdrant_mode": self.settings.qdrant_mode,
            "ingestion_enabled": self.settings.allow_public_ingest,
        }

    def triage(self, message: str, top_k: int) -> dict[str, Any]:
        return self.workflow.run(message=message, top_k=top_k)

    def search(
        self,
        message: str,
        top_k: int,
        intent: str | None,
    ) -> list[dict[str, Any]]:
        return [
            result.to_dict()
            for result in self.retriever.search(message, top_k=top_k, intent=intent)
        ]

    def ingest(self, recreate: bool, sample_size: int | None) -> dict[str, Any]:
        metadata = write_raw_dataset(self.settings, sample_size)
        records = [clean_record(record) for record in load_records(self.settings, sample_size)]
        documents = [
            SupportDocument(
                ticket_id=record["id"],
                message=record["message"],
                intent=record["intent"],
                response=record["response"],
                source=record["source"],
                created_at=record["created_at"],
                metadata=record["metadata"],
            )
            for record in records
            if record["message"]
        ]
        indexed = self.retriever.index(documents, recreate=recreate)
        return {
            "indexed": indexed,
            "collection": self.settings.qdrant_collection,
            "dataset": metadata,
        }

    def evaluation_results(self) -> dict[str, Any]:
        path = self.settings.eval_output_path
        if not path.exists():
            legacy_path = Path("reports/evaluation_metrics.json")
            path = legacy_path if legacy_path.exists() else path
        if not path.exists():
            return {"status": "not_evaluated"}
        return json.loads(path.read_text(encoding="utf-8"))


def build_services(settings: Settings | None = None) -> ApplicationServices:
    settings = settings or get_settings()
    client = build_qdrant_client(settings)
    embedder = build_embedder(settings)
    retriever = QdrantRetriever(
        client,
        settings.qdrant_collection,
        embedder,
        min_score=settings.retrieval_min_score,
    )
    use_mock = settings.demo_mode or settings.mock_llm_mode
    providers = _build_providers(settings, use_mock=use_mock)
    cache = SQLiteLLMCache(
        settings.cache_path,
        ttl_seconds=settings.llm_cache_ttl_seconds,
        enabled=settings.llm_cache_enabled,
    )
    router = ProviderRouter(
        providers,
        priority=["mock"] if use_mock else settings.provider_priority,
        cache=cache,
        max_retries=settings.llm_max_retries,
        backoff_seconds=settings.llm_retry_backoff_seconds,
        provider_models={
            "mock": "mock-small",
            "gemini": settings.gemini_default_model,
            "groq": settings.groq_default_model,
            "cerebras": settings.cerebras_default_model,
        },
        task_provider_models={
            "classify_intent": {
                "gemini": settings.gemini_fallback_model,
                "groq": settings.groq_default_model,
            },
            "detect_urgency": {
                "gemini": settings.gemini_fallback_model,
                "groq": settings.groq_default_model,
            },
            "generate_response": {
                "gemini": settings.gemini_fallback_model,
                "groq": settings.groq_generation_fallback_model,
            },
            "grounding_check": {
                "gemini": settings.gemini_fallback_model,
                "groq": settings.groq_default_model,
            },
        },
        safe_fallback_enabled=settings.enable_safe_fallback,
    )
    routes = (
        {
            "classify_intent": ("mock", "mock-small"),
            "detect_urgency": ("mock", "mock-small"),
            "generate_response": ("mock", "mock-small"),
            "grounding_check": ("mock", "mock-small"),
        }
        if use_mock
        else {
            "classify_intent": (
                settings.intent_model_provider,
                settings.intent_model_name,
            ),
            "detect_urgency": (
                settings.urgency_model_provider,
                settings.urgency_model_name,
            ),
            "generate_response": (
                settings.response_model_provider,
                settings.response_model_name,
            ),
            "grounding_check": (
                settings.grounding_model_provider,
                settings.grounding_model_name,
            ),
        }
    )
    workflow = TriageWorkflow(
        router,
        retriever,
        task_routes=routes,
        temperature=settings.llm_temperature,
        max_output_tokens=settings.llm_max_output_tokens,
        max_context_chars=settings.retrieval_max_context_chars,
    )
    return ApplicationServices(settings, retriever, workflow, list(providers))


def build_qdrant_client(settings: Settings) -> QdrantClient:
    if settings.qdrant_mode.lower() == "memory":
        return QdrantClient(":memory:")
    use_server = settings.qdrant_mode.lower() == "server" or (
        settings.qdrant_mode.lower() == "auto" and bool(settings.qdrant_url)
    )
    if use_server:
        return QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key or None,
            timeout=settings.llm_timeout_seconds,
        )
    settings.qdrant_path.mkdir(parents=True, exist_ok=True)
    return QdrantClient(path=str(settings.qdrant_path))


def build_embedder(
    settings: Settings,
) -> FastEmbedder | HashingEmbedder | SentenceTransformerEmbedder:
    provider = settings.embedding_provider.lower()
    if provider == "fastembed":
        return FastEmbedder(
            settings.embedding_model,
            dimension=settings.qdrant_vector_size,
            batch_size=settings.embedding_batch_size,
        )
    if provider == "hashing":
        return HashingEmbedder(dimension=settings.qdrant_vector_size)
    return SentenceTransformerEmbedder(
        settings.embedding_model,
        device=settings.embedding_device,
        batch_size=settings.embedding_batch_size,
        normalize=settings.normalize_embeddings,
    )


def _build_providers(settings: Settings, use_mock: bool = False) -> dict[str, Any]:
    if use_mock:
        return {"mock": MockProvider()}

    providers: dict[str, Any] = {}
    if settings.gemini_api_key:
        providers["gemini"] = GeminiProvider(
            settings.gemini_api_key,
            settings.llm_timeout_seconds,
        )
    if settings.groq_api_key:
        providers["groq"] = OpenAICompatibleProvider(
            "groq",
            settings.groq_api_key,
            "https://api.groq.com/openai/v1",
            settings.llm_timeout_seconds,
        )
    if settings.cerebras_api_key:
        providers["cerebras"] = OpenAICompatibleProvider(
            "cerebras",
            settings.cerebras_api_key,
            "https://api.cerebras.ai/v1",
            settings.llm_timeout_seconds,
        )
    if providers:
        return providers
    return {"mock": MockProvider()}
