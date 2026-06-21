# Security

## Public API controls

- Pydantic forbids extra request fields and bounds message length, `top_k`, and ingest size.
- `/triage`, `/search-similar`, and `/ingest` use configurable sliding-window limits keyed by
  client IP and route.
- `/ingest` is disabled by default. Outside local development, access requires
  `X-Admin-API-Key`; comparison uses `secrets.compare_digest`.
- Requests have a configurable timeout and unexpected exceptions return a controlled message.
- CORS origins are environment-configured.
- `/provider-health` reports routing state without credentials or raw environment values.

## Secret handling

`.env`, local caches, embedded databases, and generated frontend output are ignored. Provider keys
are read only by the backend. Never place credentials in `VITE_*` variables, screenshots, logs,
fixtures, or checked-in evaluation artifacts.

## Limitations

The limiter is intentionally in-memory and per process; it is not a distributed abuse-control
system. Timeout responses cannot forcibly stop already-running synchronous provider work in a
thread. Embedded storage is single-instance. Add a trusted proxy, shared limiter, authentication,
and persistent managed storage before multi-instance or sensitive-data use.

The application drafts responses for human review. Banking77 is not company policy, and grounding
against demo examples does not establish policy correctness.
