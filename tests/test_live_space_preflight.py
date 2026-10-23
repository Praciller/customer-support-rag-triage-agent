"""Offline guards for the public Space release preflight; no network access."""

from __future__ import annotations

import copy

import pytest

from scripts.verify_live_space import BASE_URL, HUB_URL, TEST_TICKET, run_check

SHA = "a2661562ff1a2a7b7f15e4b9145cb007c98444a5"


def fixtures():
    return {
        HUB_URL: {
            "id": "Pracill/customer-support-rag-triage-agent",
            "sha": SHA,
            "runtime": {"stage": "RUNNING", "hardware": {"current": "cpu-basic"}},
        },
        BASE_URL + "/ready": {
            "readiness": "ready",
            "index": {"ready": True, "records": 27, "indexed": 27},
        },
        BASE_URL + "/provider-health": {
            "demo_mode": True,
            "mock_mode": True,
            "ingestion_enabled": False,
        },
        BASE_URL + "/eval/results": {
            "evaluation_mode": "deterministic_mock",
            "dataset": {"sample_size": 8},
            "retrieval": {"precision_at_k": 0.375},
        },
        BASE_URL + "/triage": {
            "trace": [{"node": i} for i in range(7)],
            "next_action": "ask_for_order_id",
        },
    }


def fetcher(responses, *, calls=None):
    def fetch(url, payload):
        if calls is not None:
            calls.append((url, payload))
        if url == BASE_URL + "/triage":
            assert payload == TEST_TICKET
        else:
            assert payload is None
        return 200, copy.deepcopy(responses[url])

    return fetch


def test_get_only_default_passes_without_claiming_release_sync():
    calls = []
    report = run_check(fetcher(fixtures(), calls=calls), expected_space_sha=SHA)
    assert report["result"] == "pass"
    assert report["space_sha"] == SHA
    assert report["expected_sha_matched"] is True
    assert report["synthetic_triage_executed"] is False
    assert report["unauthorized_ingest_denial"] == "not_tested_no_mutation_attempt"
    assert len(calls) == 5
    assert all(payload is None for _, payload in calls)


def test_opt_in_synthetic_triage_requires_seven_nodes():
    report = run_check(fetcher(fixtures()), triage=True)
    assert report["trace_nodes"] == 7
    assert report["next_action"] == "ask_for_order_id"
    assert report["expected_sha_matched"] is False


def test_rejects_enabled_ingestion_before_triage():
    responses = fixtures()
    responses[BASE_URL + "/provider-health"]["ingestion_enabled"] = True
    calls = []
    with pytest.raises(ValueError, match="Public ingestion"):
        run_check(fetcher(responses, calls=calls), triage=True)
    assert BASE_URL + "/triage" not in [url for url, _ in calls]


def test_rejects_unexpected_space_revision():
    with pytest.raises(ValueError, match="does not match"):
        run_check(fetcher(fixtures()), expected_space_sha="b" * 40)


def test_rejects_revision_change_during_smoke():
    responses = fixtures()
    hub_reads = 0

    def changed_fetch(url, payload):
        nonlocal hub_reads
        status, data = fetcher(responses)(url, payload)
        if url == HUB_URL:
            hub_reads += 1
            if hub_reads == 2:
                data["sha"] = "b" * 40
        return status, data

    with pytest.raises(ValueError, match="changed during"):
        run_check(changed_fetch)


def test_rejects_incomplete_index_or_evaluation():
    responses = fixtures()
    responses[BASE_URL + "/ready"]["index"]["indexed"] = 26
    with pytest.raises(ValueError, match="index count"):
        run_check(fetcher(responses))
    responses = fixtures()
    responses[BASE_URL + "/eval/results"]["evaluation_mode"] = "unknown"
    with pytest.raises(ValueError, match="Evaluation"):
        run_check(fetcher(responses))
