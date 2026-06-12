# Requirements Audit

Audit date: June 12, 2026

| Area | Status | Evidence |
| --- | --- | --- |
| Real public dataset | Pass | 1,000 seeded samples from `mteb/banking77`; source and license documented |
| Data and indexing CLIs | Pass | Load, clean, document, embed, and Qdrant build commands execute |
| Local embeddings | Pass | `BAAI/bge-small-en-v1.5`, 384 dimensions |
| Qdrant | Pass | Docker service healthy; 1,000 points; filtered semantic search returns scores and metadata |
| LangGraph | Pass | Seven required nodes execute in order with durations and status |
| Provider routing | Pass | Gemini, Groq, Cerebras clients; task models, retry, fallback order, safe degradation |
| Cache | Pass | SQLite TTL cache checked before provider calls; disable switch tested |
| FastAPI | Pass | Seven required endpoints, validation, CORS, metadata, Swagger |
| Frontend | Pass | Overview, triage, search, trace, evaluation, dataset, and provider views |
| Evaluation | Pass | Retrieval, intent, macro F1, urgency, grounding, latency, cache, and fallback metrics |
| Docker Compose | Pass | API, frontend, and Qdrant build and run together |
| CI and tests | Pass | GitHub Actions; Pytest, Ruff, Vitest, TypeScript build, npm audit |
| Documentation | Pass | README, architecture, data, routing, Qdrant, workflow, evaluation, deployment, portfolio review |
| Security | Pass | `.env` ignored; keys stay backend-only and are not logged or returned |

## Verification Snapshot

- Backend: 15 tests passed; Ruff passed.
- Frontend: Vitest passed; production build passed; zero npm vulnerabilities.
- Evaluation: precision@5 90%, recall@5 100%, intent accuracy 100%, macro F1 100%,
  urgency accuracy 100%, groundedness 100% in deterministic mock mode.
- Runtime: API health `ok`, Qdrant health `ok`, Swagger HTTP 200, frontend HTTP 200.

## Residual Limitations

- Banking77 is intent data, not authoritative company policy.
- Provider catalogs and free-tier limits can change.
- Generated responses require human review.
- Browser automation verification depends on a working Codex Chrome Extension connection.
