# LangGraph Workflow

The compiled `StateGraph` executes:

1. `normalize_message`
2. `classify_intent`
3. `detect_urgency`
4. `retrieve_similar_cases`
5. `generate_support_response`
6. `grounding_check`
7. `suggest_next_action`

Each node appends a status, detail, and duration to the returned trace. The response includes
provider/model metadata, cache state, degraded mode, unsupported claims, and a human next action.
