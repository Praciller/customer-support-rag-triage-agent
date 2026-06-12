# Model Routing

| Task | Primary | Default model |
| --- | --- | --- |
| Intent classification | Groq | `llama-3.1-8b-instant` |
| Urgency detection | Groq | `llama-3.1-8b-instant` |
| Response generation | Gemini | `gemini-3.1-flash-lite` |
| Grounding check | Gemini | `gemini-3.1-flash-lite` |
| Provider fallback | Cerebras | `gpt-oss-120b` |

The router checks SQLite cache before each provider call, retries with bounded exponential
backoff, then advances through `LLM_PROVIDER_PRIORITY`. If no provider succeeds, it returns a
safe response with `degraded_mode=true`.

Model defaults were updated on June 12, 2026 because provider catalogs changed after the
original requirement was written. All IDs remain environment-configurable.
