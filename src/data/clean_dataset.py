import json
import re
from pathlib import Path
from typing import Any

import pandas as pd


def clean_record(record: dict[str, Any]) -> dict[str, Any]:
    metadata = record.get("metadata") or {}
    if isinstance(metadata, str):
        metadata = json.loads(metadata) if metadata.strip() else {}
    created_at = record.get("created_at")
    if pd.isna(created_at):
        created_at = None
    return {
        "id": str(record.get("id", "")),
        "message": re.sub(r"\s+", " ", str(record.get("message", ""))).strip(),
        "intent": str(record.get("intent", "other")).strip() or "other",
        "response": (
            ""
            if record.get("response") is None or pd.isna(record.get("response"))
            else re.sub(r"\s+", " ", str(record["response"])).strip()
        ),
        "source": str(record.get("source", "unknown")),
        "created_at": created_at,
        "metadata": metadata,
    }


def clean_dataset(
    input_path: Path = Path("data/raw/support_dataset.csv"),
    output_path: Path = Path("data/processed/support_tickets.csv"),
) -> dict[str, Any]:
    frame = pd.read_csv(input_path)
    records = [clean_record(row) for row in frame.to_dict(orient="records")]
    records = [record for record in records if record["message"]]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_frame = pd.DataFrame(records)
    output_frame["metadata"] = output_frame["metadata"].map(json.dumps)
    output_frame.to_csv(output_path, index=False)
    source_metadata_path = input_path.parent / "dataset_metadata.json"
    source_metadata = (
        json.loads(source_metadata_path.read_text(encoding="utf-8"))
        if source_metadata_path.exists()
        else {}
    )
    metadata = {
        **source_metadata,
        "records": len(records),
        "intents": output_frame["intent"].value_counts().to_dict(),
        "processed_path": str(output_path),
    }
    Path("data/processed/dataset_metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    print(json.dumps(clean_dataset(), indent=2))


if __name__ == "__main__":
    main()
