"""Prevent stale FastEmbed metrics from being shown as live ONNX demo evidence."""

import json

import pytest

from src.api.services import ApplicationServices
from src.config.settings import Settings


def make_services(tmp_path, **overrides):
    config = {
        "eval_output_path": tmp_path / "missing" / "results.json",
        "demo_mode": True,
        "mock_llm_mode": True,
        "embedding_provider": "onnx",
        "embedding_model": "BAAI/bge-small-en-v1.5",
    }
    config.update(overrides)
    return ApplicationServices(
        Settings(_env_file=None, **config),
        retriever=None,
        workflow=None,
        provider_names=["mock"],
    )


def test_bundled_onnx_mock_report_fills_missing_host_output(tmp_path):
    service = make_services(tmp_path)
    report = service.evaluation_results()
    assert report["evaluation_mode"] == "deterministic_mock"
    assert report["execution"]["embedding_provider"] == "onnx"
    assert report["execution"]["embedding_model"] == "BAAI/bge-small-en-v1.5"
    assert report["dataset"]["sample_size"] == 8
    assert report["dataset"]["retrieval_corpus_size"] == 27
    assert report["dataset"]["fixture_revision"] == "demo-fixture-v1"
    assert report["evaluation_schema_version"] == 2
    assert report["policy_review"]["method"] == "structural_policy_gate_counts"
    assert "groundedness_pass_rate" not in report
    assert "unsupported_claim_rate" not in report
    assert report["limitations"]


def test_mismatched_provider_does_not_serve_embedded_old_report(tmp_path, caplog):
    service = make_services(tmp_path, embedding_provider="hashing")
    assert service.evaluation_results() == {"status": "not_evaluated"}
    assert "bundled:provider" in caplog.text
    assert "configured:missing" in caplog.text
    # Diagnostics contain only the allowlisted source label and mismatch codes.
    assert str(tmp_path) not in caplog.text
    assert "BAAI/bge-small-en-v1.5" not in caplog.text


def test_demo_mode_uses_mock_report_even_with_mock_llm_flag_disabled(tmp_path, monkeypatch):
    from pathlib import Path

    # Demo mode itself forces the application onto mock inference even if
    # Render retains MOCK_LLM_MODE=false in its older environment.
    service = make_services(tmp_path, mock_llm_mode=False)
    assert service.provider_health()["mock_mode"] is True
    monkeypatch.setattr(Path, "is_file", lambda self: False)
    report = service.evaluation_results()
    assert report["evaluation_mode"] == "deterministic_mock"
    assert report["execution"]["embedding_provider"] == "onnx"
    assert report["dataset"]["sample_size"] == 8


def test_demo_mode_rejects_mismatched_provider_without_mock_flag(tmp_path, monkeypatch):
    from pathlib import Path

    service = make_services(tmp_path, mock_llm_mode=False, embedding_provider="hashing")
    monkeypatch.setattr(Path, "is_file", lambda self: False)
    assert service.evaluation_results() == {"status": "not_evaluated"}


def test_nondemo_never_falls_back_to_bundled_mock_report(tmp_path):
    assert make_services(tmp_path, demo_mode=False).evaluation_results() == {
        "status": "not_evaluated"
    }


def test_existing_incompatible_mock_report_falls_back_to_verified_onnx_snapshot(tmp_path):
    report_path = tmp_path / "chosen.json"
    report_path.write_text(
        json.dumps(
            {
                "evaluation_mode": "deterministic_mock",
                "execution": {
                    "embedding_provider": "fastembed",
                    "embedding_model": "BAAI/bge-small-en-v1.5",
                },
            }
        ),
        encoding="utf-8",
    )
    service = make_services(tmp_path, eval_output_path=report_path)
    selected = service.evaluation_results()
    assert selected["execution"]["embedding_provider"] == "onnx"
    assert selected["dataset"]["sample_size"] == 8
    assert selected["generated_at"].startswith("2026-11-14T")


def test_existing_matching_report_still_takes_precedence(tmp_path):
    report_path = tmp_path / "chosen.json"
    bundled = make_services(tmp_path).evaluation_results()
    bundled["selected_test_marker"] = "explicit-compatible"
    report_path.write_text(json.dumps(bundled), encoding="utf-8")
    service = make_services(tmp_path, eval_output_path=report_path)
    assert service.evaluation_results()["selected_test_marker"] == "explicit-compatible"


@pytest.mark.parametrize(
    "invalid",
    ["missing", "inconsistent", "bad-shape", "invalid-json", "approved", "failed-invariant"],
)
def test_invalid_v2_policy_report_does_not_shadow_reviewed_snapshot(tmp_path, invalid):
    report_path = tmp_path / "chosen.json"
    report = make_services(tmp_path).evaluation_results()
    expected = report["policy_review"].copy()
    report["candidate_test_marker"] = True
    if invalid == "missing":
        del report["policy_review"]
    elif invalid == "inconsistent":
        report["policy_review"]["proposals_withheld"] -= 1
    elif invalid == "bad-shape":
        report["execution"] = ["onnx"]
    elif invalid == "approved":
        report["policy_review"].update(
            manual_review_routes=0,
            proposals_withheld=0,
            verified_proposals=expected["proposals_seen"],
        )
    elif invalid == "failed-invariant":
        report["policy_review"]["no_policy_abstentions_satisfy_structural_invariants"] = False
    contents = "{" if invalid == "invalid-json" else json.dumps(report)
    report_path.write_text(contents, encoding="utf-8")

    selected = make_services(tmp_path, eval_output_path=report_path).evaluation_results()
    assert selected.get("policy_review") == expected
    assert "candidate_test_marker" not in selected


def test_existing_non_demo_report_retains_existing_behavior(tmp_path):
    report_path = tmp_path / "chosen.json"
    report_path.write_text(json.dumps({"intent_accuracy": 0.9}), encoding="utf-8")
    service = make_services(tmp_path, demo_mode=False, eval_output_path=report_path)
    assert service.evaluation_results() == {"intent_accuracy": 0.9}


def test_packaged_onnx_resource_exactly_matches_reviewed_json():
    import hashlib
    from pathlib import Path

    from src.api.reviewed_onnx_report import SOURCE_SHA256, load_reviewed_onnx_report

    source = Path(__file__).resolve().parents[1] / "reports/evaluation/results.json"
    raw = source.read_text(encoding="utf-8")
    assert hashlib.sha256(raw.encode("utf-8")).hexdigest() == SOURCE_SHA256
    report = load_reviewed_onnx_report()
    assert report == json.loads(raw)
    assert report["execution"]["embedding_provider"] == "onnx"
    assert report["dataset"]["sample_size"] == 8


def test_packaged_onnx_resource_survives_missing_json_report_directories(tmp_path, monkeypatch):
    from pathlib import Path

    from src.api.reviewed_onnx_report import load_reviewed_onnx_report

    # Import the trusted Python source before simulating a Render build which
    # omits both custom and repository-level JSON report directories.
    assert load_reviewed_onnx_report()["evaluation_mode"] == "deterministic_mock"
    services = make_services(tmp_path)
    monkeypatch.setattr(Path, "is_file", lambda self: False)
    report = services.evaluation_results()
    assert report["execution"]["embedding_provider"] == "onnx"
    assert report["dataset"]["sample_size"] == 8
    assert report["dataset"]["retrieval_corpus_size"] == 27

    incompatible = make_services(tmp_path, embedding_provider="hashing")
    assert incompatible.evaluation_results() == {"status": "not_evaluated"}
