from dataclasses import replace

import pytest

from src.evaluation.evaluate_thai_policy import evaluate, load_dataset, retrieve


def test_thai_policy_slice_has_positive_negative_and_injection_denominators() -> None:
    result = evaluate()
    assert result["all_checks_passed"]
    assert result["positive_cases"] > 0
    assert result["negative_abstention_cases"] > 0
    assert result["injection_cases"] > 0
    assert result["denominator"] == result["case_count"]


def test_scope_and_permission_filter_prevent_cross_scope_leakage() -> None:
    records, queries = load_dataset()
    query = next(item for item in queries if item.id == "q-finance-denied")
    assert retrieve(query, records) == []


@pytest.mark.parametrize(
    ("case_id", "corrected_dimension"),
    [
        ("q-finance-permission-denied", "permission"),
        ("q-finance-scope-denied", "scope"),
    ],
)
def test_scope_and_permission_are_independent_boundaries(
    case_id: str, corrected_dimension: str
) -> None:
    records, queries = load_dataset()
    denied_query = next(item for item in queries if item.id == case_id)

    # This query repeats the synthetic finance record, exceeding the lexical
    # threshold. Only access filters—not low lexical similarity—may abstain.
    assert retrieve(denied_query, records) == []

    if corrected_dimension == "permission":
        allowed_query = replace(denied_query, permissions=frozenset({"finance_read"}))
    else:
        allowed_query = replace(denied_query, scope="finance")

    assert retrieve(allowed_query, records)[0][0].id == "th-finance-refund"


def test_prompt_injection_does_not_override_authorized_scope() -> None:
    records, queries = load_dataset()
    query = next(item for item in queries if item.injection)
    results = retrieve(query, records)
    # Abstention is a safe outcome when the mixed request lacks sufficient evidence.
    assert results == []
    assert all(record.scope == query.scope for record, _ in results)
    assert all(record.permission in query.permissions for record, _ in results)
    assert "th-finance-refund" not in {record.id for record, _ in results}


def test_missing_evidence_abstains() -> None:
    records, queries = load_dataset()
    query = next(item for item in queries if item.id == "q-no-evidence")
    assert retrieve(query, records) == []
