# Requirements audit

Audit date: July 19, 2026

| Area | Status | Evidence |
| --- | --- | --- |
| Key-free demo | Pass | Demo/mock defaults; no provider keys required |
| Demo bootstrap | Pass | 27-record fixture, stable IDs, missing-only indexing, readiness metadata |
| Seven-node workflow | Pass | Typed LangGraph state and ordered trace |
| Retrieval | Pass | Local BGE FastEmbed plus Qdrant and bounded top-k |
| Evaluation | Pass | Corrected standard Recall@5/nDCG@5, JSON, Markdown, confusion matrix, deterministic CI command |
| API hardening | Pass | Strict requests, bounded confidences, limits, timeouts, controlled errors, configurable CORS |
| Ingestion protection | Pass | Disabled by default; constant-time admin key comparison |
| Rate limiting | Pass | Bounded in-memory limiter on triage/search/ingest |
| Frontend | Pass | Truthful API state, labeled controls, triage, search, trace, evaluation, dataset, provider, responsive views |
| CI | Pass | Ruff lint/format, Pytest, deterministic evaluation, ESLint, Vitest, TypeScript/Vite build |
| Docker Compose | Pass | No-key defaults, 27-record index, healthy Qdrant/API, working UI and triage |
| Hugging Face image | Pass | Non-root CPU image; UI, readiness, and seven-node triage verified on port 7860 |
| Screenshots | Pass | Eight reproducible desktop/mobile implementation captures |
| Documentation | Pass | Required architecture, routing, data, evaluation, deploy, security, demo, runbook docs |
| Public deployment | Pass | Public Hugging Face Space verified with API-connected UI, grounded retrieval, and seven trace nodes |

## Current measured snapshot

- Backend: 30 tests passed; Ruff lint and format checks passed.
- Frontend: 6 tests passed; ESLint and production build passed.
- Evaluation: Precision@5 37.5%, Recall@5 62.5%, MRR 0.771, nDCG@5 0.611, intent
  accuracy/macro F1 100%, urgency accuracy 100%, workflow success 100%.
- Browser: public desktop/mobile flows verified; public smoke returned 3 matches, 7/7 trace nodes,
  and no browser warnings or errors. The public Evaluation view still serves the earlier June 21
  artifact and was not redeployed during this audit.

## Live deployment

https://pracill-customer-support-rag-triage-agent.hf.space/
