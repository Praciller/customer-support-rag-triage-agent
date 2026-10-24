"""Non-deploying release preflight for the public, synthetic Hugging Face demo.

Only GET requests are sent by default. --triage sends one synthetic ticket;
the tool deliberately never attempts /ingest or any privileged action.
No customer data, credentials, package installation, or paid job is needed.
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Callable
from typing import Any
from urllib import error, request

SPACE_ID = "Pracill/customer-support-rag-triage-agent"
HUB_URL = f"https://huggingface.co/api/spaces/{SPACE_ID}"
BASE_URL = "https://pracill-customer-support-rag-triage-agent.hf.space"
TEST_TICKET = {"message": "My new card has not arrived. How can I track it?", "top_k": 5}
MAX_RESPONSE_BYTES = 2_000_000
# Keep this direct-invocation script self-contained (stdlib-only).
WORKFLOW_STAGES = (
    "normalize_message",
    "classify_intent",
    "detect_urgency",
    "retrieve_similar_cases",
    "generate_support_response",
    "grounding_check",
    "suggest_next_action",
)
Fetcher = Callable[[str, dict[str, Any] | None], tuple[int, dict[str, Any]]]


class RejectRedirects(request.HTTPRedirectHandler):
    """Never follow a redirect from a fixed public release-verification URL."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


# Ignore proxy environment variables so preflight traffic only targets the
# reviewed HTTPS endpoints, not an injected or accidental HTTP proxy.
SAFE_OPENER = request.build_opener(request.ProxyHandler({}), RejectRedirects())


def fetch_json(url: str, payload: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    headers = {"Accept": "application/json"}
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=body, headers=headers)
    try:
        with SAFE_OPENER.open(req, timeout=35) as resp:
            raw = resp.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise ValueError("JSON response exceeds the bounded size limit")
            parsed = json.loads(raw)
            if not isinstance(parsed, dict):
                raise ValueError("JSON response must be an object")
            return resp.status, parsed
    except error.HTTPError as exc:
        return exc.code, {}


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def run_check(
    fetch: Fetcher,
    *,
    triage: bool = False,
    expected_space_sha: str | None = None,
    expected_records: int = 27,
    expected_provider: str = "fastembed",
) -> dict[str, Any]:
    require(expected_provider in {"fastembed", "onnx"}, "Unreviewed provider type")
    if expected_space_sha is not None:
        require(
            bool(re.fullmatch(r"[0-9a-f]{40}", expected_space_sha)),
            "Expected Space SHA must be full lowercase 40-character hex",
        )
    status, hub = fetch(HUB_URL, None)
    sha = hub.get("sha")
    require(
        status == 200 and hub.get("id") == SPACE_ID,
        "Hugging Face Space identity cannot be verified",
    )
    require(
        isinstance(sha, str) and bool(re.fullmatch(r"[0-9a-f]{40}", sha)),
        "Space revision is unavailable",
    )
    require(hub.get("runtime", {}).get("stage") == "RUNNING", "Hugging Face Space is not running")
    if expected_space_sha:
        require(
            sha == expected_space_sha,
            "Space revision does not match the independently supplied expected SHA",
        )

    status, ready = fetch(BASE_URL + "/ready", None)
    index = ready.get("index", {})
    require(status == 200 and ready.get("readiness") == "ready", "Live API is not ready")
    require(index.get("ready") is True, "Bounded index is not ready")
    require(
        index.get("records") == expected_records and index.get("indexed") == expected_records,
        "Bounded index count differs from expected",
    )

    status, provider = fetch(BASE_URL + "/provider-health", None)
    require(
        status == 200 and provider.get("demo_mode") is True,
        "Live provider health is not the key-free demo",
    )
    require(provider.get("mock_mode") is True, "Live mock provider mode changed")
    require(
        provider.get("embedding_provider") == expected_provider
        and provider.get("embedding_model") == "BAAI/bge-small-en-v1.5"
        and provider.get("qdrant_mode") == "local"
        and provider.get("live_provider_calls_enabled") is False,
        "Live embedding/model/provider boundary differs from the reviewed demo",
    )
    require(
        provider.get("ingestion_enabled") is False,
        "Public ingestion is enabled; preflight fails closed",
    )

    status, evaluation = fetch(BASE_URL + "/eval/results", None)
    require(
        status == 200 and evaluation.get("evaluation_mode") == "deterministic_mock",
        "Evaluation is missing or not deterministic",
    )
    sample_size = evaluation.get("dataset", {}).get("sample_size")
    require(sample_size == 8, "Evaluation fixture size has changed")
    precision_at_k = evaluation.get("retrieval", {}).get("precision_at_k")

    trace_nodes = None
    next_action = None
    if triage:
        status, decision = fetch(BASE_URL + "/triage", TEST_TICKET)
        require(
            status == 200 and isinstance(decision.get("trace"), list), "Synthetic triage failed"
        )
        trace = decision["trace"]
        trace_nodes = len(trace)
        require(
            trace_nodes == len(WORKFLOW_STAGES)
            and all(isinstance(step, dict) for step in trace)
            and tuple(step.get("node") for step in trace) == WORKFLOW_STAGES
            and all(step.get("status") == "completed" for step in trace)
            and decision.get("provider_used") == "mock"
            and decision.get("grounded") is True
            and decision.get("citation_integrity") is True
            and decision.get("fallback_used") is False
            and decision.get("degraded_mode") is False
            and decision.get("next_action") == "ask_for_order_id",
            "Synthetic triage workflow/grounding contract changed",
        )
        next_action = decision["next_action"]

    status, second_hub = fetch(HUB_URL, None)
    require(
        status == 200 and second_hub.get("sha") == sha,
        "Space revision changed during the smoke test",
    )
    return {
        "result": "pass",
        "scope": "live_space_only_not_github_release_attestation",
        "space_sha": sha,
        "expected_sha_matched": expected_space_sha is not None,
        "runtime": hub["runtime"]["stage"],
        "hardware": hub["runtime"].get("hardware", {}).get("current"),
        "indexed_records": index["indexed"],
        "evaluation_mode": evaluation["evaluation_mode"],
        "evaluation_samples": sample_size,
        "precision_at_5": precision_at_k,
        "synthetic_triage_executed": triage,
        "trace_nodes": trace_nodes,
        "next_action": next_action,
        "public_ingestion_enabled": False,
        "unauthorized_ingest_denial": "not_tested_no_mutation_attempt",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Safely verify the existing public Space without deploying"
    )
    parser.add_argument(
        "--triage", action="store_true", help="Send one fixed synthetic message through /triage"
    )
    parser.add_argument(
        "--expected-space-sha",
        default=None,
        help="Compare against an independently verified full Space SHA",
    )
    parser.add_argument(
        "--expected-records", type=int, default=27, help="Expected bounded demo record count"
    )
    parser.add_argument("--expected-provider", choices=("fastembed", "onnx"), default="fastembed")
    args = parser.parse_args()
    try:
        result = run_check(
            fetch_json,
            triage=args.triage,
            expected_space_sha=args.expected_space_sha,
            expected_records=args.expected_records,
            expected_provider=args.expected_provider,
        )
    except (ValueError, TypeError, AttributeError, KeyError, error.URLError, OSError) as exc:
        # Do not expose raw HTTP bodies or tokens in diagnostic output.
        print(json.dumps({"result": "fail", "reason": type(exc).__name__ + ": " + str(exc)[:200]}))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
