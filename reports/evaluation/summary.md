# Deterministic Evaluation Summary

Generated: 2026-11-14T12:50:27.402550+00:00
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
| No-approved-policy cases | 8 / 8 |
| Manual-review routes | 8 / 8 |
| Proposals withheld | 10 / 10 |
| Workflow success rate | 100.0% |
| Fallback rate | 0.0% |
| Cache hit rate | 0.0% |
| Average latency | 7.2 ms |
| P50 / P95 latency | 6.1 / 10.5 ms |

## Failed examples

- None.

## Recommendations

- Expand the human-labeled fixture before treating these metrics as production evidence.
- Add reranking or metadata filters to improve precision@k.

## Method and limitations

- Retrieval relevance is defined by the expected mapped intent label.
- The default demo has no approved policy source; generated proposals are withheld and routed for
  human review.
- Policy-gate evaluation checks only structural statuses, references, and routing. It does not
  verify semantic entailment or policy correctness.
- The deterministic mock is used; no external API is called.
- The small fixture is intended for reproducibility and regression detection, not an SLA.
