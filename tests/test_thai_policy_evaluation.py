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
