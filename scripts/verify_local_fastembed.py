"""Bounded, loopback-only FastEmbed Docker-image smoke test.

Run after starting the local Dockerfile.hf container on 127.0.0.1:17860.
Checks the actual FastEmbed provider, not the hashing CI shortcut.
No credentials, real customer data, ingestion writes or external hosts.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from typing import Any
from urllib import error, request
from urllib.parse import urlsplit

BASE_URL = "http://127.0.0.1:17860"
SYNTHETIC_TICKET = {"message": "My card has not arrived. How can I track it?", "top_k": 5}
MAX_BYTES = 2_000_000
Fetch = Callable[[str, dict[str, Any] | None], tuple[int, dict[str, Any]]]


def validate_base_url(url: str) -> str:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in {"127.0.0.1", "localhost"}
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
        or parsed.port is None
    ):
        raise ValueError("Base URL must be http://127.0.0.1:<port> or localhost, no path/auth")
    return url.rstrip("/")


def fetch_json(url: str, body: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = request.Request(
        url,
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        headers=headers,
    )
    try:
        with request.urlopen(req, timeout=35) as response:
            raw = response.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ValueError("Response exceeded byte limit")
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise ValueError("Response must be a JSON object")
            return response.status, data
    except error.HTTPError as exc:
        return exc.code, {}


def check(fetch: Fetch, base: str = BASE_URL) -> dict[str, Any]:
    base = validate_base_url(base)

    status, ready = fetch(base + "/ready", None)
    idx = ready.get("index", {})
    if not (
        status == 200
        and ready.get("readiness") == "ready"
        and idx.get("ready") is True
        and idx.get("records") == 27
        and idx.get("indexed") == 27
        and ready.get("demo_mode") is True
    ):
        raise ValueError("Demo readiness/index was not the expected 27/27")

    status, provider = fetch(base + "/provider-health", None)
    if not (
        status == 200
        and provider.get("embedding_provider") == "fastembed"
        and provider.get("demo_mode") is True
        and provider.get("mock_mode") is True
        and provider.get("live_provider_calls_enabled") is False
        and provider.get("ingestion_enabled") is False
        and provider.get("qdrant_mode") == "local"
    ):
        raise ValueError("Release-image FastEmbed demo/admin/provider boundary changed")

    status, ds = fetch(base + "/dataset-info", None)
    if status != 200 or ds.get("records") != 27:
        raise ValueError("Bundled synthetic demo dataset is not 27 records")

    status, evaluation = fetch(base + "/eval/results", None)
    if not (
        status == 200
        and evaluation.get("evaluation_mode") == "deterministic_mock"
        and evaluation.get("dataset", {}).get("sample_size") == 8
    ):
        raise ValueError("Expected deterministic mock evaluation fixture is unavailable")

    status, triage = fetch(base + "/triage", SYNTHETIC_TICKET)
    if not (
        status == 200
        and len(triage.get("trace", [])) == 7
        and triage.get("provider_used") == "mock"
    ):
        raise ValueError("Synthetic seven-stage FastEmbed triage failed")

    # The public-ingest flag MUST be false before any denial probe is made.
    status, _ = fetch(base + "/ingest", {"recreate": False, "sample_size": 1})
    if status != 403:
        raise ValueError("Unauthenticated ingestion was not denied")

    return {
        "result": "pass",
        "scope": "local_Dockerfile.hf_fastembed_image_only_not_HF_deployment",
        "indexed_records": idx["indexed"],
        "embedding_provider": provider["embedding_provider"],
        "embedding_model": provider.get("embedding_model"),
        "mock_mode": True,
        "seven_node_trace": len(triage["trace"]),
        "grounded": triage.get("grounded"),
        "citation_integrity": triage.get("citation_integrity"),
        "next_action": triage.get("next_action"),
        "evaluation_samples": 8,
        "public_ingestion_http_status": 403,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Synthetic smoke against a local FastEmbed Space image"
    )
    parser.add_argument("--base-url", default=BASE_URL, help="Loopback URL only")
    args = parser.parse_args()
    try:
        report = check(fetch_json, args.base_url)
    except (ValueError, TypeError, AttributeError, error.URLError, OSError) as exc:
        print(json.dumps({"result": "fail", "reason": str(exc)[:200]}))
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
