# Deployment

## Current public demo — Render (verified October 25, 2026 ICT)

- **Frontend:** https://customer-support-rag-triage-agent.onrender.com/
- **API:** https://customer-support-rag-triage-api.onrender.com/ready
- **Evaluation:** https://customer-support-rag-triage-api.onrender.com/eval/results
- **Source:** protected GitHub `main` SHA `a45a9abaae2881bbf14133f981c317206fa7e65c` ([5/5 post-merge CI](https://github.com/Praciller/customer-support-rag-triage-agent/actions/runs/40120551076)).
- **Deployment:** existing Render free API, `EMBEDDING_PROVIDER=onnx`, `QDRANT_MODE=memory`, synthetic/demo mock routing, public ingestion disabled; 27/27 indexed, seven-stage grounded synthetic triage and anonymous ingestion HTTP 403 verified live.
- **Evaluation:** the API serves the committed eight-case synthetic ONNX report generated on October 24, 2026. Scores do **not** measure real-customer accuracy or live Render latency.

The Render memory index is ephemeral, so restarts/cold starts re-index the demo. Memory headroom is narrow on the free tier; do not silently upgrade to paid resources. See [the full Render evidence guide](render-free-onnx-demo-evaluation.md).

## Docker Compose

```powershell
docker compose up --build
```

The command requires no `.env` file. Compose defaults to demo/mock mode, blocks public ingestion,
loads pinned ONNX BGE-small on CPU, starts Qdrant, waits for `/ready`, and then starts the React console.

```powershell
Invoke-RestMethod http://localhost:8000/ready
Invoke-RestMethod http://localhost:8000/triage -Method Post `
  -ContentType application/json `
  -Body '{"message":"My card has not arrived","top_k":5}'
```

## Hugging Face Spaces CPU — historical Space, release on hold

Legacy Hugging Face Space (not the current recommended demo): https://pracill-customer-support-rag-triage-agent.hf.space/

This Space still has the old revision described below; newer GitHub/Render security fixes have **not** been deployed to it. Do not call it the current secure production version. Updates require an authorized owner-scoped publisher and independent verification of no-charge existing Docker Space rebuild eligibility. See [the manual release gate](hf-existing-space-manual-release.md) and [Issue #89](https://github.com/Praciller/customer-support-rag-triage-agent/issues/89).

`Dockerfile.hf` is the canonical single-container image. It builds the React app, installs only
production Python dependencies, serves UI and API from FastAPI on port 7860, uses a non-root user,
and writes embedded Qdrant/SQLite data under `/tmp`.

Repository-side verification:

```powershell
docker build -f Dockerfile.hf -t support-rag-hf .
docker run --rm -p 7860:7860 support-rag-hf
```

For a **repeatable pinned-ONNX image smoke**, run
[`scripts/verify_local_onnx.py`](../scripts/verify_local_onnx.py)
after starting the container; CI also builds the exact reviewed Docker bundle and
runs the real ONNX 27-record / seven-node synthetic smoke with blocking installed-image vulnerability audits. This does **not** authorize deployment to Hugging Face. Older FastEmbed-specific evidence remains [historical](local-fastembed-smoke-20261024.md).

The existing Docker Space runs on `cpu-basic`. No secret is required for demo mode. A deployment is
only considered verified after the live UI loads, `/ready` returns 200, and a live deterministic
triage request returns seven trace nodes.

### Historical Hugging Face verification — September 5, 2026

- GitHub source SHA: `11df5035e3f4f96b78b21f5c1d993bb6d6deaaba`.
- Current Space revision: `a2661562ff1a2a7b7f15e4b9145cb007c98444a5`.
- Previous healthy rollback revision: `255b7272544c9222e1fde5351598779049615162`.
- Bundle SHA256: `86eeb7f69fede2be2d2f7ba3cf65a98feb24e18e3fb6b0f484737ed8de9ab123`.
- `/ready`: HTTP 200, demo mode active, 27 indexed records ready; hardware `cpu-basic`.
- Triage: HTTP 200, 3 retrieval matches, grounded score 0.86, 7/7 trace nodes, `ask_for_order_id`, no fallback or degraded state.
- Public ingestion: HTTP 403.
- Evaluation: deterministic fixture, 8 labeled tickets, Precision@5 37.5%, Recall@5 62.5%, MRR 0.771, nDCG@5 0.611, with the explicit not-production-SLA limitation.
- Browser: live HF UI verified at 1440px and 390px without page overflow; mobile hierarchy passed; no application console or page errors.

Rollback with `git revert a2661562ff1a2a7b7f15e4b9145cb007c98444a5` followed by `git push origin main`; do not force-push.

Historical verification — July 26, 2026 at 14:43 ICT:

- GitHub governed release: `ac196bddb75527f5d719ca5bbb0775b30700ff49`.
- GitHub synchronized revision, including the mobile Evaluation containment fix:
  `81baa5f727da21e9cd1577ebc4131ace2fbf2b37`.
- Previous Space revision: `1c83ba447b23ff61a0f686816176e580e83ba0a0`.
- Final Space revision: `255b7272544c9222e1fde5351598779049615162`.
- `/ready`: HTTP 200, demo mode active, 27 indexed records ready.
- Triage: 3 retrieval matches, 7/7 trace nodes, grounded score 0.86, `ask_for_order_id`, no fallback
  or degraded state.
- Public ingestion: HTTP 403.
- Evaluation: Precision@5 37.5% (38% displayed), Recall@5 62.5% (63% displayed), MRR 0.771, and
  nDCG@5 0.611 from 8 labeled tickets.
- Browser: 1440-pixel desktop and 390-pixel mobile passed without page-level overflow; the console
  reported no warnings or errors.

This is a single-ticket deployment smoke result, separate from the deterministic evaluation report.

### GitHub and Space synchronization

Before a release, run the non-deploying public-Space preflight in
[`scripts/verify_live_space.py`](../scripts/verify_live_space.py) and consult
[`docs/live-space-preflight-20261023.md`](live-space-preflight-20261023.md).
The preflight records **current Space health and revision only**; it does not
establish a reviewed GitHub source SHA to live-image mapping.

The Space is a separate Hugging Face Git repository and is updated manually; pushing GitHub does
not rebuild it automatically. `Dockerfile.hf` is the canonical source build. The verified Space
pull requests used `deploy/huggingface/Dockerfile.bundle` plus an `app.tar.gz` generated from exact,
reviewed GitHub squash commits. A reproducible bundle after committing is:

```powershell
git archive --format=tar.gz --output=app.tar.gz HEAD src frontend prompts data/demo data/eval reports/evaluation requirements.production.txt
```

Upload `app.tar.gz` with `deploy/huggingface/Dockerfile.bundle` renamed to `Dockerfile`, or clone the
Space and copy the GitHub repository with `Dockerfile.hf` renamed to `Dockerfile`.

## Resource controls

- 27-record startup fixture; no full dataset download.
- Pinned ONNX BGE-small embeddings with bounded batch size (current GitHub and Render demo).
- CPU-only production dependencies; no CUDA packages.
- No paid database, vector service, or LLM required.
- Embedded Qdrant and SQLite are ephemeral on free hosts unless persistent storage is added.

Free hosts can still exceed RAM or cold-start limits while loading the embedding model. Do not
claim a live deployment from a successful image build alone.


## Local Compose isolation

Compose is a development/review deployment rather than an internet-facing production configuration.
Its React, API, and Qdrant host ports are explicitly bound to `127.0.0.1`, so they are
accessible from the local machine but not published on every network interface. The
unused host-side Qdrant gRPC port (6334) is not exposed; the API still reaches Qdrant
over Compose's private service network. The checked-in `data` and `reports` mounts
are read-only in this review deployment. Ingestion in this configuration is intentionally
disabled; an authorized writable ingestion deployment needs its own explicit data volume.

The API image runs as non-root UID 10001 and owns its internal SQLite/cache
directories. Its HOME/XDG cache path is `/home/appuser/.cache`, mounted from the named
`model_cache` volume. The previous root-owned `huggingface_cache` volume is no longer
referenced; do not remove old Docker volumes until their contents are reviewed.

GitHub Actions also builds this Docker image, checks the numeric UID and writable cache,
and performs a key-free API smoke against in-memory Qdrant and hashing embeddings with
read-only fixture mounts. This isolated smoke does not exercise the FastEmbed model download,
Compose networking, or the external Qdrant service. These defaults are not substitutes for authentication, TLS, network
policies, or a hardened multi-tenant production deployment.

Run `docker compose config --quiet` before building to validate Compose syntax.


## 2026-10-24 pinned-ONNX production image (deployed on Render, not on Hugging Face)

The verified GitHub and Render release removes FastEmbed from both production Docker
recipes and uses the **same Qdrant BGE-small quantized ONNX model**, pinned
at revision `aa8f8b060edb00e03bfdd08813a2949946c8ba55`.
This supersedes the **local release-candidate** FastEmbed instructions above;
the earlier public Space remains the historical FastEmbed build until a
separate authorized deployment is verified.

The verified production-image CI enforces a strict, exception-free Python dependency
audit. The prior Pillow exception baseline was removed, not waived. The latest
pinned-ONNX regression covers 27 synthetic records, 8 evaluation queries and
retrieval top-5 ranking, documented in [the ONNX security review](onnx-bge-security-candidate-20261024.md).

For a new **local** ONNX release-image verification:

```powershell
docker build -f Dockerfile.hf -t csrta-onnx-review .
docker run --rm --name csrta-onnx-review -p 127.0.0.1:17860:7860 csrta-onnx-review
# In another terminal, only when /ready is ready:
python scripts/verify_local_onnx.py
```

The verifier sends only synthetic data, checks strict provider/trace/grounding
contracts, and checks unauthenticated ingestion returns 403. Do **not** use
this as proof of the installed image dependency versions, human accessibility
review, production Hugging Face provenance or rollback. No paid build or
deployment is authorized by these commands.
