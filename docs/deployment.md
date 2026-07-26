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

Upload the repository to a Docker Space and select free CPU hardware. No secret is required for
demo mode. A deployment is only considered verified after the live UI loads, `/ready` returns 200,
and a live deterministic triage request returns seven trace nodes.

Verified July 19, 2026: `/ready` returned 200 and the public free-CPU Space returned 3 retrieval
matches, a passing mock grounding check, `ask_for_order_id`, and all 7 trace nodes. Playwright found
no browser warnings or errors. This is a single-ticket deployment smoke result, separate from the
deterministic evaluation report.

The deployed Evaluation view still served the earlier June 21 artifact during that check. The
repository's July 19 artifact contains corrected Recall@5 and nDCG@5 calculations. The Space is not
claimed current until an explicitly approved manual synchronization and repeat smoke test occur.

### GitHub and Space synchronization

The Space is a separate Hugging Face Git repository and is updated manually; pushing GitHub does
not rebuild it automatically. `Dockerfile.hf` is the canonical source build. The current browser
upload used `deploy/huggingface/Dockerfile.bundle` plus an `app.tar.gz` generated from reviewed,
tracked source files. A reproducible bundle after committing is:

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
