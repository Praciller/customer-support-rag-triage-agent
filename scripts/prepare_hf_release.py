"""Create a deterministic, minimal Hugging Face Docker Space release bundle.

Only git-tracked allowlisted files are packaged. This command NEVER deploys.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import re
import subprocess
import tarfile
from pathlib import Path

SPACE_ID = "Pracill/customer-support-rag-triage-agent"
ROOT = Path(__file__).resolve().parents[1]
ALLOWED = ("src/", "frontend/", "prompts/", "data/demo/", "data/eval/", "reports/evaluation/")
EXACT = {"requirements.production.txt"}
DOCKERFILE = ROOT / "deploy/huggingface/Dockerfile.bundle"
README = """---
title: Customer Support Rag Triage Agent
emoji: 🤖
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
short_description: Grounded RAG triage with auditable workflow traces.
---

This public demo uses synthetic fixtures, mock responses, and a pinned ONNX embedding model.
Public ingestion is disabled.

Source: https://github.com/Praciller/customer-support-rag-triage-agent/tree/{sha}
"""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_output(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def tracked_sources() -> list[Path]:
    names = git_output("ls-files", "-z", "--").split(b"\0")
    selected: list[Path] = []
    for raw in names:
        if not raw:
            continue
        name = raw.decode("utf-8")
        if name not in EXACT and not name.startswith(ALLOWED):
            continue
        path = ROOT / name
        if (
            not path.is_file()
            or path.is_symlink()
            or any(
                x in {".git", "node_modules", ".env", "__pycache__", ".cache"} for x in path.parts
            )
        ):
            raise ValueError(f"Unsafe or missing tracked release input: {name}")
        selected.append(Path(name))
    if len(selected) < 25 or Path("requirements.production.txt") not in selected:
        raise ValueError("Missing required production source tree")
    return sorted(selected, key=lambda p: p.as_posix())


def render_archive(files: list[Path]) -> bytes:
    out = io.BytesIO()
    with (
        gzip.GzipFile(fileobj=out, mode="wb", filename="", mtime=0, compresslevel=9) as zip_out,
        tarfile.open(fileobj=zip_out, mode="w", format=tarfile.USTAR_FORMAT) as archive,
    ):
        for name in files:
            data = (ROOT / name).read_bytes()
            info = tarfile.TarInfo(name.as_posix())
            info.size = len(data)
            info.mode = 0o644
            info.uid = info.gid = info.mtime = 0
            info.uname = info.gname = ""
            archive.addfile(info, io.BytesIO(data))
    return out.getvalue()


def prepare(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("Output directory must be empty")
    sha = git_output("rev-parse", "HEAD").decode().strip()
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("Invalid source git SHA")
    files = tracked_sources()
    archive = render_archive(files)
    dockerfile = DOCKERFILE.read_bytes()
    if (
        b"EMBEDDING_PROVIDER=onnx" not in dockerfile
        or b"ALLOW_PUBLIC_INGEST=false" not in dockerfile
    ):
        raise ValueError("Unsafe Docker recipe changed")
    manifest = {
        "space_id": SPACE_ID,
        "github_repository": "Praciller/customer-support-rag-triage-agent",
        "source_sha": sha,
        "source_archive_sha256": sha256(archive),
        "dockerfile_sha256": sha256(dockerfile),
        "source_file_count": len(files),
        "embedding_model_revision": "aa8f8b060edb00e03bfdd08813a2949946c8ba55",
    }
    (output / "app.tar.gz").write_bytes(archive)
    (output / "Dockerfile").write_bytes(dockerfile)
    (output / "README.md").write_text(README.format(sha=sha), encoding="utf-8")
    (output / "release-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.output), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
