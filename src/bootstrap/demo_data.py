import json
import uuid
from pathlib import Path
from typing import Any

from src.retrieval.retriever import QdrantRetriever, SupportDocument


def bootstrap_demo_index(
    retriever: QdrantRetriever,
    fixture_path: Path,
) -> dict[str, Any]:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    records = fixture.get("records", [])
    documents = [_to_document(record) for record in records]
    expected_ids = [
        str(uuid.uuid5(uuid.NAMESPACE_URL, document.ticket_id)) for document in documents
    ]

    existing_ids: set[str] = set()
    if retriever.client.collection_exists(retriever.collection_name):
        points = retriever.client.retrieve(
            collection_name=retriever.collection_name,
            ids=expected_ids,
            with_payload=False,
            with_vectors=False,
        )
        existing_ids = {str(point.id) for point in points}

    missing = [
        document
        for document, point_id in zip(documents, expected_ids, strict=True)
        if point_id not in existing_ids
    ]
    indexed = retriever.index(missing)
    return {
        **fixture.get("dataset", {}),
        "fixture": str(fixture_path),
        "records": len(documents),
        "indexed": indexed,
        "ready": indexed + len(existing_ids) == len(documents),
    }


def _to_document(record: dict[str, Any]) -> SupportDocument:
    return SupportDocument(
        ticket_id=str(record["ticket_id"]),
        message=str(record["message"]),
        intent=str(record["intent"]),
        response=str(record.get("response", "")),
        source=str(record.get("source", "mteb/banking77")),
        created_at=record.get("created_at"),
        metadata=dict(record.get("metadata") or {}),
    )
