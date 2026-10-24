"""Atomic update of an EXISTING Space, with expected-parent revision protection.

Never creates repositories, changes hardware, or stores credentials in files.
Only invoked by a manually approved workflow with repo-scoped OIDC write access.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path

from huggingface_hub import CommitOperationAdd, HfApi

from scripts.preflight_existing_space import SPACE, verify_space

FILES = ("Dockerfile", "README.md", "app.tar.gz", "release-manifest.json")


def validate_bundle(directory: Path, expected_github_sha: str) -> dict:
    if {p.name for p in directory.iterdir()} != set(FILES):
        raise ValueError("Release folder must contain only four reviewed files")
    manifest = json.loads((directory / "release-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("space_id") != SPACE or manifest.get("source_sha") != expected_github_sha:
        raise ValueError("GitHub source SHA / Space target mismatch")
    for name, key in (
        ("Dockerfile", "dockerfile_sha256"),
        ("app.tar.gz", "source_archive_sha256"),
    ):
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != manifest.get(key):
            raise ValueError(f"Release bundle digest mismatch: {name}")
    if b"EMBEDDING_PROVIDER=onnx" not in (directory / "Dockerfile").read_bytes():
        raise ValueError("Expected ONNX production Dockerfile missing")
    if f"/tree/{expected_github_sha}" not in (directory / "README.md").read_text(encoding="utf-8"):
        raise ValueError("Missing source provenance in Space README")
    return manifest


def make_operations(directory: Path):
    """Upload as exactly one parent-locked commit; never delete unrelated files."""
    return [
        CommitOperationAdd(path_in_repo=name, path_or_fileobj=directory / name) for name in FILES
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--expected-current-sha", required=True)
    parser.add_argument("--github-sha", required=True)
    parser.add_argument("--result-file", type=Path, required=True)
    args = parser.parse_args()

    if not re.fullmatch(r"[0-9a-f]{40}", args.github_sha):
        raise ValueError("Invalid GitHub commit SHA")
    if not os.environ.get("HF_TOKEN"):
        raise ValueError("Missing short-lived Hugging Face OIDC credential")
    manifest = validate_bundle(args.directory, args.github_sha)
    api = HfApi(token=os.environ["HF_TOKEN"])
    space = api.space_info(repo_id=SPACE)
    verify_space(
        {
            "id": space.id,
            "sha": space.sha,
            "sdk": space.sdk,
            "runtime": {
                "stage": space.runtime.stage,
                "hardware": {
                    "current": space.runtime.hardware,
                    "requested": space.runtime.requested_hardware,
                },
            },
        },
        args.expected_current_sha,
    )
    result = api.create_commit(
        repo_id=SPACE,
        repo_type="space",
        revision="main",
        parent_commit=args.expected_current_sha,
        create_pr=False,
        operations=make_operations(args.directory),
        commit_message=f"Release ONNX RAG from GitHub {args.github_sha[:12]}",
        commit_description=(
            f"Source SHA: {args.github_sha}\nBundle SHA256: {manifest['source_archive_sha256']}"
        ),
    )
    deployed_sha = result.oid
    if not isinstance(deployed_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", deployed_sha):
        raise RuntimeError("Hugging Face did not return a verified commit OID")
    attestation = {
        "space_id": SPACE,
        "previous_space_sha": args.expected_current_sha,
        "new_space_sha": deployed_sha,
        "github_source_sha": args.github_sha,
        "source_archive_sha256": manifest["source_archive_sha256"],
    }
    args.result_file.write_text(json.dumps(attestation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(attestation))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
