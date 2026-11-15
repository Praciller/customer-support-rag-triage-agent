# Security

## Public API controls

- Pydantic forbids extra request fields and bounds message length, `top_k`, and ingest size.
- `/triage` and `/answer` share a configurable sliding-window limit; `/search-similar` and `/ingest` use separate limits keyed by client IP and route.
- `/ingest` is disabled by default. Outside local development, access requires `X-Admin-API-Key`; comparison uses `secrets.compare_digest`.
- Requests have a configurable timeout and unexpected exceptions return a controlled message.
- `/triage` and `/answer` do not accept idempotency keys or deduplicate in-flight requests. A browser timeout does not prove backend work stopped; a user-triggered retry can repeat provider work or charges. The UI does not retry POST requests automatically.
- The public `GET /eval/results`, `POST /evaluate`, and `GET /metrics/sample` routes serve the selected evaluation report, including its example messages. Use synthetic or explicitly approved, de-identified evaluation data for any report exposed through these routes; never publish real customer tickets or secrets there.
- CORS origins are environment-configured.
- `/provider-health` reports local inference and storage state without credentials or raw environment values.

## CI evidence uploads

The backend CI job uses a read-only `GITHUB_TOKEN` and uploads only the explicitly
enumerated synthetic evaluation artifacts created under `/tmp/evaluation` plus the
adversarial regression report. It no longer archives the entire checkout, which
could accidentally include new local/generated data. Never insert real customer
tickets or secrets into the public evaluation fixture or CI evidence artifacts.

## Retrieved-content and prompt boundaries

Retrieved messages are untrusted text, not instructions or policy. The graph returns each result as a
typed `similar_past_case` with `approved_policy=false`. Provider generation receives the current
ticket, intent, and urgency; retrieved cases are not passed as policy evidence. Search and case
views show similar cases as context, not authorization to take an action.

Provider-supplied `grounded`, confidence, and citation claims are ignored. The public demo has no
approved policy references or policy verifier. Its policy gate withholds all generated proposals,
returns a fixed acknowledgement, and routes to `manual_review`. In deployments that configure a
policy verifier, each proposal must name an approved policy ID and return a passing result; missing,
invalid, unsupported, conflicting, uncertain, failed, or degraded-generation checks withhold the
proposal. This structural gate does not prove that a policy semantically entails a proposal.

The deterministic synthetic adversarial fixture tests authority separation and fail-closed routing
in [`reports/evaluation/adversarial_retrieval.md`](../reports/evaluation/adversarial_retrieval.md).
It does not establish semantic LLM prompt-injection immunity or universal protection against
malicious retrieved text. Before using private help-center content or customer data, add source
authorization, tenant isolation, content classification, a real approved policy corpus, and a
validated semantic review process.

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

The application prepares responses for human review. Banking77 is not company policy, and similar-case matches do not establish that an organization permits an action.


## Decision-correctness boundary

High/critical urgency and explicit escalation remain visible for human prioritization. Without a
verified proposal, the next action is `manual_review`. Similar-case search may retry once without
an intent filter when the filtered lookup returns no cases; case similarity does not confer policy
authority.

The API version 2 response reports `policy_status` and one `proposal_checks` entry per candidate.
Each returned `verified_proposals` item has an associated passing check and approved policy ID.
Invalid policy references, uncertain or failed checks, verifier errors, and degraded generation
fail closed. The default demo has no approved policy source and cannot return a verified proposal.

The policy-gate implementation validates status and reference structure; it does not perform or
claim semantic entailment or policy correctness. Provider self-report, citation presence, and
similar-case matches are not proof of support. Retrieved content remains untrusted, and a human
must review the result before taking action.

## Python production dependency advisories — unresolved

A source-level [FastEmbed/Pillow reachability review](pillow-fastembed-reachability-20261024.md)
separates the real text-only public API controls from transitive dependency
uncertainty and explains why the hashing CI smoke does not validate the
FastEmbed Hugging Face release image. Its source regression tests do not
eliminate advisories or grant release approval.

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
