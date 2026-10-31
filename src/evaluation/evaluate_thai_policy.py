"""Offline, permission-aware lexical evaluation for the synthetic Thai policy slice."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DATASET_PATH = Path(__file__).resolve().parents[2] / "data/eval/thai_policy_slice.json"
REPORT_PATH = Path("reports/evaluation/thai_policy_slice.md")


@dataclass(frozen=True)
class PolicyRecord:
    id: str
    scope: str
    permission: str
    title: str
    text: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class PolicyQuery:
    id: str
    query: str
    scope: str
    permissions: frozenset[str]
    expected_ids: frozenset[str]
    should_abstain: bool
    injection: bool


def _grams(text: str) -> set[str]:
    compact = re.sub(r"\s+", "", text.lower())
    # Thai has no whitespace between words; character bigrams are a small,
    # dependency-free lexical baseline, not a semantic embedding model.
    return {compact[index : index + 2] for index in range(max(0, len(compact) - 1))}


def load_dataset(path: Path = DATASET_PATH) -> tuple[list[PolicyRecord], list[PolicyQuery]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("synthetic") is not True or raw.get("language") != "th":
        raise ValueError("Thai evaluation dataset must be explicitly synthetic and language=th")
    records = [PolicyRecord(**{**item, "tags": tuple(item["tags"])}) for item in raw["records"]]
    queries = [
        PolicyQuery(
            **{
                **item,
                "permissions": frozenset(item["permissions"]),
                "expected_ids": frozenset(item["expected_ids"]),
            }
        )
        for item in raw["cases"]
    ]
    if not records or not queries or len({r.id for r in records}) != len(records):
        raise ValueError("Thai evaluation dataset must contain unique records and cases")
    return records, queries


def retrieve(
    query: PolicyQuery, records: list[PolicyRecord], *, min_score: float = 0.50
) -> list[tuple[PolicyRecord, float]]:
    # Authorization is applied before scoring, so forbidden records cannot rank or leak.
    allowed = [
        record
        for record in records
        if record.scope == query.scope and record.permission in query.permissions
    ]
    query_grams = _grams(query.query)
    ranked: list[tuple[PolicyRecord, float]] = []
    for record in allowed:
        document_grams = _grams(" ".join((record.title, record.text, *record.tags)))
        score = len(query_grams & document_grams) / max(1, len(query_grams))
        if score >= min_score:
            ranked.append((record, score))
    return sorted(ranked, key=lambda pair: (-pair[1], pair[0].id))


def evaluate(path: Path = DATASET_PATH) -> dict[str, Any]:
    records, cases = load_dataset(path)
    rows: list[dict[str, Any]] = []
    for case in cases:
        results = retrieve(case, records)
        ids = [record.id for record, _ in results]
        abstained = not ids
        rows.append(
            {
                "case_id": case.id,
                "expected_ids": sorted(case.expected_ids),
                "retrieved_ids": ids,
                "expected_abstain": case.should_abstain,
                "abstained": abstained,
                "injection": case.injection,
                "permission_safe": all(
                    record.scope == case.scope and record.permission in case.permissions
                    for record, _ in results
                ),
                "correct": (case.should_abstain == abstained)
                and (case.should_abstain or bool(set(ids) & case.expected_ids)),
            }
        )
    positives = sum(not case.should_abstain for case in cases)
    negatives = len(cases) - positives
    injections = [row for row in rows if row["injection"]]
    checks = {
        "cases_present": bool(cases),
        "positive_cases_present": positives > 0,
        "negative_abstention_cases_present": negatives > 0,
        "injection_cases_present": bool(injections),
        "permission_filter_pass": all(row["permission_safe"] for row in rows),
        "case_accuracy_pass": all(row["correct"] for row in rows),
        "injection_cannot_expand_permission": all(
            row["permission_safe"] and "th-finance-refund" not in row["retrieved_ids"]
            for row in injections
        ),
    }
    return {
        "dataset_id": "synthetic-thai-enterprise-policy-v1",
        "mode": "offline_character_bigram_lexical_baseline",
        "record_count": len(records),
        "case_count": len(cases),
        "positive_cases": positives,
        "negative_abstention_cases": negatives,
        "injection_cases": len(injections),
        "correct_cases": sum(row["correct"] for row in rows),
        "permission_safe_cases": sum(row["permission_safe"] for row in rows),
        "denominator": len(rows),
        "checks": checks,
        "all_checks_passed": all(checks.values()),
        "cases": rows,
        "limitations": [
            "All records and queries are synthetic; they do not define enterprise policy.",
            "Character bigram overlap is lexical, not Thai semantic retrieval or embeddings.",
            "Permission labels filter this fixture; they are not production authorization.",
            "Injection tests filter behavior, not semantic LLM immunity.",
        ],
    }


def render_report(result: dict[str, Any]) -> str:
    rows = "\n".join(
        f"| `{row['case_id']}` | {'yes' if row['expected_abstain'] else 'no'} | "
        f"{'yes' if row['abstained'] else 'no'} | {'PASS' if row['correct'] else 'FAIL'} |"
        for row in result["cases"]
    )
    checks = "\n".join(
        f"| `{key}` | {'PASS' if value else 'FAIL'} |" for key, value in result["checks"].items()
    )
    limitations = "\n".join(f"- {item}" for item in result["limitations"])
    return f"""# Synthetic Thai Policy Retrieval Slice

Mode: `{result["mode"]}`; offline only; no external provider or paid API.
Dataset: `{result["dataset_id"]}` ({result["record_count"]} records, all synthetic).

## Scope and denominator

Cases: **{result["case_count"]}**; positive retrieval: **{result["positive_cases"]}**;
negative abstention: **{result["negative_abstention_cases"]}**; injection:
**{result["injection_cases"]}**. Correct: **{result["correct_cases"]}/{result["denominator"]}**;
permission-safe: **{result["permission_safe_cases"]}/{result["denominator"]}**.

| Case | Expected abstain | Did abstain | Result |
| --- | --- | --- | --- |
{rows}

## Invariants

| Check | Result |
| --- | --- |
{checks}

## Limitations and upgrade path

{limitations}

Practical next steps: review policy taxonomy and access labels with policy owners; expand a
reviewed,
non-sensitive Thai benchmark with adjudicated relevance and refusal labels; compare this baseline
with a locally hosted Thai-capable embedding model and reranker; evaluate citation support and
adversarial cases with human reviewers before considering live inference. Enforce identity-derived
authorization at a trusted service boundary, outside the retriever fixture.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-path", type=Path, default=DATASET_PATH)
    parser.add_argument("--report-path", type=Path)
    args = parser.parse_args()
    result = evaluate(args.dataset_path)
    if args.report_path:
        args.report_path.parent.mkdir(parents=True, exist_ok=True)
        args.report_path.write_text(render_report(result), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(0 if result["all_checks_passed"] else 1)


if __name__ == "__main__":
    main()
