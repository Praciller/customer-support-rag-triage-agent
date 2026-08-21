# Architecture

## Runtime boundaries

```mermaid
flowchart TB
  Browser[React operations console] -->|JSON/HTTP| API[FastAPI]
  API --> Services[ApplicationServices]
  Services --> Graph[Compiled LangGraph StateGraph]
  Graph --> Router[Local inference router]
  Router --> Cache[(SQLite TTL cache)]
  Router --> Local[Deterministic generator]
  Graph --> Retriever[QdrantRetriever]
  Retriever --> Embedder[Local BGE FastEmbed]
  Retriever --> Qdrant[(Qdrant collection)]
  Bootstrap[Bounded JSON fixture] --> Retriever
  Reports[Evaluation JSON] --> API
```

FastAPI owns trust-boundary validation, rate limits, ingestion authorization, controlled errors, liveness, and readiness. `ApplicationServices` constructs the local inference route, cache, retriever, and graph.

## Workflow contract

`TriageState` carries the ticket, classification, urgency, retrieved cases, draft, grounding, next action, inference metadata, and append-only trace through seven fixed nodes. Prompts remain in `prompts/`; inference and retrieval implementations remain outside graph orchestration.

Every node returns bounded, non-secret trace metadata. Public responses exclude environment values, raw prompts, filesystem paths, and stack traces.

### Seven-node implementation contract

| Node | Typed state consumed | Typed state produced | Degraded or error behavior | Trace evidence |
| --- | --- | --- | --- | --- |
| `normalize_message` | `message`, `top_k` | `normalized_message` | API validation rejects empty or over-limit input before the graph. Unexpected errors become a controlled API 500. | Input and normalized lengths; local component. |
| `classify_intent` | `normalized_message` | `intent`, `intent_confidence` | Unknown labels become `other`; confidence is clamped to 0..1. Retry/fallback/degraded state remains visible on this node. | Intent, confidence, route, model label, cache/fallback/degraded flags. |
| `detect_urgency` | `normalized_message`, `intent` | `urgency`, `escalate`, `escalation_reason` | Unknown urgency becomes `medium`. Retry/fallback/degraded state remains visible on this node. | Urgency, escalation flag, route, model label, cache/fallback/degraded flags. |
| `retrieve_similar_cases` | `normalized_message`, `intent`, `top_k` | `retrieved_cases` | A missing collection returns no evidence. Retrieval service exceptions fail the request through the controlled API boundary. | Intent filter, requested K, returned count, Qdrant component. |
| `generate_support_response` | Message, intent, urgency, retrieved cases | `suggested_response`, route/cache/fallback/degraded metadata | Router exhaustion returns a manual-review-safe fallback and marks the result degraded. Retrieved case IDs are appended as internal evidence references. | Draft length, context count, route/model label and cache/fallback/degraded flags. |
| `grounding_check` | Draft and retrieved cases | `grounded`, score, confidence, unsupported claims | Retrieved context is supplied to the verifier. Empty evidence or degraded generation deterministically forces `grounded=false`, caps score/confidence, and records an unsupported-claim reason. | Draft length, grounded result, score, route/model label and cache/fallback/degraded flags. |
| `suggest_next_action` | Intent, urgency, escalation, grounding | `next_action` | Ungrounded output always becomes `manual_review`; other actions are selected by explicit rules. | Inputs used and selected action; rules component. |

`TriageState` is a `TypedDict`, API requests and responses are Pydantic models, and the frontend mirrors the public trace and evidence schemas in TypeScript. A node that raises does not fabricate a completed trace step; FastAPI returns a sanitized error instead.

## Data lifecycle

On startup, demo mode reads `data/demo/support_cases.json`, computes stable UUID5 point IDs, retrieves existing IDs, and embeds/uploads only missing records. Readiness becomes `ready` only when all fixture records exist. The full Banking77 dataset is never downloaded during demo startup or CI.

## Deployment shapes

- Docker Compose: React dev server, FastAPI, and Qdrant server.
- CPU container deployment: built React assets served by FastAPI, embedded local Qdrant, SQLite cache, and FastEmbed on one application port.
- Test/CI: in-memory Qdrant and deterministic hashing embeddings for bounded checks.

Local embedded storage and the in-memory limiter are deliberate single-instance constraints. Move to managed persistence and shared rate limiting only when horizontal scale is required.
