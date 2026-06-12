import json
from pathlib import Path

from qdrant_client import QdrantClient

from src.config.settings import get_settings
from src.retrieval.retriever import (
    QdrantRetriever,
    SentenceTransformerEmbedder,
    SupportDocument,
)


def build_qdrant_index(
    input_path: Path = Path("data/processed/support_documents.jsonl"),
) -> dict[str, object]:
    settings = get_settings()
    records = [
        json.loads(line)
        for line in input_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    documents = [
        SupportDocument(
            ticket_id=item["id"],
            message=item["message"],
            intent=item["intent"],
            response=item["response"],
            source=item["source"],
            created_at=item["created_at"],
            metadata=item["metadata"],
        )
        for item in records
    ]
    retriever = QdrantRetriever(
        QdrantClient(url=settings.qdrant_url),
        settings.qdrant_collection,
        SentenceTransformerEmbedder(
            settings.embedding_model,
            device=settings.embedding_device,
            batch_size=settings.embedding_batch_size,
            normalize=settings.normalize_embeddings,
        ),
        min_score=settings.retrieval_min_score,
    )
    indexed = retriever.index(documents, recreate=settings.qdrant_recreate_collection)
    return {"indexed": indexed, "collection": settings.qdrant_collection}


def main() -> None:
    print(json.dumps(build_qdrant_index(), indent=2))


if __name__ == "__main__":
    main()
