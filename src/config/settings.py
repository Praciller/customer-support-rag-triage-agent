from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    app_name: str = "customer-support-rag-triage-agent"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_origin: str = "http://localhost:5173"
    cors_origins: str = ""
    admin_api_key: str = ""
    allow_public_ingest: bool = False
    demo_mode: bool = True
    bootstrap_demo_data: bool = True
    demo_fixture_path: Path = Path("data/demo/support_cases.json")
    log_level: str = "INFO"

    dataset_provider: str = "huggingface"
    hf_dataset_name: str = "mteb/banking77"
    hf_dataset_config: str = "default"
    hf_dataset_split: str = "train"
    dataset_sample_size: int = 1000
    csv_dataset_path: Path = Path("data/raw/support_dataset.csv")
    text_field: str = "message"
    intent_field: str = "intent"
    response_field: str = "response"
    source_field: str = "source"

    qdrant_mode: str = "auto"
    qdrant_path: Path = Path(".data/qdrant")
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "support_tickets"
    qdrant_vector_size: int = 384
    qdrant_distance: str = "Cosine"
    qdrant_recreate_collection: bool = False

    embedding_provider: str = "fastembed"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_device: str = "cpu"
    embedding_batch_size: int = 32
    normalize_embeddings: bool = True

    retrieval_top_k: int = 5
    retrieval_min_score: float = 0.35
    retrieval_max_context_chars: int = 4000

    llm_timeout_seconds: float = 30
    llm_max_retries: int = 0
    llm_retry_backoff_seconds: float = 0
    llm_temperature: float = 0.2
    llm_max_output_tokens: int = 512
    mock_llm_mode: bool = True

    llm_cache_enabled: bool = True
    llm_cache_backend: str = "sqlite"
    llm_cache_dir: Path = Path(".cache/llm")
    llm_cache_ttl_seconds: int = 86400

    max_message_chars: int = 2000
    max_top_k: int = 10
    max_ingest_batch_size: int = 1000
    enable_safe_fallback: bool = True
    return_agent_trace: bool = True
    request_timeout_seconds: float = 60

    triage_rate_limit_requests: int = 30
    triage_rate_limit_window_seconds: int = 3600
    search_rate_limit_requests: int = 60
    search_rate_limit_window_seconds: int = 3600
    ingest_rate_limit_requests: int = 5
    ingest_rate_limit_window_seconds: int = 3600

    eval_data_path: Path = Path("data/eval/eval_set.csv")
    eval_output_path: Path = Path("reports/evaluation/results.json")

    @property
    def cache_path(self) -> Path:
        return self.llm_cache_dir / "responses.sqlite3"

    @property
    def allowed_origins(self) -> list[str]:
        configured = self.cors_origins or self.frontend_origin
        return [origin.strip() for origin in configured.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
