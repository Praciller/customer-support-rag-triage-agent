# Requirements audit

Audit date: June 21, 2026

| Area | Status | Evidence |
| --- | --- | --- |
| Key-free demo | Pass | Demo/mock defaults; no provider keys required |
| Demo bootstrap | Pass | 27-record fixture, stable IDs, missing-only indexing, readiness metadata |
| Seven-node workflow | Pass | Typed LangGraph state and ordered trace |
| Retrieval | Pass | Local BGE FastEmbed plus Qdrant and bounded top-k |
| Evaluation | Pass | JSON, Markdown, confusion matrix, deterministic CI command |
| API hardening | Pass | Strict requests, limits, timeouts, controlled errors, configurable CORS |
| Ingestion protection | Pass | Disabled by default; constant-time admin key comparison |
| Rate limiting | Pass | Bounded in-memory limiter on triage/search/ingest |
| Frontend | Pass | Triage, search, trace, evaluation, dataset, provider, responsive views |
| CI | Pass | Ruff, Pytest, deterministic evaluation, ESLint, Vitest, TypeScript/Vite build |
| Docker Compose | Pass | No-key defaults, 27-record index, healthy Qdrant/API, working UI and triage |
| Hugging Face image | Pass | Non-root CPU image; UI, readiness, and seven-node triage verified on port 7860 |
| Screenshots | Pass | Eight reproducible desktop/mobile implementation captures |
| Documentation | Pass | Required architecture, routing, data, evaluation, deploy, security, demo, runbook docs |
| Public deployment | Pass | Public Hugging Face Space verified with API-connected UI, grounded retrieval, and seven trace nodes |

## Current measured snapshot

- Backend: 27 tests passed.
- Frontend: 4 tests passed; ESLint and production build passed.
- Evaluation: Precision@5 37.5%, Recall@5 100%, MRR 0.771, nDCG@5 0.814, intent
  accuracy/macro F1 100%, urgency accuracy 100%, workflow success 100%.
- Browser: desktop/mobile local flows and the public Hugging Face triage flow verified; public smoke
  returned 3 matches, 86% grounding, 7/7 trace nodes, and no final application console errors.

## Live deployment

https://pracill-customer-support-rag-triage-agent.hf.space/
