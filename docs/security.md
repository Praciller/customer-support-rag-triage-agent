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

The SQLite inference cache hashes the key and stores provider output in plaintext before policy review. Expired rows are removed when their key is read again. Use trusted storage and disable caching for sensitive traffic until encryption, access controls, and scheduled deletion are in place. Application traces record bounded summaries and evidence identifiers.

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

## Dependency audit and release evidence

CI blocks on `pip-audit==2.10.1 --strict` for `requirements.production.txt`,
a separate strict audit of the installed packages in the ONNX Docker release
image, and frontend `npm audit --audit-level=low`. The ONNX image check verifies
that FastEmbed and Pillow are absent. These results apply to the resolved
packages and the image checked by the run. A previously deployed image needs
its own package audit and smoke test before release claims are made.
[CI workflow](../.github/workflows/ci.yml)

[Issue #93](https://github.com/Praciller/customer-support-rag-triage-agent/issues/93)
and the [historical FastEmbed/Pillow review](pillow-fastembed-reachability-20261024.md)
document the October 23 audit of Datasets 4.8.5, fsspec 2026.2.0 and Pillow 12.3.0.
The current Datasets and fsspec minimums include the published fixes for those
advisories. FastEmbed 0.9.1 supports Pillow 13 on Python 3.12. Any optional
FastEmbed package graph needs its own strict audit and runtime verification
before release. [FastEmbed upstream change](https://github.com/qdrant/fastembed/pull/830)
