import json
import time
from pathlib import Path
from typing import Any

import pandas as pd

from src.api.services import ApplicationServices, build_services
from src.config.settings import get_settings
from src.evaluation.evaluate_retrieval import evaluate_retrieval
from src.evaluation.metrics import classification_metrics, percentile


def evaluate_triage(
    eval_path: Path = Path("data/eval/eval_set.csv"),
    services: ApplicationServices | None = None,
) -> dict[str, Any]:
    settings = get_settings()
    services = services or build_services(settings)
    if services.bootstrap_status.get("status") == "pending":
        services.bootstrap_demo()
    frame = pd.read_csv(eval_path)
    expected_intents: list[str] = []
    predicted_intents: list[str] = []
    expected_urgencies: list[str] = []
    predicted_urgencies: list[str] = []
    results: list[dict[str, Any]] = []
    latencies: list[float] = []
    provider_usage: dict[str, int] = {}

    for row in frame.to_dict(orient="records"):
        started = time.perf_counter()
        result = services.triage(str(row["message"]), top_k=5)
        measured_latency = (time.perf_counter() - started) * 1000
        latency = float(result.get("total_latency_ms", measured_latency))
        latencies.append(latency)
        expected_intents.append(str(row["intent"]))
        predicted_intents.append(str(result["intent"]))
        expected_urgencies.append(str(row["urgency"]))
        predicted_urgencies.append(str(result["urgency"]))
        provider = str(result["provider_used"])
        provider_usage[provider] = provider_usage.get(provider, 0) + 1
        results.append(result)

    intent = classification_metrics(expected_intents, predicted_intents)
    urgency = classification_metrics(expected_urgencies, predicted_urgencies)
    retrieval = evaluate_retrieval(eval_path, services=services)
    sample_size = len(results)
    grounded_count = sum(bool(result["grounded"]) for result in results)
    unsupported_count = sum(bool(result["unsupported_claims"]) for result in results)
    degraded_count = sum(bool(result["degraded_mode"]) for result in results)
    fallback_count = sum(bool(result.get("fallback_used", False)) for result in results)
    cached_count = sum(bool(result["cached"]) for result in results)
    workflow_successes = sum(
        len(result.get("trace", [])) == 7
        and all(step.get("status") == "completed" for step in result["trace"])
        for result in results
    )
    mock_mode = services.provider_names == ["mock"]

    metrics = {
        "evaluation_mode": "deterministic_mock" if mock_mode else "real_provider",
        "dataset": {
            "name": "Banking77-derived deterministic evaluation fixture",
            "path": str(eval_path),
            "sample_size": sample_size,
        },
        "classification": {
            "intent": intent,
            "urgency": urgency,
        },
        "retrieval": retrieval,
        "grounding_workflow": {
            "grounded_response_rate": grounded_count / sample_size,
            "grounding_failure_rate": (sample_size - grounded_count) / sample_size,
            "unsupported_claim_rate": unsupported_count / sample_size,
            "degraded_mode_rate": degraded_count / sample_size,
            "fallback_rate": fallback_count / sample_size,
            "cache_hit_rate": cached_count / sample_size,
            "workflow_success_rate": workflow_successes / sample_size,
            "average_latency_ms": sum(latencies) / sample_size,
            "p50_latency_ms": percentile(latencies, 0.5),
            "p95_latency_ms": percentile(latencies, 0.95),
            "provider_usage": provider_usage,
        },
        "limitations": [
            "The fixture is small and deterministic; results are not a production SLA.",
            "Relevance uses mapped intent labels, not human-graded policy relevance.",
            "Mock generation measures workflow determinism, not real-model answer quality.",
        ],
        "retrieval_precision_at_k": retrieval["precision_at_k"],
        "retrieval_recall_at_k": retrieval["recall_at_k"],
        "retrieval_mrr": retrieval["mrr"],
        "retrieval_ndcg_at_k": retrieval["ndcg_at_k"],
        "retrieval_zero_result_rate": retrieval["zero_result"],
        "retrieval_average_score": retrieval["average_score"],
        "retrieval_latency_ms": retrieval["latency_ms"],
        "top_k": retrieval["top_k"],
        "intent_accuracy": intent["accuracy"],
        "intent_macro_f1": intent["macro_f1"],
        "urgency_accuracy": urgency["accuracy"],
        "urgency_macro_f1": urgency["macro_f1"],
        "groundedness_pass_rate": grounded_count / sample_size,
        "unsupported_claim_rate": unsupported_count / sample_size,
        "degraded_mode_rate": degraded_count / sample_size,
        "average_latency_ms": sum(latencies) / sample_size,
        "p50_latency_ms": percentile(latencies, 0.5),
        "p95_latency_ms": percentile(latencies, 0.95),
        "cache_hit_rate": cached_count / sample_size,
        "provider_fallback_rate": fallback_count / sample_size,
        "workflow_success_rate": workflow_successes / sample_size,
        "fallback_count": fallback_count,
        "provider_usage": provider_usage,
        "examples": sample_size,
        "mock_mode": mock_mode,
    }
    _write_artifacts(metrics, settings.eval_output_path)
    return metrics


def _write_artifacts(metrics: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    confusion_path = output_path.parent / "confusion_matrix.json"
    confusion_path.write_text(
        json.dumps(
            {
                "intent": {
                    "labels": metrics["classification"]["intent"]["labels"],
                    "matrix": metrics["classification"]["intent"]["confusion_matrix"],
                },
                "urgency": {
                    "labels": metrics["classification"]["urgency"]["labels"],
                    "matrix": metrics["classification"]["urgency"]["confusion_matrix"],
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    summary_path = output_path.parent / "summary.md"
    summary_path.write_text(_summary(metrics), encoding="utf-8")


def _summary(metrics: dict[str, Any]) -> str:
    def percent(value: float) -> str:
        return f"{value * 100:.1f}%"

    workflow = metrics["grounding_workflow"]
    return f"""# Deterministic Evaluation Summary

Mode: `{metrics['evaluation_mode']}`
Dataset: {metrics['dataset']['name']}
Sample size: {metrics['dataset']['sample_size']}

| Metric | Measured result |
| --- | ---: |
| Intent accuracy | {percent(metrics['intent_accuracy'])} |
| Intent macro F1 | {percent(metrics['intent_macro_f1'])} |
| Urgency accuracy | {percent(metrics['urgency_accuracy'])} |
| Precision@{metrics['top_k']} | {percent(metrics['retrieval_precision_at_k'])} |
| Recall@{metrics['top_k']} | {percent(metrics['retrieval_recall_at_k'])} |
| MRR | {metrics['retrieval_mrr']:.3f} |
| nDCG@{metrics['top_k']} | {metrics['retrieval_ndcg_at_k']:.3f} |
| Zero-result rate | {percent(metrics['retrieval_zero_result_rate'])} |
| Grounded response rate | {percent(metrics['groundedness_pass_rate'])} |
| Unsupported-claim rate | {percent(metrics['unsupported_claim_rate'])} |
| Workflow success rate | {percent(metrics['workflow_success_rate'])} |
| Fallback rate | {percent(metrics['provider_fallback_rate'])} |
| Cache hit rate | {percent(metrics['cache_hit_rate'])} |
| Average latency | {workflow['average_latency_ms']:.1f} ms |
| P50 / P95 latency | {workflow['p50_latency_ms']:.1f} / {workflow['p95_latency_ms']:.1f} ms |

## Method and limitations

- Retrieval relevance is defined by the expected mapped intent label.
- Generation and grounding use the deterministic mock provider; no external API is called.
- The small fixture is intended for reproducibility and regression detection, not an SLA.
"""


def main() -> None:
    print(json.dumps(evaluate_triage(), indent=2))


if __name__ == "__main__":
    main()
