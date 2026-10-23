"""Source-level regression guard for the public Hugging Face Docker configurations.

These assertions protect reviewable defaults; they do not attest the live image,
its transitive dependency risk, or its Hugging Face settings/secrets.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPACE_DOCKERFILES = (
    "Dockerfile.hf",
    "deploy/huggingface/Dockerfile.bundle",
)


@pytest.mark.parametrize("dockerfile", SPACE_DOCKERFILES)
def test_public_space_build_keeps_demo_and_admin_boundary(dockerfile: str) -> None:
    content = (ROOT / dockerfile).read_text(encoding="utf-8")
    env = dict(
        re.findall(
            r"(?m)^\s*(APP_ENV|DEMO_MODE|MOCK_LLM_MODE|ALLOW_PUBLIC_INGEST|EMBEDDING_PROVIDER)=([^\s\\]+)",
            content,
        )
    )

    assert env == {
        "APP_ENV": "production",
        "DEMO_MODE": "true",
        "MOCK_LLM_MODE": "true",
        "ALLOW_PUBLIC_INGEST": "false",
        "EMBEDDING_PROVIDER": "fastembed",
    }, "Review any change to public Space security or embedding defaults separately"
    assert re.search(r"(?m)^RUN useradd\b.*\buser\b", content)
    assert re.search(r"(?m)^USER user\s*$", content)
    assert "requirements.production.txt" in content


def test_ci_hashing_smoke_is_not_misrepresented_as_space_fastembed() -> None:
    ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "--env EMBEDDING_PROVIDER=hashing" in ci
    for dockerfile in SPACE_DOCKERFILES:
        content = (ROOT / dockerfile).read_text(encoding="utf-8")
        assert "EMBEDDING_PROVIDER=fastembed" in content
    # CI hashing smoke is intentionally fast and offline. Deployment still
    # requires separate FastEmbed 27-record / seven-node release-image smoke.


def test_production_dependency_keeps_supported_fastembed_range() -> None:
    requirements = (ROOT / "requirements.production.txt").read_text(encoding="utf-8")
    assert re.search(r"(?m)^fastembed>=0\.7,<1\s*$", requirements)
    # Do not use a forced Pillow 13 pin or weaken the dependency resolver.
    assert not re.search(r"(?im)^\s*(?:pillow\s*[=>]|--no-deps\b)", requirements)
