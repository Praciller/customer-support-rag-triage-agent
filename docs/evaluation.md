# Evaluation

`evaluate_retrieval.py` measures intent-label precision and recall from Qdrant results.
`evaluate_triage.py` measures intent accuracy, macro F1, urgency accuracy, groundedness,
latency, cache hits, provider usage, and fallback rate.

Run evaluation with `MOCK_LLM_MODE=true` to avoid external API calls:

```powershell
python -m src.evaluation.evaluate_triage
```

The checked-in report represents the deterministic baseline and is not a production SLA.
