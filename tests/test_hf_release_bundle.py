"""Offline release bundle determinism and Space preflight authorization gates."""

import gzip
import hashlib
import io
import json
import tarfile

import pytest

from scripts.preflight_existing_space import SPACE, verify_space
from scripts.prepare_hf_release import (
    prepare,
    tracked_sources,
)


def test_bundle_deterministic_and_allowlisted(tmp_path):
    one = prepare(tmp_path / "first")
    two = prepare(tmp_path / "second")
    assert one == two
    folder = tmp_path / "first"
    packed = (folder / "app.tar.gz").read_bytes()
    assert hashlib.sha256(packed).hexdigest() == one["source_archive_sha256"]
    assert (tmp_path / "second" / "app.tar.gz").read_bytes() == packed
    with tarfile.open(fileobj=io.BytesIO(gzip.decompress(packed))) as archive:
        names = archive.getnames()
        assert len(names) == one["source_file_count"]
        assert "requirements.production.txt" in names
        assert "src/retrieval/onnx_bge.py" in names
        assert "frontend/package.json" in names
        assert "data/demo/support_cases.json" in names
        assert not any(n.startswith((".git", ".github", "tests/", "docs/")) for n in names)
        assert all(member.isfile() for member in archive.getmembers())
    assert "sdk: docker" in (folder / "README.md").read_text(encoding="utf-8")
    assert "EMBEDDING_PROVIDER=onnx" in (folder / "Dockerfile").read_text(encoding="utf-8")
    assert json.loads((folder / "release-manifest.json").read_text()) == one


def test_never_overwrite_preexisting_bundle(tmp_path):
    folder = tmp_path / "already"
    folder.mkdir()
    (folder / "important.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):
        prepare(folder)
    assert (folder / "important.txt").read_text() == "keep"


def test_source_list_is_explicitly_scoped():
    names = [p.as_posix() for p in tracked_sources()]
    assert len(names) >= 25
    assert not any(p.startswith(("tests/", "docs/", ".github/")) for p in names)
    assert not any(".env" in p for p in names)


def sample_space():
    return {
        "id": SPACE,
        "sha": "a" * 40,
        "sdk": "docker",
        "runtime": {
            "stage": "RUNNING",
            "hardware": {"current": "cpu-basic", "requested": "cpu-basic"},
        },
    }


def test_readonly_preflight_accepts_exact_existing_free_hardware():
    result = verify_space(sample_space(), "a" * 40)
    assert result["previous_sha"] == "a" * 40
    assert "NOT an entitlement" in result["note"]


@pytest.mark.parametrize(
    "change",
    [
        lambda d: d.update(id="someone-else/space"),
        lambda d: d.update(sha="b" * 40),
        lambda d: d.update(sdk="gradio"),
        lambda d: d["runtime"].update(stage="PAUSED"),
        lambda d: d["runtime"]["hardware"].update(current="cpu-upgrade"),
        lambda d: d["runtime"]["hardware"].update(requested="t4-small"),
    ],
)
def test_space_preflight_refuses_drift_or_paid_hardware(change):
    data = sample_space()
    change(data)
    with pytest.raises(ValueError, match="gate"):
        verify_space(data, "a" * 40)


def test_reject_invalid_revision():
    with pytest.raises(ValueError, match="40"):
        verify_space(sample_space(), "deadbeef")


def test_manual_workflow_has_no_automatic_deploy_triggers():
    from pathlib import Path

    workflow = (
        Path(__file__).parents[1] / ".github/workflows/manual-hf-space-release.yml"
    ).read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "  push:" not in workflow
    assert "  pull_request:" not in workflow
    assert "default: dry-run" in workflow
    assert "CONFIRM_EXISTING_CPU_BASIC_NO_CHARGE" in workflow
    assert "id-token: write" in workflow
    assert "spaces/Pracill/customer-support-rag-triage-agent" in workflow
    assert "--expected-current-sha" in workflow
    assert "--expected-provider onnx" in workflow


def test_deployed_revision_and_source_provenance_validation():
    from scripts.verify_hf_publish_result import verify_published

    sha = "b" * 40
    github_sha = "c" * 40
    manifest = {"space_id": SPACE, "source_sha": github_sha, "source_archive_sha256": "d" * 64}
    result = {
        "space_id": SPACE,
        "new_space_sha": sha,
        "github_source_sha": github_sha,
        "source_archive_sha256": "d" * 64,
    }
    observed = sample_space()
    with pytest.raises(ValueError, match="revision"):
        verify_published(observed, result, manifest)
    observed["sha"] = sha
    verify_published(observed, result, manifest)
    observed["runtime"]["hardware"]["current"] = "cpu-upgrade"
    with pytest.raises(ValueError, match="CPU Basic"):
        verify_published(observed, result, manifest)
