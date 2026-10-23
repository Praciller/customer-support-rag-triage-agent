# Pillow/FastEmbed reachability review — 2026-10-24

Status: **Unresolved security dependency risk. No exception granted.**
Related: [Issue #93](https://github.com/Praciller/customer-support-rag-triage-agent/issues/93) and [Slice F #89](https://github.com/Praciller/customer-support-rag-triage-agent/issues/89).

## Deployment-versus-CI difference

The public Hugging Face build paths, `Dockerfile.hf` and
`deploy/huggingface/Dockerfile.bundle`, both select Python 3.12 with
`APP_ENV=production`, `DEMO_MODE=true`, `MOCK_LLM_MODE=true`,
`ALLOW_PUBLIC_INGEST=false`, and **`EMBEDDING_PROVIDER=fastembed`**.
FastEmbed is initialized lazily by `src/retrieval/retriever.py`, but is used
for demo-index passages and incoming text queries when this provider is
selected. Its declared Pillow dependency is therefore present in the
production resolver graph even without an image-upload endpoint.

The GitHub `docker-smoke` workflow intentionally starts `Dockerfile.api`
with **`EMBEDDING_PROVIDER=hashing`**, to verify a deterministic,
network-independent 27-record index and seven-node graph. A passing
hashing smoke **does not** verify the FastEmbed model download, exact
runtime packages, image decoding transitive behavior, or the deployed
Hugging Face image. The independent live Space smoke reports current
behavior of the *previously deployed revision*, not the pending GitHub
source. See `docs/live-space-preflight-20261023.md`.

## Observed entry points and boundaries

| Entry or capability | Source-backed behavior | What it does **not** establish |
| --- | --- | --- |
| `POST /triage`, `/answer`, `/search-similar` | Strict JSON-compatible content types; Pydantic text fields, forbidden unknown fields, message and top-k bounds. Binary and multipart bodies are rejected by tests in `tests/test_public_text_only_boundary.py`. | Transitive native/ONNX/Pillow code cannot be reached in an unforeseen way. |
| `POST /ingest` | Outside local development it requires a matching `X-Admin-API-Key`; disabled by default, and the public Docker configurations explicitly set public ingestion off. | That a privately authenticated ingestion path is risk-free. |
| Demo initialization | Bundled JSON fixture, 27 bounded records indexed using the configured text embedder. | That importing or executing FastEmbed does not import or execute image-related code. |
| Optional `datasets` loader | `datasets.load_dataset` is lazily invoked via the authenticated ingestion flow or separate offline CLI; it is not needed to serve the bundled demo fixtures. | That optional dataset ingestion is hardened for arbitrary sources or safe to expose publicly. |
| Model artefacts and Python packages | The FastEmbed text ONNX model and Python wheels are external release inputs, resolved on build/startup. | That a green GitHub CI or an unchanged API surface proves deployed dependency safety. |

No direct `PIL` import or image decoder invocation was found in
`src/` at the time of review. This is a **source-level observation**,
not a whole-program reachability proof; Pillow may still be imported
or executed by dependencies and remains installed on the supported
FastEmbed path. No exploitation or compromise has been established.

## Automated drift checks

`tests/test_space_release_boundaries.py` asserts that both published
Hugging Face Docker build recipes retain reviewed demo/admin/provider
defaults and non-root execution, that the CI hashing smoke is recognized
as distinct from Space FastEmbed, and that a forced unsupported Pillow
override is absent. It is intentionally a *source regression guard*;
it does not perform a container vulnerability scan or certify production.

## Required remediation before a newer Space release

1. Await a **released** FastEmbed/Pillow-compatible dependency graph (not
   merely an open upstream PR). Do not force-install Pillow 13 with
   `--no-deps`, hide vulnerabilities, or silently switch embedding
   provider. Validate exact dependencies with a **strict** Python audit.
2. From the **exact reviewed GitHub SHA**, build the intended Hugging Face
   image, record source archive checksum and resolved installed packages,
   and verify its user/group, environment and administrative ingress gates.
3. Run the **FastEmbed** release image, not only the hashing CI smoke,
   through a deterministic 27-record initialization, synthetic seven-node
   triage, retrieval/citation checks, and the expected evaluation fixture.
   Verify unauthorized ingestion remains HTTP 403.
4. Verify immutable Space source revision, live behavior/UI and a working
   rollback to the pre-release Space revision. No deployment is authorized
   by this review; any risk exception requires separately explicit owner
   decision, documented scope, expiry, compensating controls and rollback.

Python advisory records are not a count of proven remote attack paths.
This review reduces ambiguity about exposure, **not** the unresolved
Pillow advisories or the manual accessibility/release gates.
