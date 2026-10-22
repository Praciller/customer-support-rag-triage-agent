import csv
import json
from pathlib import Path

import pytest

from src.evaluation.human_review import FIELDS, main, summarize_human_review


def _write_reviews(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _row(
    sample: str = "synthetic-1",
    reviewer: str = "reviewer-a",
    action: str = "pass",
    citation: str = "pass",
    policy: str = "pass",
) -> dict[str, str]:
    return {
        "sample_id": sample,
        "run_id": "synthetic-run",
        "source_sha": "ff8a105b90dc0d2d3574220d2703a3d16ca92530",
        "model_id": "mock-test",
        "reviewer_id": reviewer,
        "reviewed_at_utc": "2026-10-22T12:00:00Z",
        "action_appropriate": action,
        "citation_supported": citation,
        "policy_safe": policy,
    }


def test_human_review_counts_without_leaking_reviewer_ids(tmp_path: Path) -> None:
    source = tmp_path / "labels.csv"
    _write_reviews(
        source,
        [
            _row(),
            _row(reviewer="reviewer-b"),
            _row(sample="synthetic-2", policy="fail", citation="not_applicable"),
        ],
    )
    result = summarize_human_review(source, expected_samples=4)

    assert result["status_counts"] == {
        "pass": 1,
        "fail": 1,
        "uncertain": 0,
        "disputed": 0,
    }
    assert result["sample_count"] == 2
    assert result["annotation_count"] == 3
    assert result["reviewer_count"] == 2
    assert result["single_reviewer_sample_count"] == 1
    assert result["strict_pass_fraction"] == 0.5
    assert result["review_coverage"] == 0.5
    assert "reviewer-a" not in json.dumps(result)
    assert "synthetic-1" not in json.dumps(result)


def test_human_review_marks_disagreement_inconclusive(tmp_path: Path) -> None:
    source = tmp_path / "labels.csv"
    _write_reviews(source, [_row(), _row(reviewer="reviewer-b", citation="fail")])

    result = summarize_human_review(source)

    assert result["status_counts"]["disputed"] == 1
    assert result["dimension_counts"]["citation_supported"]["disputed"] == 1
    assert result["strict_pass_fraction"] == 0


@pytest.mark.parametrize(
    ("mutation", "error"),
    [
        ({"reviewed_at_utc": "2026-10-22T12:00:00"}, "UTC offset"),
        ({"reviewed_at_utc": "not-a-date"}, "timestamp"),
        ({"action_appropriate": "not_applicable"}, "action_appropriate"),
        ({"citation_supported": "yes"}, "citation_supported"),
        ({"source_sha": "NOT-A-SHA"}, "source_sha"),
        ({"policy_safe": "uncertain"}, None),
    ],
)
def test_review_validation(tmp_path: Path, mutation: dict[str, str], error: str | None) -> None:
    source = tmp_path / "labels.csv"
    row = {**_row(), **mutation}
    _write_reviews(source, [row])
    if error is None:
        assert summarize_human_review(source)["status_counts"]["uncertain"] == 1
    else:
        with pytest.raises(ValueError, match=error):
            summarize_human_review(source)


def test_review_rejects_duplicate_reviewer_pair_and_mixed_model(tmp_path: Path) -> None:
    source = tmp_path / "labels.csv"
    _write_reviews(source, [_row(), _row()])
    with pytest.raises(ValueError, match="duplicates"):
        summarize_human_review(source)

    _write_reviews(source, [_row(), {**_row(sample="synthetic-2"), "model_id": "other"}])
    with pytest.raises(ValueError, match="mixes evaluation"):
        summarize_human_review(source)


def test_review_rejects_missing_fields_empty_and_wrong_population(tmp_path: Path) -> None:
    source = tmp_path / "labels.csv"
    _write_reviews(source, [])
    with pytest.raises(ValueError, match="no human annotations"):
        summarize_human_review(source)

    _write_reviews(source, [_row(sample="synthetic-1"), _row(sample="synthetic-2")])
    with pytest.raises(ValueError, match="Expected sample count"):
        summarize_human_review(source, expected_samples=1)

    source.write_text("sample_id,run_id\nsynthetic-1,synthetic-run\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid review columns"):
        summarize_human_review(source)


def test_review_cli_outputs_aggregates_only(tmp_path: Path, capsys) -> None:
    source = tmp_path / "labels.csv"
    target = tmp_path / "summary.json"
    _write_reviews(source, [_row()])
    main(["--input", str(source), "--output", str(target)])
    assert json.loads(target.read_text())["status_counts"]["pass"] == 1
    assert "reviewer-a" not in capsys.readouterr().out
