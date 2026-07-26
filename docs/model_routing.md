# Model routing

## Demo route

When `DEMO_MODE=true` or `MOCK_LLM_MODE=true`, all four model-backed tasks use
`mock/mock-small`. No provider key is read and no external LLM request is made. The mock provider
uses deterministic rules and JSON outputs suitable for tests, CI, screenshots, and public demos.
`/provider-health` reports these active mock routes rather than the dormant external configuration.

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

The defaults were reviewed against official provider documentation on July 19, 2026. Gemini uses
[`gemini-3.1-flash-lite`](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite)
with `gemini-3.5-flash` fallback. Groq uses `openai/gpt-oss-20b` with
`openai/gpt-oss-120b` fallback because [Groq announced an August 16, 2026
shutdown](https://console.groq.com/docs/deprecations) for the previous Llama 3.1 8B and Llama 3.3
70B defaults. Cerebras uses [`gpt-oss-120b`](https://inference-docs.cerebras.ai/api-reference/models/public-models).
Availability, permissions, and free quotas still require live account verification.
