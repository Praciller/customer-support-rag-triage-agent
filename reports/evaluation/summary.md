# Deterministic Evaluation Summary

Generated: 2026-06-21T16:47:15.130308+00:00
Command: `python -m src.evaluation.evaluate_triage`
Mode: `deterministic_mock`
Dataset: Banking77-derived deterministic evaluation fixture
Sample size: 8

| Metric | Measured result |
| --- | ---: |
| Intent accuracy | 100.0% |
| Intent macro F1 | 100.0% |
| Urgency accuracy | 100.0% |
| Precision@5 | 37.5% |
| Recall@5 | 100.0% |
| MRR | 0.771 |
| nDCG@5 | 0.814 |
| Zero-result rate | 0.0% |
| Grounded response rate | 100.0% |
| Unsupported-claim rate | 0.0% |
| Workflow success rate | 100.0% |
| Fallback rate | 0.0% |
| Cache hit rate | 0.0% |
| Average latency | 9.1 ms |
| P50 / P95 latency | 7.9 / 13.5 ms |

## Failed examples

- None.

## Recommendations

- Expand the human-labeled fixture before treating these metrics as production evidence.
- Add reranking or metadata filters to improve precision@k.

## Method and limitations

- Retrieval relevance is defined by the expected mapped intent label.
- Generation and grounding use the deterministic mock provider; no external API is called.
- The small fixture is intended for reproducibility and regression detection, not an SLA.
