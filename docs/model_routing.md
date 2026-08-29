# Inference routing

## Default deterministic route

Demo mode and mock mode use one deterministic local route for all four inference-backed tasks:

| Task | Default route | Model label |
| --- | --- | --- |
| Intent classification | local | `deterministic-small` |
| Urgency detection | local | `deterministic-small` |
| Response generation | local | `deterministic-small` |
| Grounding check | local | `deterministic-small` |

No external model account, API key, or network inference call is required for tests, CI, screenshots, regression fixtures, or the public demo.

## Generic external GenAI route

The repository also preserves a vendor-neutral external GenAI adapter. It becomes active only when all three conditions are true:

- `DEMO_MODE=false`
- `MOCK_LLM_MODE=false`
- `EXTERNAL_LLM_URL` is non-empty

Optional server-side settings are `EXTERNAL_LLM_API_KEY` and `EXTERNAL_LLM_MODEL`. The endpoint credential is never returned to the browser or by `/provider-health`.

The configured endpoint receives an HTTP `POST` JSON body with this neutral contract:

```json
{
  "task": "generate_response",
  "workflow_instructions": "bounded task instructions",
  "user_ticket": "current customer ticket",
  "candidate_response": "candidate response when grounding is checked",
  "evidence": [
    {
      "reference_id": "case-123",
      "content": "retrieved evidence",
      "intent": "billing_issue",
      "prior_response": "synthetic prior response",
      "source": "public_dataset"
    }
  ],
  "model": "general",
  "temperature": 0.2,
  "max_output_tokens": 512
}
```

It must return a JSON object containing a non-empty `text` field and may return a `model` field:

```json
{
  "text": "generated result",
  "model": "remote-model-label"
}
```

If `EXTERNAL_LLM_API_KEY` is set, the adapter sends it as a server-side bearer token. The public repository does not prescribe which inference service implements this endpoint.

## Cache, retry, and fallback behavior

Route/model/task, workflow instructions, user ticket, candidate response, typed evidence, temperature, and token limit are hashed into the SQLite cache key. The existing retry and exponential-backoff settings apply to external calls. When external inference is active, the route order is `external` then deterministic `mock`; exhaustion can still return the safe manual-review response with `fallback_used=true` and `degraded_mode=true`.

The external adapter receives evidence as a dedicated data array. It does not receive a system/developer role assignment for retrieved content, and the workflow rejects provider evidence references that are not present in the retrieved array.

When demo/mock mode is active, the route order is local-only, so configuration of an external endpoint cannot accidentally make the public demo perform a network inference call.

`/provider-health` exposes whether external inference is configured and active, plus operational cache, embedding, vector-store, and ingestion metadata. It does not expose the endpoint URL or credential.

## Evaluation boundary

The checked-in metrics use the deterministic route. They demonstrate workflow and retrieval behavior on a small rules-aligned fixture; they are not evidence of production language-model quality or policy correctness. External GenAI behavior requires a separate controlled evaluation before any production claim.
