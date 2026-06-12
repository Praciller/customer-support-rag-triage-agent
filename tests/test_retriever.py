from qdrant_client import QdrantClient

from src.retrieval.retriever import FastEmbedder, QdrantRetriever, SupportDocument


class KeywordEmbedder:
    dimension = 3

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        for text in texts:
            lowered = text.lower()
            vectors.append(
                [
                    float("refund" in lowered),
                    float("card" in lowered),
                    float("password" in lowered),
                ]
            )
        return vectors


class FakeFastEmbedModel:
    def passage_embed(self, texts: list[str], **kwargs):
        assert kwargs == {"batch_size": 4, "parallel": None}
        for text in texts:
            yield FakeVector([float(len(text)), 1.0])

    def query_embed(self, text: str, **kwargs):
        assert kwargs == {"batch_size": 1, "parallel": None}
        yield FakeVector([float(len(text)), 2.0])


class FakeVector(list):
    def tolist(self) -> list[float]:
        return list(self)


def test_fastembedder_uses_passage_and_query_encoders() -> None:
    embedder = FastEmbedder("BAAI/bge-small-en-v1.5", dimension=2, batch_size=4)
    embedder._model = FakeFastEmbedModel()

    assert embedder.embed_documents(["card"]) == [[4.0, 1.0]]
    assert embedder.embed_query("refund") == [6.0, 2.0]


def test_retriever_returns_scores_and_applies_intent_filter() -> None:
    retriever = QdrantRetriever(
        client=QdrantClient(":memory:"),
        collection_name="tickets",
        embedder=KeywordEmbedder(),
        min_score=0.1,
    )
    retriever.index(
        [
            SupportDocument(
                ticket_id="1",
                message="I need a refund",
                intent="refund_request",
                response="Review the refund request.",
                source="test",
            ),
            SupportDocument(
                ticket_id="2",
                message="My card is blocked",
                intent="account_access",
                response="Verify the card status.",
                source="test",
            ),
        ],
        recreate=True,
    )

    results = retriever.search("refund please", top_k=5, intent="refund_request")

    assert len(results) == 1
    assert results[0].ticket_id == "1"
    assert results[0].score > 0.9
    assert results[0].intent == "refund_request"
