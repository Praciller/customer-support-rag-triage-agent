import math
from typing import Any

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)


def classification_metrics(
    expected: list[str],
    predicted: list[str],
) -> dict[str, Any]:
    labels = sorted(set(expected) | set(predicted))
    precision, recall, f1, support = precision_recall_fscore_support(
        expected,
        predicted,
        labels=labels,
        zero_division=0,
    )
    return {
        "accuracy": float(accuracy_score(expected, predicted)),
        "macro_f1": float(
            f1_score(expected, predicted, labels=labels, average="macro", zero_division=0)
        ),
        "labels": labels,
        "per_class": {
            label: {
                "precision": float(precision[index]),
                "recall": float(recall[index]),
                "f1": float(f1[index]),
                "support": int(support[index]),
            }
            for index, label in enumerate(labels)
        },
        "confusion_matrix": confusion_matrix(
            expected,
            predicted,
            labels=labels,
        ).tolist(),
    }


def retrieval_metrics(
    retrieved_labels: list[str],
    relevant_label: str,
    top_k: int,
    scores: list[float],
    latency_ms: float,
) -> dict[str, float]:
    labels = retrieved_labels[:top_k]
    relevance = [label == relevant_label for label in labels]
    relevant_count = sum(relevance)
    reciprocal_rank = next(
        (1 / (index + 1) for index, relevant in enumerate(relevance) if relevant),
        0.0,
    )
    dcg = sum(
        1 / math.log2(index + 2)
        for index, relevant in enumerate(relevance)
        if relevant
    )
    ideal_dcg = sum(
        1 / math.log2(index + 2) for index in range(min(relevant_count, top_k))
    )
    return {
        "precision_at_k": relevant_count / top_k,
        "recall_at_k": 1.0 if relevant_count else 0.0,
        "mrr": reciprocal_rank,
        "ndcg_at_k": dcg / ideal_dcg if ideal_dcg else 0.0,
        "zero_result": float(not labels),
        "average_score": sum(scores[:top_k]) / len(scores[:top_k]) if scores else 0.0,
        "latency_ms": latency_ms,
    }


def percentile(values: list[float], percentile_value: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = (len(ordered) - 1) * percentile_value
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (rank - lower)
