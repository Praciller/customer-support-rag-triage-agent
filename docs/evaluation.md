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
- Recall@K: retrieved mapped-intent relevant records divided by the known relevant fixture records
  for that intent. The balanced demo fixture has three relevant records per intent.
- MRR: reciprocal rank of the first relevant result.
- nDCG@K: discounted binary mapped-intent gain divided by an ideal ranking built from the known
  relevant fixture count, capped at K.
- Workflow success: all seven nodes completed.
- Mock grounding-verifier pass rate: the deterministic verifier passed and the graph confirmed that
  retrieval was non-empty and generation was not degraded.

## Measured result: July 19, 2026

| Metric | Result |
| --- | ---: |
| Intent accuracy / macro F1 | 100.0% / 100.0% |
| Urgency accuracy / macro F1 | 100.0% / 100.0% |
| Precision@5 / Recall@5 | 37.5% / 62.5% |
| MRR / nDCG@5 | 0.771 / 0.611 |
| Zero-result rate | 0.0% |
| Grounded / unsupported claim | 100.0% / 0.0% |
| Degraded / fallback / cache hit | 0.0% / 0.0% / 0.0% |
| Workflow success | 100.0% |
| Average / P50 / P95 latency | 18.8 / 16.2 / 28.8 ms |

## Limitations

The fixture has one example per intent and rules intentionally aligned to those examples. Retrieval
relevance uses mapped intent rather than human policy judgment. Latency is a local snapshot. Mock
grounding checks evidence presence and deterministic workflow guards, not semantic entailment or
policy correctness. Mock results measure regression stability, not real-provider answer quality.
Optional real-provider evaluation must be run manually and never runs in normal CI.

The deployed public Evaluation view can lag the checked-in artifact because the Hugging Face Space
is synchronized manually. Deployment smoke evidence must be reported separately from this local
regression artifact and from any production-performance claim.
