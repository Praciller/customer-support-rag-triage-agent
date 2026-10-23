# Python image-decoding exposure assessment (2026-10-23)

Status: **partial static/HTTP assessment; Pillow remediation remains open**.
Tracking: [Issue #93](https://github.com/Praciller/customer-support-rag-triage-agent/issues/93).
Scope: the public, zero-key, text-only demo. This document does **not** approve a
risk exception, certify a transitive package, or claim the live Space uses GitHub main.

## Dependency and release distinction

- GitHub main at review: `57856353d9d094bd398058cd582036bd47cfbded`
  (PR #94). Exact-SHA post-merge CI:
  [run 39940513987](https://github.com/Praciller/customer-support-rag-triage-agent/actions/runs/39940513987).
- The compatible `datasets>=5.0.1,<6` and `fsspec>=2026.6.0,<2027`
  constraints removed the two reported advisories for those packages in CI.
  The scan still reported **35 Pillow advisory records**, not 35 proven exploits.
- `fastembed>=0.7,<1` currently resolves to a release requiring
  `Pillow<13`; the reported Pillow fixes require `Pillow>=13`.
  An attempted override failed package resolution; do not ignore declared
  FastEmbed requirements, suppress all advisories, or call the Python gate clean.
- Read-only live Hub metadata during this review showed Space revision
  `a2661562ff1a2a7b7f15e4b9145cb007c98444a5`, last updated September 2026.
  It is **not** proof that the live runtime has the main-branch dependency
  versions. Do not apply CI package-version claims to the Space image.

## Static public ingress review

| Surface | Observed behavior | Evidence in source |
| --- | --- | --- |
| `/triage`, `/answer` | Accept Pydantic JSON `message: str`, `top_k: int`; no upload/image parameter; unexpected keys forbidden | `src/api/main.py`, `src/api/schemas.py` |
| `/search-similar` | Same text-only model, optional intent string; no image upload route | `src/api/main.py`, `src/api/schemas.py` |
| `/ingest` | Requires configured admin key, except explicitly enabled local development/test ingestion; request only supports `recreate` and `sample_size` | `src/api/main.py`, `src/api/schemas.py` |
| Demo startup | Loads checked-in 27 text records; does not require downloading a dataset | `src/bootstrap/demo_data.py`, `src/api/services.py` |
| Embedding | Runtime FastEmbed wrapper instantiates `fastembed.TextEmbedding`, passing strings to `passage_embed`/`query_embed` | `src/retrieval/retriever.py` |
| Optional dataset import | `datasets.load_dataset` is imported only in `_load_huggingface`, on an authorized ingestion/offline acquisition path, not ordinary demo triage | `src/data/load_dataset.py`, `src/api/services.py` |

The repository's application code has no direct Pillow image-decoder call or
public image-upload endpoint in the inspected `src/` tree. A synthetic
live request for `/triage` completed all seven trace nodes, and unauthenticated
`/ingest` returned HTTP 403. The tests in
`tests/test_public_text_only_boundary.py` add regression guards for image-shaped
JSON keys and binary request bodies on the three text endpoints.

## Residual risk and limits

**Pillow remains installed in the production dependency graph.** The public
API is not currently designed to route image bytes to Pillow, which narrows
the apparent remote-image-decoding surface. This static review does not trace
every transitive import or image-related code path in FastEmbed, model
downloads, ONNX Runtime, dataset processing, or future changes. It also does
not establish whether every Pillow advisory is reachable or non-reachable.
Malformed model artifacts, trusted-asset handling, authorized/offline
ingestion, and dependency-chain behavior require separate dynamic analysis.

**No blanket risk acceptance.** Keep Issue #93 open; retain the visible Python
audit and do not declare dependency-security release readiness. Independently
verify the exact Docker/Windows/Space package graphs. Track supported FastEmbed
releases for Pillow 13, and re-enable a blocking clean Python audit only when
the resolved graph can pass it. If proposing a time-limited exception, obtain
explicit owner approval and record precise versions, exposure, controls,
expiration, and rollback before a release.

## Safe next verification

1. In an isolated, ephemeral CPU-only environment, record
   `python -m pip show fastembed Pillow datasets fsspec` and
   `python -m pip_audit --strict --requirement requirements.production.txt`.
2. Inspect FastEmbed transitive Pillow call paths and exercise text-only
   embeddings without user-provided image data; do not download paid models.
3. Repeat the live checks after a separately approved release and record
   the exact Space revision and image digest before updating portfolio images.
