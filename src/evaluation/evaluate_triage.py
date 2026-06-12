import json
import time
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score

from src.api.services import build_services
from src.config.settings import get_settings
from src.evaluation.evaluate_retrieval import evaluate_retrieval


def evaluate_triage(
    eval_path: Path = Path("data/eval/eval_set.csv"),
) -> dict[str, Any]:
    settings = get_settings()
    services = build_services(settings)
    frame = pd.read_csv(eval_path)
    expected_intents: list[str] = []
    predicted_intents: list[str] = []
    expected_urgencies: list[str] = []
    predicted_urgencies: list[str] = []
    grounded: list[bool] = []
    cached: list[bool] = []
    degraded: list[bool] = []
    latencies: list[float] = []
    provider_usage: dict[str, int] = {}

    for row in frame.to_dict(orient="records"):
        started = time.perf_counter()
        result = services.triage(str(row["message"]), top_k=5)
        latencies.append((time.perf_counter() - started) * 1000)
        expected_intents.append(str(row["intent"]))
        predicted_intents.append(result["intent"])
        expected_urgencies.append(str(row["urgency"]))
        predicted_urgencies.append(result["urgency"])
        grounded.append(bool(result["grounded"]))
        cached.append(bool(result["cached"]))
        degraded.append(bool(result["degraded_mode"]))
        provider = str(result["provider_used"])
        provider_usage[provider] = provider_usage.get(provider, 0) + 1

    retrieval = evaluate_retrieval(eval_path)
    metrics = {
        **retrieval,
        "intent_accuracy": accuracy_score(expected_intents, predicted_intents),
        "intent_macro_f1": f1_score(
            expected_intents,
            predicted_intents,
            average="macro",
            zero_division=0,
        ),
        "urgency_accuracy": accuracy_score(expected_urgencies, predicted_urgencies),
        "groundedness_pass_rate": sum(grounded) / len(grounded),
        "average_latency_ms": sum(latencies) / len(latencies),
        "cache_hit_rate": sum(cached) / len(cached),
        "provider_fallback_rate": sum(degraded) / len(degraded),
        "fallback_count": sum(degraded),
        "provider_usage": provider_usage,
        "examples": len(frame),
        "mock_mode": settings.mock_llm_mode,
    }
    settings.eval_output_path.parent.mkdir(parents=True, exist_ok=True)
    settings.eval_output_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    _write_report(metrics, Path("reports/evaluation_report.md"))
    return metrics


def _write_report(metrics: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    def percent(value: float) -> str:
        return f"{value * 100:.1f}%"

    content = f"""# Evaluation Report

Offline evaluation uses the real Banking77-derived evaluation set and local retrieval.
LLM-dependent steps run in deterministic mock mode; no paid provider calls are made.

| Metric | Result |
| --- | ---: |
| Retrieval precision@{metrics['top_k']} | {percent(metrics['retrieval_precision_at_k'])} |
| Retrieval recall@{metrics['top_k']} | {percent(metrics['retrieval_recall_at_k'])} |
| Intent accuracy | {percent(metrics['intent_accuracy'])} |
| Intent macro F1 | {percent(metrics['intent_macro_f1'])} |
| Urgency accuracy | {percent(metrics['urgency_accuracy'])} |
| Groundedness pass rate | {percent(metrics['groundedness_pass_rate'])} |
| Average latency | {metrics['average_latency_ms']:.1f} ms |
| Cache hit rate | {percent(metrics['cache_hit_rate'])} |
| Provider fallback rate | {percent(metrics['provider_fallback_rate'])} |

These results measure this repository's deterministic baseline, not a production SLA.
"""
    path.write_text(content, encoding="utf-8")


def main() -> None:
    print(json.dumps(evaluate_triage(), indent=2))


if __name__ == "__main__":
    main()
