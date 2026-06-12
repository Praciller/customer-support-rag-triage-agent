import json
from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient

from src.config.settings import Settings, get_settings
from src.data.clean_dataset import clean_record
from src.data.load_dataset import load_records, write_raw_dataset
from src.graph.workflow import TriageWorkflow
from src.llm.cache import SQLiteLLMCache
from src.llm.http_clients import GeminiProvider, OpenAICompatibleProvider
from src.llm.mock import MockProvider
from src.llm.router import ProviderRouter
from src.retrieval.retriever import (
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

    def health(self) -> dict[str, Any]:
        try:
            self.retriever.client.get_collections()
            qdrant = "ok"
        except Exception:
            qdrant = "unavailable"
        return {
            "status": "ok" if qdrant == "ok" else "degraded",
            "qdrant": qdrant,
            "app": self.settings.app_name,
        }

    def dataset_info(self) -> dict[str, Any]:
        for path in (
            Path("data/processed/dataset_metadata.json"),
            Path("data/raw/dataset_metadata.json"),
        ):
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        return {
            "name": self.settings.hf_dataset_name,
            "records": 0,
            "split": self.settings.hf_dataset_split,
            "status": "not_ingested",
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
            "embedding_model": self.settings.embedding_model,
            "qdrant_collection": self.settings.qdrant_collection,
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
            return {"status": "not_evaluated"}
        return json.loads(path.read_text(encoding="utf-8"))


def build_services(settings: Settings | None = None) -> ApplicationServices:
    settings = settings or get_settings()
    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key or None,
        timeout=settings.llm_timeout_seconds,
    )
    embedder = SentenceTransformerEmbedder(
        settings.embedding_model,
        device=settings.embedding_device,
        batch_size=settings.embedding_batch_size,
        normalize=settings.normalize_embeddings,
    )
    retriever = QdrantRetriever(
        client,
        settings.qdrant_collection,
        embedder,
        min_score=settings.retrieval_min_score,
    )
    providers = _build_providers(settings)
    cache = SQLiteLLMCache(
        settings.cache_path,
        ttl_seconds=settings.llm_cache_ttl_seconds,
        enabled=settings.llm_cache_enabled,
    )
    router = ProviderRouter(
        providers,
        priority=["mock"] if settings.mock_llm_mode else settings.provider_priority,
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
        if settings.mock_llm_mode
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


def _build_providers(settings: Settings) -> dict[str, Any]:
    if settings.mock_llm_mode:
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
