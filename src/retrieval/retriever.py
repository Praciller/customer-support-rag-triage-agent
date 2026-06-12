import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol

from qdrant_client import QdrantClient, models


class Embedder(Protocol):
    dimension: int

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class SentenceTransformerEmbedder:
    def __init__(
        self,
        model_name: str,
        device: str = "cpu",
        batch_size: int = 32,
        normalize: bool = True,
    ) -> None:
        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size
        self.normalize = normalize
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name, device=self.device)
        return self._model

    @property
    def dimension(self) -> int:
        dimension = self.model.get_embedding_dimension()
        if dimension is None:
            raise RuntimeError(f"Embedding dimension unavailable for {self.model_name}")
        return dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=self.normalize,
            show_progress_bar=False,
        )
        return vectors.tolist()


@dataclass(frozen=True)
class SupportDocument:
    ticket_id: str
    message: str
    intent: str
    response: str = ""
    source: str = "public_dataset"
    created_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchResult:
    ticket_id: str
    message: str
    intent: str
    response: str
    source: str
    score: float
    created_at: str | None
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class QdrantRetriever:
    def __init__(
        self,
        client: QdrantClient,
        collection_name: str,
        embedder: Embedder,
        min_score: float = 0.35,
    ) -> None:
        self.client = client
        self.collection_name = collection_name
        self.embedder = embedder
        self.min_score = min_score

    def index(self, documents: list[SupportDocument], recreate: bool = False) -> int:
        if recreate and self.client.collection_exists(self.collection_name):
            self.client.delete_collection(self.collection_name)
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.embedder.dimension,
                    distance=models.Distance.COSINE,
                ),
            )
        if not documents:
            return 0

        vectors = self.embedder.embed([document.message for document in documents])
        points = [
            models.PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_URL, document.ticket_id)),
                vector=vector,
                payload=asdict(document),
            )
            for document, vector in zip(documents, vectors, strict=True)
        ]
        self.client.upload_points(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )
        return len(points)

    def search(
        self,
        query: str,
        top_k: int,
        intent: str | None = None,
    ) -> list[SearchResult]:
        if not self.client.collection_exists(self.collection_name):
            return []
        query_filter = None
        if intent:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="intent",
                        match=models.MatchValue(value=intent),
                    )
                ]
            )
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=self.embedder.embed([query])[0],
            query_filter=query_filter,
            limit=top_k,
            score_threshold=self.min_score,
            with_payload=True,
        )
        return [self._to_result(point) for point in response.points]

    @staticmethod
    def _to_result(point: models.ScoredPoint) -> SearchResult:
        payload = point.payload or {}
        return SearchResult(
            ticket_id=str(payload.get("ticket_id", point.id)),
            message=str(payload.get("message", "")),
            intent=str(payload.get("intent", "other")),
            response=str(payload.get("response", "")),
            source=str(payload.get("source", "unknown")),
            score=float(point.score),
            created_at=payload.get("created_at"),
            metadata=dict(payload.get("metadata") or {}),
        )
