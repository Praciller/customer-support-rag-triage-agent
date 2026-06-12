# Evaluation Report

Offline evaluation uses the real Banking77-derived evaluation set and local retrieval.
LLM-dependent steps run in deterministic mock mode; no paid provider calls are made.

| Metric | Result |
| --- | ---: |
| Retrieval precision@5 | 90.0% |
| Retrieval recall@5 | 100.0% |
| Intent accuracy | 100.0% |
| Intent macro F1 | 100.0% |
| Urgency accuracy | 100.0% |
| Groundedness pass rate | 100.0% |
| Average latency | 4245.3 ms |
| Cache hit rate | 0.0% |
| Provider fallback rate | 0.0% |

These results measure this repository's deterministic baseline, not a production SLA.
