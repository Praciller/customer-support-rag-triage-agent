"""Read-only, fail-closed check of existing free-hardware Hugging Face Space."""

from __future__ import annotations

import argparse
import json
import re
from urllib.request import ProxyHandler, Request, build_opener

SPACE = "Pracill/customer-support-rag-triage-agent"
URL = f"https://huggingface.co/api/spaces/{SPACE}"
OPENER = build_opener(ProxyHandler({}))


def verify_space(data: dict, expected_sha: str) -> dict:
    if not re.fullmatch(r"[0-9a-f]{40}", expected_sha):
        raise ValueError("expected Space SHA must contain exactly 40 lowercase hex characters")
    runtime = data.get("runtime")
    if not isinstance(runtime, dict):
        raise ValueError("Space runtime metadata missing")
    hardware = runtime.get("hardware") or {}
    if (
        data.get("id") != SPACE
        or data.get("sha") != expected_sha
        or data.get("sdk") != "docker"
        or hardware.get("current") != "cpu-basic"
        or hardware.get("requested") not in (None, "cpu-basic")
        or runtime.get("stage") != "RUNNING"
    ):
        raise ValueError("Existing Space SHA / identity / CPU Basic / runtime gate failed")
    return {
        "space_id": SPACE,
        "previous_sha": expected_sha,
        "sdk": "docker",
        "current_hardware": "cpu-basic",
        "runtime": "RUNNING",
        "note": "Read-only hardware/identity evidence, NOT an entitlement or billing guarantee.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-sha", required=True)
    args = parser.parse_args()
    try:
        req = Request(URL, headers={"Accept": "application/json"})
        with OPENER.open(req, timeout=20) as response:
            data = json.loads(response.read(500_000))
        print(json.dumps(verify_space(data, args.expected_sha), indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"Space preflight FAILED: {type(exc).__name__}: {str(exc)[:200]}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
