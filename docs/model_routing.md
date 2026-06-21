# Model routing

## Demo route

When `DEMO_MODE=true` or `MOCK_LLM_MODE=true`, all four model-backed tasks use
`mock/mock-small`. No provider key is read and no external LLM request is made. The mock provider
uses deterministic rules and JSON outputs suitable for tests, CI, screenshots, and public demos.

## Optional provider route

| Task | Configured primary | Configured model variable |
| --- | --- | --- |
| Intent classification | Groq | `INTENT_MODEL_NAME` |
| Urgency detection | Groq | `URGENCY_MODEL_NAME` |
| Response generation | Gemini | `RESPONSE_MODEL_NAME` |
| Grounding check | Gemini | `GROUNDING_MODEL_NAME` |

`LLM_PROVIDER_PRIORITY` controls fallback order. Provider/model/task, prompt, context,
temperature, and token limit are hashed into the SQLite cache key. Each provider receives bounded
retries and timeout configuration. Exhaustion returns a safe manual-review response with
`fallback_used=true` and `degraded_mode=true`.

Model names and provider catalogs change. The values in `.env.example` are configuration defaults,
not availability guarantees. Keys stay in backend environment variables and are never returned by
`/provider-health`.
