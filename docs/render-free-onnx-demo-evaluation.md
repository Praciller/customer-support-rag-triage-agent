# Free Render demo: pinned ONNX retrieval and synthetic evaluation

This is a **portfolio demonstration**, not a service-level agreement, a
production bank support system, or an assessment of real LLM response quality.

## Currently verified deployment

- Static UI: https://customer-support-rag-triage-agent.onrender.com
- API: https://customer-support-rag-triage-api.onrender.com
- Existing **free** Render API service: `customer-support-rag-triage-api`
- Demo provider: `EMBEDDING_PROVIDER=onnx` using the pinned quantized
  `BAAI/bge-small-en-v1.5` model; `QDRANT_MODE=memory`
- `DEMO_MODE=true`, `MOCK_LLM_MODE=true`, `ALLOW_PUBLIC_INGEST=false`
- Index reboots from **27 synthetic fixtures**, never customer records.
  The Qdrant memory index and any local cache are ephemeral on Render Free.
- Readiness, all seven trace stages, mock grounding and citations, CORS
  connectivity, and anonymous ingestion HTTP 403 were verified against the
  live API after the `onnx`/Qdrant configuration updates on 2026-10-24.

## Reviewable deterministic evaluation

The committed `reports/evaluation/results.json` and `summary.md`
were **regenerated on 2026-10-24 with ONNX and memory Qdrant**, using
`python -m src.evaluation.evaluate_triage`. They contain exactly **8
synthetic evaluation queries**, 27 synthetic passages and a deterministic
mock provider, not a sampled production workload.

The evaluation report is a dated **local Windows/CPU experiment**. Its
latency measurements do not describe public Render hosting speed. Likewise,
workflow success on eight mock inputs is not model-grounding performance
on real support tickets. The limitations and evaluation mode are retained
alongside the scores.

For free/demo environments whose writable `EVAL_OUTPUT_PATH` is missing,
the API serves this **committed** report only when mode is demo+mock and
its embedding provider/model and fixture identity match. Render native builds
may omit the non-package `reports/` JSON directory entirely. A checked-in
`src/api/reviewed_onnx_report.py` resource contains the exact same dated
synthetic report, validated against the source JSON with a normalized
SHA-256 regression test. It is used only after report-file candidates
are missing or incompatible, and only if its ONNX provider/model and
fixture identity also match. It deliberately returns `not_evaluated`
for a non-demo environment, a provider mismatch or missing/invalid
fixture evidence. It never runs costly evaluations in the
unauthenticated HTTP request handler.

## Free-tier operational constraints

Render Free may spin down after inactivity, then take time to restore the
process and reload the pinned model. Local memory is capped at roughly
512 MiB; an observed fresh ONNX+Qdrant process used about **496 MB of the
537 MB byte limit**. Treat this as a capacity risk. Avoid concurrent heavy
requests and monitor service events for out-of-memory restarts. Do not
silently upgrade to paid hardware to solve it.

The historical Hugging Face Docker Space remains a **different
deployment** and is not changed by any Render evaluation report update.

## Reproduce the synthetic evaluation locally

In a Python 3.12 environment with project dependencies plus
`scikit-learn`:

```sh
export EMBEDDING_PROVIDER=onnx
export QDRANT_MODE=memory
export DEMO_MODE=true
export MOCK_LLM_MODE=true
export ALLOW_PUBLIC_INGEST=false
export LLM_CACHE_ENABLED=false
python -m src.evaluation.evaluate_triage
```

Any change to model weights/tokenizer, retrieval contract, corpus, mapped
intents or workflow should regenerate and review the report separately,
rather than reusing the previous scores.

See [Issue #89](https://github.com/Praciller/customer-support-rag-triage-agent/issues/89)
for separate Hugging Face release authorization and manual accessibility.
