import pytest

from src.evaluation.evaluate_triage import _evaluation_mode
from src.evaluation.metrics import classification_metrics, retrieval_metrics
from src.evaluation.validation import load_evaluation_frame


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


@pytest.mark.parametrize(
    ("contents", "error"),
    [
        ("message,intent,urgency\\n", "no tickets"),
        ("message,intent\\nA ticket,other\\n", "Missing evaluation columns"),
        ("message,intent,urgency\\n,other,low\\n", "empty values"),
        (
            "message,intent,urgency\\nMy issue,other,low\\n MY ISSUE ,other,low\\n",
            "duplicate ticket",
        ),
    ],
)
def test_evaluation_rejects_malformed_fixtures(tmp_path, contents: str, error: str) -> None:
    path = tmp_path / "eval.csv"
    path.write_text(contents.replace("\\n", "\n"), encoding="utf-8")
    with pytest.raises(ValueError, match=error):
        load_evaluation_frame(path)


def test_evaluation_accepts_unique_labeled_tickets(tmp_path) -> None:
    path = tmp_path / "eval.csv"
    path.write_text(
        "message,intent,urgency\nA delivery issue,delivery_issue,medium\n"
        "A billing issue,billing_issue,low\n",
        encoding="utf-8",
    )
    frame = load_evaluation_frame(path)
    assert len(frame) == 2


@pytest.mark.parametrize(
    ("providers", "fallback", "degraded", "expected"),
    [
        (["mock"] * 4, False, False, "deterministic_mock"),
        (["external"] * 4, False, False, "real_provider"),
        (["mock"] * 4, True, True, "mixed_or_degraded"),
        (["external", "mock", "external", "external"], True, True, "mixed_or_degraded"),
    ],
)
def test_evaluation_mode_tracks_executed_provider_calls(
    providers: list[str], fallback: bool, degraded: bool, expected: str
) -> None:
    result = {
        "trace": [{"component": "llm_router", "provider": name} for name in providers],
        "fallback_used": fallback,
        "degraded_mode": degraded,
    }
    mode, observed = _evaluation_mode([result])
    assert mode == expected
    assert observed == sorted(set(providers))
