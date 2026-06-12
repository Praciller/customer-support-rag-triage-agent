import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.data.clean_dataset import clean_record


def build_documents(
    input_path: Path = Path("data/processed/support_tickets.csv"),
    output_path: Path = Path("data/processed/support_documents.jsonl"),
) -> dict[str, Any]:
    frame = pd.read_csv(input_path)
    records = [clean_record(row) for row in frame.to_dict(orient="records")]
    records = [record for record in records if record["message"]]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")
    return {"documents": len(records), "path": str(output_path)}


def main() -> None:
    print(json.dumps(build_documents(), indent=2))


if __name__ == "__main__":
    main()
