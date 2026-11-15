# Inference routing

## Default deterministic route

Demo and mock modes use one local deterministic provider for intent classification, urgency
detection, and proposal generation:

| Task | Default route | Model label |
| --- | --- | --- |
| Intent classification | local | `deterministic-small` |
| Urgency detection | local | `deterministic-small` |
| Proposal generation | local | `deterministic-small` |

Policy review is a separate backend gate, not a model task. The public demo has no approved policy
references and no verifier configured, so generated proposals are withheld. The provider cannot
mark its own output as allowed, grounded, or policy-checked. Similar past cases are not passed to
proposal generation as policy evidence.

No external model account, API key, or network inference call is required for tests, CI,
screenshots, regression fixtures, or the public demo.

## Generic external GenAI route

The repository preserves a vendor-neutral external GenAI adapter. It becomes active only when all
three conditions are true:

- `DEMO_MODE=false`
- `MOCK_LLM_MODE=false`
- `EXTERNAL_LLM_URL` is non-empty

Optional server-side settings are `EXTERNAL_LLM_API_KEY` and `EXTERNAL_LLM_MODEL`. The endpoint
credential is never returned to the browser or by `/provider-health`.

The configured endpoint receives a bounded HTTP `POST` JSON body. The current workflow sends the
user ticket and instructions for classification, urgency, or candidate proposal generation. It
does not attach retrieved similar cases to proposal-generation requests. The adapter supports a
separate typed evidence field for other callers, but that does not make such data policy authority.

For proposal generation, the provider returns candidate text. Any provider-supplied `grounded`,
confidence, citation, or policy-approval fields are ignored. A host-configured policy verifier and
approved policy ID set are required before a proposal may be returned; each proposal needs a
passing check and its policy reference. The verifier outcome is only as strong as its
implementation. The current deterministic code checks control flow and reference membership; it
does not establish semantic entailment or policy correctness.

If `EXTERNAL_LLM_API_KEY` is set, the adapter sends it as a server-side bearer token. The public
repository does not prescribe which inference service implements this endpoint.

## Cache, retry, and fallback behavior

Route/model/task, workflow instructions, user ticket, candidate response, typed evidence,
temperature, and token limit are hashed into the SQLite cache key. The existing retry and
exponential-backoff settings apply to external calls. When external inference is active, the
route order is `external` then deterministic `mock`; a fallback is marked degraded. Degraded
proposal generation is withheld by the policy gate.

When demo/mock mode is active, the route order is local-only, so configuration of an external
endpoint cannot accidentally make the public demo perform a network inference call.

`/provider-health` exposes whether external inference is configured and active, plus operational
cache, embedding, vector-store, ingestion, and policy-source status. It does not expose the
endpoint URL or credential.

## Evaluation boundary

The checked-in evaluation uses the deterministic route. It measures workflow completion,
classification labels, mapped-intent retrieval, and structural policy-gate counts on a small
synthetic fixture. It does not measure semantic entailment, policy correctness, production
language-model quality, or customer outcomes. External GenAI behavior requires a separate
controlled evaluation before any production claim.
