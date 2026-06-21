import json
from pathlib import Path

from qdrant_client import QdrantClient

from src.bootstrap.demo_data import bootstrap_demo_index
from src.retrieval.retriever import QdrantRetriever


class KeywordEmbedder:
    dimension = 3

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [
            [
                float("card" in text.lower()),
                float("transfer" in text.lower()),
                float("fraud" in text.lower()),
            ]
            for text in texts
        ]


def test_demo_bootstrap_indexes_missing_fixture_once(tmp_path: Path) -> None:
    fixture = tmp_path / "support_cases.json"
    fixture.write_text(
        json.dumps(
            {
                "dataset": {
                    "name": "mteb/banking77",
                    "license": "CC BY 4.0",
                    "revision": "demo-fixture-v1",
                },
                "records": [
                    {
                        "ticket_id": "demo-card",
                        "message": "Where is the card I ordered?",
                        "intent": "delivery_issue",
                        "metadata": {"original_intent": "card_arrival"},
                    },
                    {
                        "ticket_id": "demo-transfer",
                        "message": "Why is my transfer pending?",
                        "intent": "billing_issue",
                        "metadata": {"original_intent": "pending_transfer"},
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    retriever = QdrantRetriever(
        QdrantClient(":memory:"),
        "demo_cases",
        KeywordEmbedder(),
        min_score=0,
    )

    first = bootstrap_demo_index(retriever, fixture)
    second = bootstrap_demo_index(retriever, fixture)

    assert first["indexed"] == 2
    assert second["indexed"] == 0
    assert second["ready"] is True
    assert second["records"] == 2
