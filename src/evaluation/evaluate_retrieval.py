import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.api.services import build_services


def evaluate_retrieval(
    eval_path: Path = Path("data/eval/eval_set.csv"),
    top_k: int = 5,
) -> dict[str, Any]:
    services = build_services()
    frame = pd.read_csv(eval_path)
    precisions: list[float] = []
    recalls: list[float] = []
    for row in frame.to_dict(orient="records"):
        results = services.search(str(row["message"]), top_k, None)
        relevant = sum(item["intent"] == row["intent"] for item in results)
        precisions.append(relevant / top_k)
        recalls.append(1.0 if relevant else 0.0)
    return {
        "retrieval_precision_at_k": sum(precisions) / len(precisions),
        "retrieval_recall_at_k": sum(recalls) / len(recalls),
        "retrieval_examples": len(frame),
        "top_k": top_k,
    }


def main() -> None:
    print(json.dumps(evaluate_retrieval(), indent=2))


if __name__ == "__main__":
    main()
