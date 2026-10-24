"""Verify newly published Hugging Face revision, manifest provenance and CPU Basic runtime.

The actual synthetic live workflow is tested separately by verify_live_space.py.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from urllib.request import ProxyHandler, Request, build_opener

from scripts.preflight_existing_space import SPACE, URL

OPENER = build_opener(ProxyHandler({}))


def download_json(url: str) -> dict:
    with OPENER.open(Request(url, headers={"Accept": "application/json"}), timeout=25) as resp:
        obj = json.loads(resp.read(300_000))
    if not isinstance(obj, dict):
        raise ValueError("Expected JSON object")
    return obj


def verify_published(actual: dict, expected: dict, manifest: dict) -> None:
    if actual.get("id") != SPACE or actual.get("sha") != expected["new_space_sha"]:
        raise ValueError("Space revision does not match publish result")
    if actual.get("sdk") != "docker":
        raise ValueError("Space switched away from Docker")
    runtime = actual.get("runtime") or {}
    hardware = runtime.get("hardware") or {}
    if (
        runtime.get("stage") != "RUNNING"
        or hardware.get("current") != "cpu-basic"
        or hardware.get("requested") not in (None, "cpu-basic")
    ):
        raise ValueError("Space not running on free CPU Basic")
    if (
        manifest.get("space_id") != SPACE
        or manifest.get("source_sha") != expected["github_source_sha"]
        or manifest.get("source_archive_sha256") != expected["source_archive_sha256"]
    ):
        raise ValueError("Published source provenance does not match GitHub release")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-file", type=Path, required=True)
    parser.add_argument("--release-dir", type=Path, required=True)
    args = parser.parse_args()
    expected = json.loads(args.result_file.read_text(encoding="utf-8"))
    full_sha = expected["new_space_sha"]
    if not re.fullmatch(r"[0-9a-f]{40}", full_sha):
        raise ValueError("Invalid released Space SHA")
    local = json.loads((args.release_dir / "release-manifest.json").read_text(encoding="utf-8"))
    raw_url = f"https://huggingface.co/spaces/{SPACE}/raw/{full_sha}/release-manifest.json"

    last_error = None
    for _ in range(75):  # Max 15 minutes including one current poll
        try:
            published_manifest = download_json(raw_url)
            if published_manifest != local:
                raise ValueError("Published manifest differs from GitHub input")
            observed = download_json(URL)
            verify_published(observed, expected, published_manifest)
            print(
                json.dumps(
                    {
                        "result": "pass",
                        "space_sha": full_sha,
                        "github_source_sha": expected["github_source_sha"],
                        "hardware": "cpu-basic",
                        "runtime": "RUNNING",
                    }
                )
            )
            return 0
        except (OSError, ValueError, KeyError, TypeError) as exc:
            last_error = f"{type(exc).__name__}: {str(exc)[:160]}"
            time.sleep(12)
    print(f"Live provenance / CPU Basic verification FAILED: {last_error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
