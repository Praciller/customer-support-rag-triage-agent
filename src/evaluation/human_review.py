"""Aggregate human judgments offline without publishing tickets or reviewer identities."""

import argparse
import csv
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

FIELDS = (
    "sample_id",
    "run_id",
    "source_sha",
    "model_id",
    "reviewer_id",
    "reviewed_at_utc",
    "action_appropriate",
    "citation_supported",
    "policy_safe",
)
DIMENSIONS = ("action_appropriate", "citation_supported", "policy_safe")
JUDGMENTS = {"pass", "fail", "uncertain"}
CITATION_JUDGMENTS = JUDGMENTS | {"not_applicable"}
STATUSES = ("pass", "fail", "uncertain", "disputed")


def summarize_human_review(path: Path, expected_samples: int | None = None) -> dict[str, Any]:
    """Report only aggregate review statistics; never copy ticket or reviewer fields."""
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        headers = reader.fieldnames
        if headers is None or len(headers) != len(set(headers)):
            raise ValueError("Review CSV has missing or duplicate headers")
        missing = set(FIELDS) - set(headers)
        unexpected = set(headers) - set(FIELDS)
        if missing or unexpected:
            raise ValueError(
                "Invalid review columns; "
                f"missing={sorted(missing)}, unexpected={sorted(unexpected)}"
            )
        rows = list(reader)

    if not rows:
        raise ValueError("Review CSV has no human annotations")

    samples: dict[str, list[dict[str, str]]] = defaultdict(list)
    reviewer_ids: set[str] = set()
    annotation_keys: set[tuple[str, str]] = set()
    provenance: tuple[str, str, str] | None = None

    for row_number, row in enumerate(rows, start=2):
        if None in row or any(value is None or not value.strip() for value in row.values()):
            raise ValueError(f"Row {row_number} has missing or empty fields")

        data = {key: value.strip() for key, value in row.items()}
        batch = (data["run_id"], data["source_sha"], data["model_id"])
        if not re.fullmatch(r"[0-9a-fA-F]{7,40}", data["source_sha"]):
            raise ValueError(f"Row {row_number} has invalid source_sha")
        if provenance is None:
            provenance = batch
        elif batch != provenance:
            raise ValueError(f"Row {row_number} mixes evaluation runs or model revisions")

        key = (data["sample_id"], data["reviewer_id"])
        if key in annotation_keys:
            raise ValueError(f"Row {row_number} duplicates a sample/reviewer pair")
        annotation_keys.add(key)
        reviewer_ids.add(data["reviewer_id"])

        try:
            reviewed = datetime.fromisoformat(data["reviewed_at_utc"].replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError(f"Row {row_number} has invalid review timestamp") from error
        if reviewed.utcoffset() != timedelta(0):
            raise ValueError(f"Row {row_number} timestamp must include a UTC offset")

        for dimension in DIMENSIONS:
            allowed = CITATION_JUDGMENTS if dimension == "citation_supported" else JUDGMENTS
            if data[dimension] not in allowed:
                raise ValueError(f"Row {row_number} has invalid {dimension} judgment")
        samples[data["sample_id"]].append(data)

    if expected_samples is not None and (expected_samples < 1 or expected_samples < len(samples)):
        raise ValueError("Expected sample count must cover all reviewed samples")

    counts = dict.fromkeys(STATUSES, 0)
    dimension_counts = {dim: dict.fromkeys((*STATUSES, "not_applicable"), 0) for dim in DIMENSIONS}
    single_reviewer_samples = 0

    for annotations in samples.values():
        if len(annotations) == 1:
            single_reviewer_samples += 1
        resolved: dict[str, str] = {}
        for dimension in DIMENSIONS:
            judgments = {entry[dimension] for entry in annotations}
            resolved[dimension] = next(iter(judgments)) if len(judgments) == 1 else "disputed"
            dimension_counts[dimension][resolved[dimension]] += 1

        if "disputed" in resolved.values():
            status = "disputed"
        elif "fail" in resolved.values():
            status = "fail"
        elif "uncertain" in resolved.values():
            status = "uncertain"
        else:
            status = "pass"
        counts[status] += 1

    sample_count = len(samples)
    assert provenance is not None
    result: dict[str, Any] = {
        "evaluation_mode": "offline_human_review",
        "run_id": provenance[0],
        "source_sha": provenance[1],
        "model_id": provenance[2],
        "sample_count": sample_count,
        "annotation_count": len(rows),
        "reviewer_count": len(reviewer_ids),
        "single_reviewer_sample_count": single_reviewer_samples,
        "status_counts": counts,
        "dimension_counts": dimension_counts,
        "strict_pass_fraction": counts["pass"] / sample_count,
        "limitations": [
            "Labels and provenance are reviewer-supplied and have not been independently verified.",
            "A single reviewer is not inter-rater agreement.",
            "Uncertain, disputed and failed examples do not count as passing.",
            "This is not an automated semantic-grounding or production-quality guarantee.",
        ],
    }
    if expected_samples is not None:
        result["expected_sample_count"] = expected_samples
        result["review_coverage"] = sample_count / expected_samples
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Score offline human-reviewed support samples")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--expected-samples", type=int)
    args = parser.parse_args(argv)
    try:
        summary = summarize_human_review(args.input, expected_samples=args.expected_samples)
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
