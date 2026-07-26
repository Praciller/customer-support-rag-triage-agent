from src.evaluation.metrics import classification_metrics, retrieval_metrics


def test_evaluation_metrics_include_per_class_and_rank_quality() -> None:
    classification = classification_metrics(
        expected=["billing_issue", "billing_issue", "complaint"],
        predicted=["billing_issue", "complaint", "complaint"],
    )
    retrieval = retrieval_metrics(
        retrieved_labels=["billing_issue", "complaint", "billing_issue"],
        relevant_label="billing_issue",
        top_k=3,
        scores=[0.9, 0.7, 0.6],
        latency_ms=12.5,
        relevant_total=3,
    )

    assert classification["accuracy"] == 2 / 3
    assert classification["per_class"]["billing_issue"]["recall"] == 0.5
    assert classification["confusion_matrix"] == [[1, 1], [0, 1]]
    assert retrieval["precision_at_k"] == 2 / 3
    assert retrieval["recall_at_k"] == 2 / 3
    assert retrieval["mrr"] == 1.0
    assert 0 < retrieval["ndcg_at_k"] < 1
