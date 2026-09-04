# Deployment

## Docker Compose

```powershell
docker compose up --build
```

The command requires no `.env` file. Compose defaults to demo/mock mode, blocks public ingestion,
loads FastEmbed on CPU, starts Qdrant, waits for `/ready`, and then starts the React console.

```powershell
Invoke-RestMethod http://localhost:8000/ready
Invoke-RestMethod http://localhost:8000/triage -Method Post `
  -ContentType application/json `
  -Body '{"message":"My card has not arrived","top_k":5}'
```

## Hugging Face Spaces CPU

Live demo: https://pracill-customer-support-rag-triage-agent.hf.space/

`Dockerfile.hf` is the canonical single-container image. It builds the React app, installs only
production Python dependencies, serves UI and API from FastAPI on port 7860, uses a non-root user,
and writes embedded Qdrant/SQLite data under `/tmp`.

Repository-side verification:

```powershell
docker build -f Dockerfile.hf -t support-rag-hf .
docker run --rm -p 7860:7860 support-rag-hf
```

The existing Docker Space runs on `cpu-basic`. No secret is required for demo mode. A deployment is
only considered verified after the live UI loads, `/ready` returns 200, and a live deterministic
triage request returns seven trace nodes.

### Current verified deployment — September 5, 2026

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
- FastEmbed BGE model with batch size 8.
- CPU-only production dependencies; no CUDA packages.
- No paid database, vector service, or LLM required.
- Embedded Qdrant and SQLite are ephemeral on free hosts unless persistent storage is added.

Free hosts can still exceed RAM or cold-start limits while loading the embedding model. Do not
claim a live deployment from a successful image build alone.
