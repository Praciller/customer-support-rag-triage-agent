# Security

## Public API controls

- Pydantic forbids extra request fields and bounds message length, `top_k`, and ingest size.
- `/triage`, `/search-similar`, and `/ingest` use configurable sliding-window limits keyed by client IP and route.
- `/ingest` is disabled by default. Outside local development, access requires `X-Admin-API-Key`; comparison uses `secrets.compare_digest`.
- Requests have a configurable timeout and unexpected exceptions return a controlled message.
- CORS origins are environment-configured.
- `/provider-health` reports local inference and storage state without credentials or raw environment values.

## Retrieved-content and prompt boundaries

Retrieved messages are untrusted text, not instructions or policy. The graph passes bounded context to generation and grounding prompts, appends internal evidence IDs, and requires human review. Empty retrieval or degraded generation deterministically forces an ungrounded result and `manual_review`.

These controls do not prove semantic entailment and do not prevent every prompt-injection pattern. Before using private help-center content or customer data, add source authorization, tenant isolation, content classification, stronger citation/entailment checks, and an approved policy corpus.

## Secret and local-state handling

`.env`, local caches, embedded databases, and generated frontend output are ignored. The public inference route does not require an external inference credential. Never place credentials in frontend variables, screenshots, logs, fixtures, or checked-in evaluation artifacts.

The SQLite inference cache hashes prompts and retrieved context for keys but stores generated responses in plaintext. Keep it on trusted local storage, set retention appropriate to the data, and do not cache sensitive tickets without encryption and deletion controls. Application traces deliberately contain bounded summaries rather than raw prompts or environment values.

## Limitations

The limiter is intentionally in-memory and per process; it is not a distributed abuse-control system. Embedded storage is single-instance. Add a trusted proxy, shared limiter, authentication, and persistent managed storage before multi-instance or sensitive-data use.

The application drafts responses for human review. Banking77 is not company policy, and grounding against demo examples does not establish policy correctness.
