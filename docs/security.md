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

## Python production dependency advisories — unresolved

As of October 23, 2026, the Python Packaging Authority's
`pip-audit==2.10.1` is run on `requirements.production.txt` in
GitHub Actions' `backend` job. Unlike the **blocking** frontend npm
audit, this scan is currently **reporting-only** with
`continue-on-error: true` because the verified supported package
graph has unresolved advisories. A successful CI workflow **does not
mean Python dependency vulnerabilities are absent**.

Evidence: [Actions run 39843328801](https://github.com/Praciller/customer-support-rag-triage-agent/actions/runs/39843328801)
detected **37 advisory records in three packages**: `datasets@4.8.5`
(1; fixes at `5.0.1`), `fsspec@2026.2.0` (1; fixes at `2026.6.0`),
and `Pillow@12.3.0` (35; fixes at `13.0.0`). These are advisory
records, **not** 37 independently proven exploitable application
paths. An attempted fix conflicted with the current supported
`FastEmbed` line's `Pillow<13` constraint and failed Windows and
Docker dependency installation. The incompatible attempted changes
were **not** merged into `main`.

Track the supported remediation and any explicitly time-bounded,
owner-approved risk decision in
[Issue #93](https://github.com/Praciller/customer-support-rag-triage-agent/issues/93).
Do not bypass resolver constraints, suppress specific advisory IDs,
or claim the public demo is production-ready. React/npm audit results
are independent. The scan resolves current ranges at CI runtime,
not the exact Hugging Face deployment artifact or external CPU
PyTorch wheel.

## Partial Python remediation: Datasets and fsspec

An isolated update raises the `datasets` minimum to 5.0.1 and
`fsspec` minimum to 2026.6.0 in both development and production
requirements, without changing FastEmbed, Pillow or embedding behavior.
A new offline, real-Datasets `Dataset.from_dict` test checks that the
lazy Hugging Face loader continues to map ClassLabel records and respect
sample limits after the Datasets major-version change. It deliberately
does not download from the Hugging Face Hub.

This addresses the two advisory records for the prior Datasets and
fsspec versions **only after a passing exact-head pip-audit and full
CI confirms it**. The 35 Pillow advisory records remain pending
upstream FastEmbed support for Pillow 13. Track this in
[Issue #93](https://github.com/Praciller/customer-support-rag-triage-agent/issues/93).
The Python audit remains reporting-only; a passing CI workflow is
not evidence of zero Python advisories or a deployed-image security
attestation.
