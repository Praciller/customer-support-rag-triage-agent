# Security

## Public API controls

- Pydantic forbids extra request fields and bounds message length, `top_k`, and ingest size.
- `/triage`, `/search-similar`, and `/ingest` use configurable sliding-window limits keyed by client IP and route.
- `/ingest` is disabled by default. Outside local development, access requires `X-Admin-API-Key`; comparison uses `secrets.compare_digest`.
- Requests have a configurable timeout and unexpected exceptions return a controlled message.
- CORS origins are environment-configured.
- `/provider-health` reports local inference and storage state without credentials or raw environment values.

## Retrieved-content and prompt boundaries

Retrieved messages are untrusted text, not instructions or policy. The graph converts each result to a typed `RetrievedEvidence` record and passes it through a dedicated `evidence` field. Workflow instructions, the current user ticket, candidate response, and retrieved evidence are separate request fields; retrieved text is never assigned a system/developer role. Original evidence text remains available for traceability.

The generation contract accepts structured `evidence_references` only when every reference ID belongs to the retrieved evidence block. Unknown or fabricated IDs are rejected, removed from the public reference list, and force an ungrounded result. Empty evidence, rejected citations, or degraded generation deterministically forces `grounded=false` and `manual_review`. Trace metadata carries reference IDs and counts without copying evidence text or prompts.

Structural authority isolation and a deterministic eight-record adversarial fixture are tested in [`reports/evaluation/adversarial_retrieval.md`](../reports/evaluation/adversarial_retrieval.md). These tests do not establish semantic LLM prompt-injection immunity or universal protection against malicious retrieved text.

These controls do not prove semantic entailment and do not prevent every prompt-injection pattern. Before using private help-center content or customer data, add source authorization, tenant isolation, content classification, stronger citation/entailment checks, and an approved policy corpus.

## Secret and local-state handling

`.env`, local caches, embedded databases, and generated frontend output are ignored. The public inference route does not require an external inference credential. Never place credentials in frontend variables, screenshots, logs, fixtures, or checked-in evaluation artifacts.

The SQLite inference cache hashes workflow request fields and typed retrieved evidence for keys but stores generated responses in plaintext. Keep it on trusted local storage, set retention appropriate to the data, and do not cache sensitive tickets without encryption and deletion controls. Application traces deliberately contain bounded summaries and evidence reference IDs rather than raw prompts, evidence text, or environment values.

## Limitations

The limiter is intentionally in-memory and per process; it is not a distributed abuse-control system. Embedded storage is single-instance. Add a trusted proxy, shared limiter, authentication, and persistent managed storage before multi-instance or sensitive-data use.

The application drafts responses for human review. Banking77 is not company policy, and grounding against demo examples does not establish policy correctness.
