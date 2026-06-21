# Runbook

## Health checks

```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/ready
Invoke-RestMethod http://localhost:8000/dataset-info
Invoke-RestMethod http://localhost:8000/provider-health
```

`/health` confirms process liveness and reports dependencies. `/ready` returns 503 until the demo
index is complete.

## Common failures

### Readiness remains 503

Inspect the `index.error_category` field from `/health`. Verify the fixture path is readable, the
Qdrant target is writable/reachable, and `QDRANT_VECTOR_SIZE` matches the embedding model.

### Free host exits while loading embeddings

Confirm `EMBEDDING_PROVIDER=fastembed`, `EMBEDDING_BATCH_SIZE=8`, CPU-only requirements, and the
27-record fixture. A 512 MB host may still be insufficient; use a larger genuinely free CPU tier or
keep the demo local rather than enabling billing.

### Frontend reports API errors

Check `/ready`, `VITE_API_URL`, and `CORS_ORIGINS`. Same-container production uses a blank
`VITE_API_URL`; local Compose uses `http://localhost:8000`.

### Evaluation artifact unavailable

Run `python -m src.evaluation.evaluate_triage` with demo/mock mode, then confirm
`reports/evaluation/results.json` exists and `EVAL_OUTPUT_PATH` points to it.

### Rate limited

Respect `Retry-After`. Limits reset in memory and are lost on restart. Do not raise public limits
without reviewing host capacity.

## Verification sequence

1. Run Ruff and backend tests.
2. Run ESLint, Vitest, and the frontend production build.
3. Run deterministic evaluation.
4. Build/start Compose and wait for `/ready`.
5. Smoke test triage, search, evaluation, and blocked ingestion.
6. Load the UI at desktop and mobile widths; confirm no browser console errors.
