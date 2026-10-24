"""Detect NEW production dependency advisories without waiving known Pillow risk.

The checked-in baseline only permits the exact historic advisory IDs documented
in the release tracker. Passing this guard is NOT a clean vulnerability scan,
release approval, or evidence that the known Pillow issues are mitigated.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def compare_advisories(
    report: dict[str, Any], baseline: dict[str, Any]
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Return (known_unresolved, unexpected) by normalized package name."""
    dependencies = report.get("dependencies")
    if not isinstance(dependencies, list) or not dependencies:
        raise ValueError("Audit report must include a nonempty dependencies list")
    allowed = baseline.get("allowed_known_advisories")
    if (
        baseline.get("status") != "unresolved_not_a_release_waiver"
        or not isinstance(allowed, dict)
        or set(allowed) != {"pillow"}
        or not isinstance(allowed["pillow"], list)
        or not allowed["pillow"]
        or any(not isinstance(i, str) or not i.strip() for i in allowed["pillow"])
        or len(set(allowed["pillow"])) != len(allowed["pillow"])
    ):
        raise ValueError("Known-advisory baseline invalid: only Pillow is permitted")

    observed: dict[str, set[str]] = {}
    for dep in dependencies:
        if not isinstance(dep, dict):
            raise ValueError("Malformed audited dependency")
        package = dep.get("name")
        vulns = dep.get("vulns")
        if not isinstance(package, str) or not package.strip() or not isinstance(vulns, list):
            raise ValueError("Missing package name or vulnerability data")
        name = package.lower().replace("_", "-")
        if name in observed:
            raise ValueError(f"Duplicate package in audit report: {name}")
        ids: set[str] = set()
        for vuln in vulns:
            if not isinstance(vuln, dict):
                raise ValueError(f"Malformed vulnerability for {name}")
            ident = vuln.get("id")
            if not isinstance(ident, str) or not ident.strip():
                raise ValueError(f"Missing vulnerability ID for {name}")
            ids.add(ident)
        observed[name] = ids

    known: dict[str, list[str]] = {}
    unexpected: dict[str, list[str]] = {}
    for name, ids in observed.items():
        allowed_ids = set(allowed.get(name, []))
        if ids & allowed_ids:
            known[name] = sorted(ids & allowed_ids)
        if ids - allowed_ids:
            unexpected[name] = sorted(ids - allowed_ids)
    return known, unexpected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument(
        "--require-clean", action="store_true", help="Fail on ALL advisories at release time"
    )
    args = parser.parse_args()
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
        baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
        if not isinstance(report, dict) or not isinstance(baseline, dict):
            raise ValueError("Audit and baseline must be JSON objects")
        known, unexpected = compare_advisories(report, baseline)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"FAIL: Cannot validate Python audit: {type(exc).__name__}: {exc}")
        return 2

    count = sum(len(ids) for ids in known.values())
    print(f"Known unresolved Pillow advisories: {count}. RELEASE SECURITY HOLD remains.")
    if unexpected:
        print("FAIL: New or non-baselined production Python advisories:")
        for package, ids in sorted(unexpected.items()):
            print(f"  {package}: {', '.join(ids)}")
        return 1
    if args.require_clean and known:
        print("FAIL: Release requires an advisory-free production dependency graph.")
        return 1
    print("PASS: No new Python advisories relative to the explicit baseline.")
    print("IMPORTANT: This is NOT an advisory-free scan or deployment approval.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
