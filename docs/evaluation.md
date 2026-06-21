# Deterministic evaluation

## Reproduce

```powershell
$env:DEMO_MODE="true"
$env:MOCK_LLM_MODE="true"
$env:QDRANT_MODE="memory"
$env:EMBEDDING_PROVIDER="fastembed"
$env:LLM_CACHE_ENABLED="false"
$env:EVAL_OUTPUT_PATH="reports/evaluation/results.json"
.venv\Scripts\python.exe -m src.evaluation.evaluate_triage
```

Artifacts:

- `reports/evaluation/results.json`
- `reports/evaluation/summary.md`
- `reports/evaluation/confusion_matrix.json`

## Fixture and definitions

The evaluation uses 8 labeled tickets from `data/eval/eval_set.csv`, 27 indexed demo records,
local `BAAI/bge-small-en-v1.5` embeddings, and the deterministic mock provider.

- Intent/urgency accuracy: exact label match.
- Macro F1: unweighted F1 across observed labels.
- Precision@K: relevant mapped-intent results divided by K.
- Recall@K: whether at least one mapped-intent relevant result appears in K.
- MRR: reciprocal rank of the first relevant result.
- nDCG@K: discounted gain over binary mapped-intent relevance.
- Workflow success: all seven nodes completed.
- Grounded response rate: mock grounding verifier passed with retrieved context.

## Measured result: June 21, 2026

| Metric | Result |
| --- | ---: |
| Intent accuracy / macro F1 | 100.0% / 100.0% |
| Urgency accuracy / macro F1 | 100.0% / 100.0% |
| Precision@5 / Recall@5 | 37.5% / 100.0% |
| MRR / nDCG@5 | 0.771 / 0.814 |
| Zero-result rate | 0.0% |
| Grounded / unsupported claim | 100.0% / 0.0% |
| Degraded / fallback / cache hit | 0.0% / 0.0% / 0.0% |
| Workflow success | 100.0% |
| Average / P50 / P95 latency | 15.8 / 11.0 / 40.2 ms |

## Limitations

The fixture has one example per intent and rules intentionally aligned to those examples. Retrieval
relevance uses mapped intent rather than human policy judgment. Latency is a local snapshot. Mock
results measure regression stability, not real-provider answer quality. Optional real-provider
evaluation must be run manually and never runs in normal CI.
