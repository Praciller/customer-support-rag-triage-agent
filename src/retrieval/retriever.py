import hashlib
import math
import re
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


class FastEmbedder:
    def __init__(
        self,
        model_name: str,
        dimension: int = 384,
        batch_size: int = 32,
    ) -> None:
        self.model_name = model_name
        self.dimension = dimension
        self.batch_size = batch_size
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from fastembed import TextEmbedding

            self._model = TextEmbedding(model_name=self.model_name)
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self.embed_documents(texts)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [
            vector.tolist()
            for vector in self.model.passage_embed(
                texts,
                batch_size=self.batch_size,
                parallel=None,
            )
        ]

    def embed_query(self, text: str) -> list[float]:
        return next(
            self.model.query_embed(
                text,
                batch_size=1,
                parallel=None,
            )
        ).tolist()


class HashingEmbedder:
    """Deterministic dependency-free embedder for tests and bounded CI smoke checks."""

    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.embed(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._embed_one(text)

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        for token in re.findall(r"[a-z0-9]+", text.lower()):
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            index = int.from_bytes(digest, "big") % self.dimension
            vector[index] += 1.0
        norm = math.sqrt(sum(value * value for value in vector))
        return [value / norm for value in vector] if norm else vector


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

        embed_documents = getattr(self.embedder, "embed_documents", self.embedder.embed)
        vectors = embed_documents([document.message for document in documents])
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
        embed_query = getattr(self.embedder, "embed_query", None)
        query_vector = embed_query(query) if embed_query else self.embedder.embed([query])[0]
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
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
