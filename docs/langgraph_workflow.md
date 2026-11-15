# LangGraph Workflow

The compiled `StateGraph` executes:

1. `normalize_message`
2. `classify_intent`
3. `detect_urgency`
4. `retrieve_similar_cases`
5. `generate_support_response`
6. `policy_gate`
7. `suggest_next_action`

Each successful node appends bounded input/output summaries, status, duration, component, and
task-specific metadata to the returned trace. Model-backed nodes add provider, model, cache,
fallback, and degraded flags. Retrieval records similar-case counts and IDs. Proposal generation
does not receive retrieved cases; the policy gate accepts only configured approved-policy IDs and
per-proposal verifier outcomes.

The public demo has no approved policy source, so each proposal is withheld, the response is a fixed
short acknowledgement, and the next action is `manual_review`. Similar past cases are not policy
evidence. Any missing, invalid, uncertain, unsupported, conflicting, or failed policy check also
routes to review. Intent and urgency remain visible for prioritization. Unexpected node exceptions
are sanitized at the FastAPI boundary and do not create a false completed trace step.

See [architecture.md](architecture.md#seven-node-implementation-contract) for the authoritative
per-node input, output, failure, and trace contract. Policy review is structural; the current
implementation and deterministic evaluation do not prove semantic entailment or policy correctness.
