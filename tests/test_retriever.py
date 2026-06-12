from qdrant_client import QdrantClient

from src.retrieval.retriever import QdrantRetriever, SupportDocument


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
