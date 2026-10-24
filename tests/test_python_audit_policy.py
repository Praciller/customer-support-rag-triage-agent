"""Fail-closed regression tests for the production advisory drift policy."""

import json
import sys

import pytest

from scripts.check_python_audit import compare_advisories, main

BASELINE = {
    "status": "unresolved_not_a_release_waiver",
    "allowed_known_advisories": {"pillow": ["CVE-OLD", "GHSA-OLD"]},
}


def report(*dependencies):
    return {"dependencies": list(dependencies)}


def dep(name, *ids):
    return {"name": name, "version": "12.3.0", "vulns": [{"id": value} for value in ids]}


def test_strict_release_mode_rejects_existing_advisories(tmp_path, monkeypatch):
    report_path = tmp_path / "audit.json"
    baseline_path = tmp_path / "baseline.json"
    report_path.write_text(json.dumps(report(dep("pillow", "CVE-OLD"))), encoding="utf-8")
    baseline_path.write_text(json.dumps(BASELINE), encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "check_python_audit.py",
            "--report",
            str(report_path),
            "--baseline",
            str(baseline_path),
            "--require-clean",
        ],
    )
    assert main() == 1


def test_exact_documented_risk_does_not_block_other_ci():
    known, unexpected = compare_advisories(report(dep("Pillow", "CVE-OLD", "GHSA-OLD")), BASELINE)
    assert known == {"pillow": ["CVE-OLD", "GHSA-OLD"]}
    assert unexpected == {}


def test_remediated_vulnerabilities_are_allowed_to_disappear():
    known, unexpected = compare_advisories(report(dep("pillow"), dep("fastapi")), BASELINE)
    assert known == unexpected == {}


def test_additional_pillow_advisory_fails_closed():
    _, unexpected = compare_advisories(report(dep("pillow", "CVE-OLD", "CVE-NEW")), BASELINE)
    assert unexpected == {"pillow": ["CVE-NEW"]}


def test_other_package_advisory_fails_closed():
    _, unexpected = compare_advisories(
        report(dep("pillow", "CVE-OLD"), dep("fsspec", "CVE-BAD")), BASELINE
    )
    assert unexpected == {"fsspec": ["CVE-BAD"]}


@pytest.mark.parametrize(
    "bad_report",
    [
        {},
        {"dependencies": []},
        {"dependencies": [{}]},
        report({"name": "pillow", "vulns": None}),
        report(dep("pillow"), dep("PILLOW")),
        report({"name": "pillow", "vulns": [{}]}),
    ],
)
def test_missing_or_invalid_scan_fails_closed(bad_report):
    with pytest.raises(ValueError):
        compare_advisories(bad_report, BASELINE)


@pytest.mark.parametrize(
    "baseline",
    [
        {},
        {"status": "approved", "allowed_known_advisories": {"pillow": ["CVE-OLD"]}},
        {
            "status": "unresolved_not_a_release_waiver",
            "allowed_known_advisories": {"pillow": ["CVE-OLD"], "other": ["CVE-NEW"]},
        },
        {
            "status": "unresolved_not_a_release_waiver",
            "allowed_known_advisories": {"pillow": ["CVE-OLD", "CVE-OLD"]},
        },
    ],
)
def test_unauthorized_baseline_change_fails_closed(baseline):
    with pytest.raises(ValueError):
        compare_advisories(report(dep("pillow", "CVE-OLD")), baseline)
