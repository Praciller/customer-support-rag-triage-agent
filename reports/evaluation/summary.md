# Deterministic Evaluation Summary

Generated: 2026-10-24T16:59:56.670459+00:00
Command: `python -m src.evaluation.evaluate_triage`
Mode: `deterministic_mock`
Dataset: Banking77-derived deterministic evaluation fixture
Sample size: 8
Retrieval corpus: 27 records
Embeddings: `onnx` / `BAAI/bge-small-en-v1.5`

| Metric | Measured result |
| --- | ---: |
| Intent accuracy | 100.0% |
| Intent macro F1 | 100.0% |
| Urgency accuracy | 100.0% |
| Precision@5 | 37.5% |
| Recall@5 | 62.5% |
| MRR | 0.771 |
| nDCG@5 | 0.611 |
| Zero-result rate | 0.0% |
| Mock grounding-verifier pass rate | 100.0% |
| Unsupported-claim rate | 0.0% |
| Workflow success rate | 100.0% |
| Fallback rate | 0.0% |
| Cache hit rate | 0.0% |
| Average latency | 9.4 ms |
| P50 / P95 latency | 8.4 / 13.7 ms |

## Failed examples

- None.

## Recommendations

- Expand the human-labeled fixture before treating these metrics as production evidence.
- Add reranking or metadata filters to improve precision@k.

## Method and limitations

- Retrieval relevance is defined by the expected mapped intent label.
- Generation and grounding use the deterministic mock provider plus graph evidence guards;
  no external API is called.
- The small fixture is intended for reproducibility and regression detection, not an SLA.
