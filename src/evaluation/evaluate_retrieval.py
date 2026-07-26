import json
import time
from pathlib import Path
from typing import Any

import pandas as pd

from src.api.services import ApplicationServices, build_services
from src.evaluation.metrics import retrieval_metrics


def evaluate_retrieval(
    eval_path: Path = Path("data/eval/eval_set.csv"),
    top_k: int = 5,
    services: ApplicationServices | None = None,
) -> dict[str, Any]:
    services = services or build_services()
    if services.bootstrap_status.get("status") == "pending":
        services.bootstrap_demo()
    frame = pd.read_csv(eval_path)
    dataset_info = services.dataset_info()
    relevant_totals = dataset_info.get("intents", {})
    examples: list[dict[str, Any]] = []

    for row in frame.to_dict(orient="records"):
        started = time.perf_counter()
        results = services.search(str(row["message"]), top_k, None)
        latency_ms = (time.perf_counter() - started) * 1000
        metrics = retrieval_metrics(
            retrieved_labels=[str(item["intent"]) for item in results],
            relevant_label=str(row["intent"]),
            top_k=top_k,
            scores=[float(item["score"]) for item in results],
            latency_ms=latency_ms,
            relevant_total=int(relevant_totals.get(str(row["intent"]), 0)) or None,
        )
        examples.append(
            {
                "message": str(row["message"]),
                "expected_intent": str(row["intent"]),
                "retrieved_ids": [str(item["ticket_id"]) for item in results],
                **metrics,
            }
        )

    metric_names = (
        "precision_at_k",
        "recall_at_k",
        "mrr",
        "ndcg_at_k",
        "zero_result",
        "average_score",
        "latency_ms",
    )
    aggregate = {
        metric: sum(example[metric] for example in examples) / len(examples)
        for metric in metric_names
    }
    return {
        **aggregate,
        "top_k": top_k,
        "sample_size": len(examples),
        "examples": examples,
    }


def main() -> None:
    print(json.dumps(evaluate_retrieval(), indent=2))


if __name__ == "__main__":
    main()
