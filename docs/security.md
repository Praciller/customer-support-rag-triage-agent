# Security

## Public API controls

- Pydantic forbids extra request fields and bounds message length, `top_k`, and ingest size.
- `/triage`, `/search-similar`, and `/ingest` use configurable sliding-window limits keyed by client IP and route.
- `/ingest` is disabled by default. Outside local development, access requires `X-Admin-API-Key`; comparison uses `secrets.compare_digest`.
- Requests have a configurable timeout and unexpected exceptions return a controlled message.
- CORS origins are environment-configured.
- `/provider-health` reports local inference and storage state without credentials or raw environment values.

## CI evidence uploads

The backend CI job uses a read-only `GITHUB_TOKEN` and uploads only the explicitly
enumerated synthetic evaluation artifacts created under `/tmp/evaluation` plus the
adversarial regression report. It no longer archives the entire checkout, which
could accidentally include new local/generated data. Never insert real customer
tickets or secrets into the public evaluation fixture or CI evidence artifacts.

## Retrieved-content and prompt boundaries

Retrieved messages are untrusted text, not instructions or policy. The graph converts each result to a typed `RetrievedEvidence` record and passes it through a dedicated `evidence` field. Workflow instructions, the current user ticket, candidate response, and retrieved evidence are separate request fields; retrieved text is never assigned a system/developer role. Original evidence text remains available for traceability.

The generation contract accepts structured `evidence_references` only when every reference ID belongs to the retrieved evidence block. Unknown or fabricated IDs are rejected, removed from the public reference list, and force an ungrounded result. Empty evidence, rejected citations, or degraded generation deterministically forces `grounded=false` and `manual_review`. Trace metadata carries reference IDs and counts without copying evidence text or prompts.

Structural authority isolation and a deterministic eight-record adversarial fixture are tested in [`reports/evaluation/adversarial_retrieval.md`](../reports/evaluation/adversarial_retrieval.md). These tests do not establish semantic LLM prompt-injection immunity or universal protection against malicious retrieved text.

These controls do not prove semantic entailment and do not prevent every prompt-injection pattern. Before using private help-center content or customer data, add source authorization, tenant isolation, content classification, stronger citation/entailment checks, and an approved policy corpus.

## Secret and local-state handling

`.env`, local caches, embedded databases, and generated frontend output are ignored. The public inference route does not require an external inference credential. Never place credentials in frontend variables, screenshots, logs, fixtures, or checked-in evaluation artifacts.

The SQLite inference cache hashes workflow request fields and typed retrieved evidence for keys but stores generated responses in plaintext. Keep it on trusted local storage, set retention appropriate to the data, and do not cache sensitive tickets without encryption and deletion controls. Application traces deliberately contain bounded summaries and evidence reference IDs rather than raw prompts, evidence text, or environment values.

## Local Compose and container boundary

The local Compose example binds UI, API, and Qdrant HTTP host ports to
`127.0.0.1`, does not publish Qdrant's gRPC port, and mounts checked-in data
and reports read-only. The Compose API runs as non-root UID 10001, with
writable internal cache directories and a user-owned persistent model cache mount. Do not expose Compose to the public
internet as a production support system: it intentionally lacks end-user
authentication, multi-tenant authorization, and distributed rate limiting.

## Limitations

The limiter is intentionally in-memory and per process; it is not a distributed abuse-control system. Embedded storage is single-instance. Add a trusted proxy, shared limiter, authentication, and persistent managed storage before multi-instance or sensitive-data use.

The application drafts responses for human review. Banking77 is not company policy, and grounding against demo examples does not establish policy correctness.


## Decision-correctness hardening

High/critical urgency and explicit escalation take precedence over requesting missing identifiers when
the draft is grounded. Ungrounded drafts still require `manual_review`. A classified-intent search
with zero matches retries once without an intent filter; it does not claim to solve wrong-intent
retrieval when filtered results are nonempty.

The graph never fabricates evidence citations when a provider omits reference IDs; missing IDs
with retrieved evidence force an ungrounded result. Only literal JSON `true` permits the grounding
verifier to approve a draft. Nonfinite scores and malformed unsupported-claim lists fail closed.
If an active external provider falls back to the deterministic mock provider, the route is marked
degraded (including cached mock fallbacks), and final grounding is denied. Degradation from
classification or urgency detection propagates through the full graph.

These safeguards enforce workflow invariants, not claim-level semantic entailment or policy
correctness. Neither model self-report nor presence of retrieved text proves a response is supported.

## Python production dependency advisory gate

The backend GitHub Actions job now invokes the Python Packaging Authority's
`pip-audit==2.10.1` on `requirements.production.txt` with strict dependency
collection. Findings and resolution failures block the existing `backend`
required check; it is not a best-effort `continue-on-error` step.
This tool is installed **only inside CI**, not added to either production
or development requirements.

**Scope:** the file contains version ranges, not a hashed lockfile. The
scanner resolves a fresh production-dependency graph at CI execution time.
A clean result does **not** attest the exact wheels baked into a previously
deployed Hugging Face image, the explicitly installed CPU PyTorch wheel,
the native/shared libraries inside containers, or the OS image. Those require
release-specific SBOM and image scanning. The public demo is not a
multi-tenant customer production system.

If advisories appear, keep the check failing and open a focused remediation
issue with exact affected package, version and advisory; do not suppress
failures or widen dependency ranges silently.

### October 2026 remediation after first scan

The first strict scan in [run 39843328801](https://github.com/Praciller/customer-support-rag-triage-agent/actions/runs/39843328801)
**failed** with 37 advisory records across three resolved packages:
`datasets@4.8.5` (fixed in 5.0.1), `fsspec@2026.2.0` (fixed in
2026.6.0), and `Pillow@12.3.0` (fixed in 13.0.0). These were
**37 advisory records, not 37 separately exploitable application paths**.
Both the development and production requirements now specify explicit
security minimums for these three packages, including the necessary
Datasets major-version upgrade. CI rechecks exact resolved versions
and basic imports; the offline synthetic workflow does not exercise
a remote Hugging Face dataset download, and no production deploy
is implied. Do not waive a failing advisory gate.
