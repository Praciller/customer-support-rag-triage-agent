# Inference routing

## Public route

The public implementation uses one deterministic local route for all four inference-backed tasks:

| Task | Route | Model label |
| --- | --- | --- |
| Intent classification | local | `deterministic-small` |
| Urgency detection | local | `deterministic-small` |
| Response generation | local | `deterministic-small` |
| Grounding check | local | `deterministic-small` |

No external model account, API key, or network inference call is required. The deterministic generator returns bounded JSON outputs suitable for tests, CI, screenshots, regression fixtures, and the public demo.

## Cache and fallback behavior

The router retains the same cache and fallback contracts used by the workflow. Route/model/task, prompt, context, temperature, and token limit are hashed into the SQLite cache key. A failed local generation can return the existing safe manual-review response with `fallback_used=true` and `degraded_mode=true`.

`/provider-health` exposes only operational metadata for the active local route, cache state, embeddings, vector store, and ingestion boundary. It does not expose credentials because the public inference path does not require any.

## Evaluation boundary

The deterministic route is intended for reproducible portfolio evaluation. Its checked-in metrics demonstrate workflow and retrieval behavior on a small rules-aligned fixture; they are not evidence of production language-model quality or policy correctness.
