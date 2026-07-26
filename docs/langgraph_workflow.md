# LangGraph Workflow

The compiled `StateGraph` executes:

1. `normalize_message`
2. `classify_intent`
3. `detect_urgency`
4. `retrieve_similar_cases`
5. `generate_support_response`
6. `grounding_check`
7. `suggest_next_action`

Each successful node appends bounded input/output summaries, status, duration, component, and
task-specific metadata to the returned trace. Model-backed nodes add provider, model, cache,
fallback, and degraded flags. Retrieval records its evidence count; grounding records its result.

Empty retrieval or degraded generation cannot finish as grounded, and an ungrounded result routes to
`manual_review`. Unexpected node exceptions are sanitized at the FastAPI boundary and do not create
a false completed trace step.

See [architecture.md](architecture.md#seven-node-implementation-contract) for the authoritative
per-node input, output, failure, and trace contract.
