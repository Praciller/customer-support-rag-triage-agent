"""Source-only guard for manual, parent-locked Hugging Face commit operations."""

import pytest

from scripts.prepare_hf_release import prepare
from scripts.publish_existing_hf_space import FILES, make_operations, validate_bundle


def test_publish_manifest_matches_repo_and_bundle_sha(tmp_path):
    folder = tmp_path / "release"
    manifest = prepare(folder)
    verified = validate_bundle(folder, manifest["source_sha"])
    assert verified == manifest
    assert [o.path_in_repo for o in make_operations(folder)] == list(FILES)


def test_publish_fails_closed_on_source_drift(tmp_path):
    folder = tmp_path / "release"
    data = prepare(folder)
    with pytest.raises(ValueError, match="SHA"):
        validate_bundle(folder, "f" * 40)
    (folder / "app.tar.gz").write_bytes(b"corrupted")
    with pytest.raises(ValueError, match="digest"):
        validate_bundle(folder, data["source_sha"])


def test_publish_rejects_extra_files(tmp_path):
    folder = tmp_path / "release"
    data = prepare(folder)
    (folder / ".env").write_text("should_not_upload", encoding="utf-8")
    with pytest.raises(ValueError, match="four"):
        validate_bundle(folder, data["source_sha"])


def test_publish_source_never_creates_repo_or_changes_hardware():
    from pathlib import Path

    source = (Path(__file__).parents[1] / "scripts/publish_existing_hf_space.py").read_text(
        encoding="utf-8"
    )
    assert "parent_commit=args.expected_current_sha" in source
    assert 'revision="main"' in source
    assert "api.create_repo" not in source
    assert "request_space_hardware" not in source
    assert "api.create_commit" in source
