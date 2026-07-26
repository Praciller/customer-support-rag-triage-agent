# Architecture

## Runtime boundaries

```mermaid
flowchart TB
  Browser[React operations console] -->|JSON/HTTP| API[FastAPI]
  API --> Services[ApplicationServices]
  Services --> Graph[Compiled LangGraph StateGraph]
  Graph --> Router[ProviderRouter]
  Router --> Cache[(SQLite TTL cache)]
  Router --> Mock[Deterministic mock]
  Router -. optional .-> Providers[Gemini / Groq / Cerebras]
  Graph --> Retriever[QdrantRetriever]
  Retriever --> Embedder[Local BGE FastEmbed]
  Retriever --> Qdrant[(Qdrant collection)]
  Bootstrap[Bounded JSON fixture] --> Retriever
  Reports[Evaluation JSON] --> API
```

The browser receives no provider credentials. FastAPI owns trust-boundary validation, rate
limits, ingestion authorization, controlled errors, liveness, and readiness. `ApplicationServices`
constructs the configured providers, cache, retriever, and graph.

## Workflow contract

`TriageState` carries the ticket, classification, urgency, retrieved cases, draft, grounding,
next action, provider metadata, and append-only trace through seven fixed nodes. Prompts remain in
`prompts/`; provider and retrieval implementations remain outside graph orchestration.

Every node returns bounded, non-secret trace metadata. Public responses exclude environment
values, provider keys, raw prompts, filesystem paths, and stack traces.

### Seven-node implementation contract

| Node | Typed state consumed | Typed state produced | Degraded or error behavior | Trace evidence |
| --- | --- | --- | --- | --- |
| `normalize_message` | `message`, `top_k` | `normalized_message` | API validation rejects empty or over-limit input before the graph. Unexpected errors become a controlled API 500. | Input and normalized lengths; local component. |
| `classify_intent` | `normalized_message` | `intent`, `intent_confidence` | Unknown labels become `other`; confidence is clamped to 0..1. Provider retry/fallback/degraded state remains visible on this node. | Intent, confidence, provider, model, cache/fallback/degraded flags. |
| `detect_urgency` | `normalized_message`, `intent` | `urgency`, `escalate`, `escalation_reason` | Unknown urgency becomes `medium`. Provider retry/fallback/degraded state remains visible on this node. | Urgency, escalation flag, provider, model, cache/fallback/degraded flags. |
| `retrieve_similar_cases` | `normalized_message`, `intent`, `top_k` | `retrieved_cases` | A missing collection returns no evidence. Retrieval service exceptions fail the request through the controlled API boundary. | Intent filter, requested K, returned count, Qdrant component. |
| `generate_support_response` | Message, intent, urgency, retrieved cases | `suggested_response`, provider/cache/fallback/degraded metadata | Router exhaustion returns a manual-review-safe fallback and marks the result degraded. Retrieved case IDs are appended as internal evidence references. | Draft length, context count, provider/model and cache/fallback/degraded flags. |
| `grounding_check` | Draft and retrieved cases | `grounded`, score, confidence, unsupported claims | Retrieved context is supplied to the verifier. Empty evidence or degraded generation deterministically forces `grounded=false`, caps score/confidence, and records an unsupported-claim reason. | Draft length, grounded result, score, provider/model and cache/fallback/degraded flags. |
| `suggest_next_action` | Intent, urgency, escalation, grounding | `next_action` | Ungrounded output always becomes `manual_review`; other actions are selected by explicit rules. | Inputs used and selected action; rules component. |

`TriageState` is a `TypedDict`, API requests and responses are Pydantic models, and the frontend
mirrors the public trace and evidence schemas in TypeScript. A node that raises does not fabricate a
completed trace step; FastAPI returns a sanitized error instead.

## Data lifecycle

On startup, demo mode reads `data/demo/support_cases.json`, computes stable UUID5 point IDs,
retrieves existing IDs, and embeds/uploads only missing records. Readiness becomes `ready` only
when all fixture records exist. The full Banking77 dataset is never downloaded during demo startup
or CI.

## Deployment shapes

- Docker Compose: React dev server, FastAPI, and Qdrant server.
- Hugging Face CPU image: built React assets served by FastAPI, embedded local Qdrant, SQLite cache,
  and FastEmbed, all on port 7860.
- Test/CI: in-memory Qdrant and deterministic hashing embeddings for bounded checks.

Local embedded storage and the in-memory limiter are deliberate single-instance constraints. Move
to managed persistence and shared rate limiting only when horizontal scale is required.
