# Python production dependency security

## Candidate remediation — 2026-10-24

The new proposed Hugging Face Docker recipe and `requirements.production.txt`
use a **pinned direct ONNX Runtime** implementation of the existing
`BAAI/bge-small-en-v1.5` embedding model instead of FastEmbed. The exact
Qdrant model snapshot revision is hardcoded in
`src/retrieval/onnx_bge.py` (`aa8f8b060edb00e03bfdd08813a2949946c8ba55`).
It uses the same tokenizer, CLS pooling and L2 normalization as
FastEmbed 0.9.0. It supports text-only input and 384-dimensional vectors.

Strict `pip-audit==2.10.1` of the candidate production dependency graph
passed with **zero known advisories** on Windows Python 3.12
(October 24, 2026); neither `fastembed` nor `pillow` resolved. This does
**not** attest a future image, eliminate unknown vulnerabilities, or certify
production.

The previous baseline of 37 unresolved Pillow advisories was **removed**:
the production CI gate now fails on *any* resolved dependency advisory, with
no exceptions or `continue-on-error`. The old baseline and special comparison
script are no longer used. No `--no-deps`, package override, or security
waiver was applied.

## Reproduce

```sh
python -m pip install pip-audit==2.10.1
python -m pip_audit --strict --requirement requirements.production.txt --progress-spinner off
python -m pytest tests/test_onnx_bge.py tests/test_space_release_boundaries.py
# Opt-in only: separately install legacy fastembed to compare, never in production:
python scripts/verify_onnx_equivalence.py
```

The equivalence test checks 27 bundled synthetic passages and 8 evaluation
queries, 384-d output, maximum vector difference and retrieval top-5
ranking against the previous FastEmbed behavior. FastEmbed is an
**independent development-only benchmark prerequisite**, not a production
requirement.

## Remaining deployment gates

Build the exact production container, audit the **installed image** rather
than only dependency resolution, run the pinned model/27-record index,
seven-node triage and citation-integrity tests, verify public ingestion
denial, and complete manual screen-reader/zoom QA. Finally secure a
write-authorized Hugging Face deployment path and record exact GitHub
source checksum, Space revision and rollback evidence. The historical
public Space still uses its previous deployment until separately released.

See [Issue #89](https://github.com/Praciller/customer-support-rag-triage-agent/issues/89).
