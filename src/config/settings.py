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

    qdrant_url: str = "http://localhost:6333"
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "support_tickets"
    qdrant_vector_size: int = 384
    qdrant_distance: str = "Cosine"
    qdrant_recreate_collection: bool = False

    embedding_provider: str = "local"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_device: str = "cpu"
    embedding_batch_size: int = 32
    normalize_embeddings: bool = True

    retrieval_top_k: int = 5
    retrieval_min_score: float = 0.35
    retrieval_max_context_chars: int = 4000

    llm_provider_priority: str = "gemini,groq,cerebras"
    llm_default_provider: str = "gemini"
    llm_timeout_seconds: float = 30
    llm_max_retries: int = 1
    llm_retry_backoff_seconds: float = 2
    llm_temperature: float = 0.2
    llm_max_output_tokens: int = 512
    mock_llm_mode: bool = False

    gemini_api_key: str = ""
    gemini_default_model: str = "gemini-3.1-flash-lite"
    gemini_fallback_model: str = "gemini-3.5-flash"
    groq_api_key: str = ""
    groq_default_model: str = "llama-3.1-8b-instant"
    groq_generation_fallback_model: str = "openai/gpt-oss-120b"
    groq_quality_fallback_model: str = "llama-3.3-70b-versatile"
    cerebras_api_key: str = ""
    cerebras_default_model: str = "gpt-oss-120b"

    intent_model_provider: str = "groq"
    intent_model_name: str = "llama-3.1-8b-instant"
    urgency_model_provider: str = "groq"
    urgency_model_name: str = "llama-3.1-8b-instant"
    response_model_provider: str = "gemini"
    response_model_name: str = "gemini-3.1-flash-lite"
    grounding_model_provider: str = "gemini"
    grounding_model_name: str = "gemini-3.1-flash-lite"

    llm_cache_enabled: bool = True
    llm_cache_backend: str = "sqlite"
    llm_cache_dir: Path = Path(".cache/llm")
    llm_cache_ttl_seconds: int = 86400

    max_message_chars: int = 2000
    max_top_k: int = 10
    enable_safe_fallback: bool = True
    return_agent_trace: bool = True

    eval_data_path: Path = Path("data/eval/eval_set.csv")
    eval_output_path: Path = Path("reports/evaluation_metrics.json")

    @property
    def provider_priority(self) -> list[str]:
        return [item.strip() for item in self.llm_provider_priority.split(",") if item.strip()]

    @property
    def cache_path(self) -> Path:
        return self.llm_cache_dir / "responses.sqlite3"


@lru_cache
def get_settings() -> Settings:
    return Settings()
