# Customer Support RAG Triage Agent

A typed, inspectable RAG triage workflow that retrieves support evidence, drafts a response, checks grounding, and recommends a human action.

**[Open the live zero-key demo](https://pracill-customer-support-rag-triage-agent.hf.space/)**

![Ticket triage result](docs/screenshots/triage-result.png)

## Evidence-backed outcomes

- Runs a fixed seven-node LangGraph workflow with typed state and an inspectable per-node trace.
- Retrieves bounded Banking77-derived evidence from Qdrant with local BGE embeddings and stable, idempotent fixture IDs.
- Exposes provider, model, cache, fallback, degraded-mode, retrieval, grounding, and human-action metadata.
- Ships a zero-key deterministic review path plus a checked-in 8-ticket regression artifact. The fixture is evidence of reproducibility, not real-world model quality.

[![CI](https://github.com/Praciller/customer-support-rag-triage-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/Praciller/customer-support-rag-triage-agent/actions/workflows/ci.yml)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Zero-key demo](https://img.shields.io/badge/demo-zero--key-26735F)

## 30-second reviewer path

1. Open the [live demo](https://pracill-customer-support-rag-triage-agent.hf.space/) and run **Card not arrived**.
2. Read the decision, three retrieved cases, grounding state, and recommended human action.
3. Scan the complete 7/7 trace, then open Evaluation for the small deterministic fixture.
4. Review [architecture](docs/architecture.md), [evaluation methodology](docs/evaluation.md), and [security boundaries](docs/security.md).

This is a reviewable support decision workflow, not a generic chatbot or an autonomous customer-support replacement.

## Architecture

```mermaid
flowchart LR
  UI[React operations console] --> API[FastAPI]
  API --> G[Typed LangGraph workflow]
  G --> Q[Qdrant]
  Q --> E[Local BGE embeddings]
  G --> C[SQLite response cache]
  G --> R[Provider router]
  R --> M[Deterministic mock]
  R -. opt-in .-> P[Gemini / Groq / Cerebras]
```

The public demo bootstraps 27 bounded Banking77-derived records into Qdrant without duplicating existing stable IDs. Provider credentials remain backend-only and external providers are opt-in. See [the architecture contract](docs/architecture.md).

## Workflow stages

1. `normalize_message`
2. `classify_intent`
3. `detect_urgency`
4. `retrieve_similar_cases`
5. `generate_support_response`
6. `grounding_check`
7. `suggest_next_action`

Each successful node records duration, bounded input/output summaries, component, provider/model when applicable, cache/fallback/degraded flags, retrieval count, and grounding result. Empty retrieval or degraded generation cannot produce a grounded final result.

![Seven-node workflow trace](docs/screenshots/workflow-trace.png)

## Deterministic evaluation

Generated on July 19, 2026 with local `BAAI/bge-small-en-v1.5` FastEmbed embeddings, the mock provider, 27 indexed demo records, and 8 labeled evaluation tickets.

| Metric | Result |
| --- | ---: |
| Intent accuracy / macro F1 | 100.0% / 100.0% |
| Urgency accuracy | 100.0% |
| Precision@5 / Recall@5 | 37.5% / 62.5% |
| MRR / nDCG@5 | 0.771 / 0.611 |
| Zero-result rate | 0.0% |
| Mock grounding-verifier pass rate | 100.0% |
| Unsupported-claim flag rate | 0.0% |
| Workflow success rate | 100.0% |
| P50 / P95 local latency | 16.2 ms / 28.8 ms |

Recall and nDCG use the three known relevant fixture records per intent. These are deterministic regression results from a deliberately small, rules-aligned fixture. They are not production latency, policy correctness, semantic-entailment, or universal model-quality claims. See the [generated summary](reports/evaluation/summary.md) and [methodology](docs/evaluation.md).

### Public deployment smoke evidence

Verified July 19, 2026: `/ready` returned 200 and one live mock triage returned 3 retrieved cases, 7/7 completed trace nodes, a passing mock grounding check, and `ask_for_order_id`. Playwright found no browser warnings or errors. The deployed Evaluation view still serves an earlier June 21 artifact; the checked-in July 19 artifact above is the current local regression evidence. No redeploy was performed in this task.

![Evaluation dashboard](docs/screenshots/evaluation.png)

## Local quickstart

The primary review path uses deterministic mock generation and requires no provider key.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn src.api.main:app --reload --port 8000
```

In another terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open `http://localhost:5173`. The first FastEmbed run downloads the public BGE ONNX model. If a stale Hugging Face login interferes with that public download, run the command without an implicit token or use the hashing-based CI command below for a network-free workflow check.

### Docker alternative

```powershell
docker compose up --build
```

- Console: `http://localhost:5173`
- API docs: `http://localhost:8000/docs`
- Readiness: `http://localhost:8000/ready`
- Qdrant: `http://localhost:6333/dashboard`

## Testing and verification

```powershell
.venv\Scripts\ruff.exe check src tests
.venv\Scripts\ruff.exe format --check src tests
.venv\Scripts\python.exe -m pytest

cd frontend
npm run lint
npm test
npm run build
```

Reproduce the checked-in FastEmbed evaluation from the repository root:

```powershell
$env:DEMO_MODE="true"
$env:MOCK_LLM_MODE="true"
$env:QDRANT_MODE="memory"
$env:EMBEDDING_PROVIDER="fastembed"
$env:LLM_CACHE_ENABLED="false"
.venv\Scripts\python.exe -m src.evaluation.evaluate_triage
```

CI uses deterministic hashing embeddings to avoid model downloads while exercising the same graph, API, fixture, evaluation, and artifact-generation contracts.

## API review points

```powershell
curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/ready
curl.exe -X POST http://localhost:8000/triage -H "Content-Type: application/json" -d '{"message":"My card has not arrived","top_k":5}'
curl.exe -X POST http://localhost:8000/search-similar -H "Content-Type: application/json" -d '{"message":"I need a refund","top_k":5}'
curl.exe http://localhost:8000/eval/results
```

`/provider-health` reports the active mock routes in demo mode. External Gemini, Groq, and Cerebras routes remain configurable and opt-in; provider catalogs and quotas can change.

## Security and limitations

- Requests forbid extra fields and bound message length, `top_k`, confidence values, and ingestion batch size.
- Public ingestion is disabled; non-local ingestion requires `X-Admin-API-Key`.
- Provider keys stay server-side. Controlled errors omit stack traces, environment values, and local paths.
- Retrieved records are untrusted precedent, not company policy. The mock grounding check validates evidence presence and workflow behavior, not semantic entailment.
- Generated responses require human review. Prompt injection, policy authority, tenant isolation, distributed rate limiting, and sensitive-data retention require controls beyond this demo.
- The in-memory limiter and local Qdrant/SQLite state are single-process constraints. Free CPU hosts may cold-start or exceed memory limits.
- The public Space is manually synchronized and may lag this GitHub working tree.

See [security details](docs/security.md) and [deployment constraints](docs/deployment.md).

## Documentation

- [Architecture and node contracts](docs/architecture.md)
- [Deterministic demo mode](docs/demo_mode.md)
- [Model routing](docs/model_routing.md)
- [Data source and license](docs/data_source.md)
- [Evaluation methodology](docs/evaluation.md)
- [Qdrant lifecycle](docs/qdrant.md)
- [Deployment](docs/deployment.md)
- [Security](docs/security.md)
- [Operations runbook](docs/runbook.md)
- [Portfolio review](PORTFOLIO_REVIEW.md)

## Resume bullet

Built a zero-key, retrieval-grounded support triage workflow with typed LangGraph orchestration, Qdrant and local BGE embeddings, deterministic evaluation, provider fallback/cache controls, protected FastAPI endpoints, and a React evidence-and-trace console.
