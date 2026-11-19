# API v2 coordinated release

## Approval gate

This plan changes the existing Render services only after owner approval. The candidate
is based on PR #121 head `8597655c110b16588ca0236e3c0ed5091597fdbc`.
The compatibility changes require a new approved commit, exact-head CI and post-merge CI.
No deployment has been performed for this plan.

## Candidate dependency audit

On November 18, the full frontend audit reported 14 High affected package
entries associated with one picomatch advisory,
[GHSA-fc5q-39xc-vjpf](https://github.com/advisories/GHSA-fc5q-39xc-vjpf).
This is recorded as historical evidence.

On November 19, `npm ci` and the full `npm audit --audit-level=low` passed on the
17-file local compatibility candidate based on `8597655c110b16588ca0236e3c0ed5091597fdbc`.
The full audit exited 0 and reported zero vulnerabilities. The candidate
preserves the dependency manifests and lockfiles.

[GitHub CI run #44126491185](https://github.com/Praciller/customer-support-rag-triage-agent/actions/runs/44126491185)
passed all five jobs for the existing PR head. The 17-file candidate was
verified locally. Its future commit still requires the full audit, exact-head
CI, owner approvals, and post-merge CI before the coordinated Render release.

## Observed Render state on November 18, 2026

Both existing services build GitHub `main` and currently serve
`00e2900d8deb6ead82fabdcb2485c93ebb25a9ff`.

| Service | Live deploy | Build | Auto Deploy |
| --- | --- | --- | --- |
| API `srv-d8m34d6q1p3s73fpkcgg` | `dep-dbivuarbc2fs73ctmgtg` | Native Python, repository root, `sh scripts/install-cpu-deps.sh` | On Commit |
| Frontend `srv-d8m34q6gvqtc73ck13qg` | `dep-dbivuarbc2fs73ctmi40` | Static site, `frontend`, `npm ci && npm run build`, publish `dist` | On Commit |

PR previews are Off for both services. The API is Free. The latest matching
deployments took 4m32s for API and 36s for Frontend. These historical timings
demonstrate independent deployment completion and cannot predict cutover duration.
The public API OpenAPI document advertises version 1.0.0 and its legacy
grounding fields. Static-site rollback and native-service rollback are separate.

## Consumer inventory and migration contract

| Consumer | v1 backend | v2 backend without bridge | Candidate bridge |
| --- | --- | --- | --- |
| Deployed v1 console, including previously opened tabs | Current contract | Missing scores and `unsupported_claims` can break rendering | Unmarked triage requests receive HTTP 426 through the existing error handler |
| PR console | Missing `policy_status` and proposal arrays can break rendering | Current contract | Sends version header and rejects legacy HTTP 200 results before setting UI state |
| v1 third-party `/triage` or `/answer` callers | Current contract | Breaking response schema | Explicit HTTP 426, caller upgrade required |
| Updated ONNX/FastEmbed/local and Space verifier scripts | v2 checks fail honestly | v2 contract | Send the required version header |
| CI API container smoke and API integration tests | v1 fields differ | v2 contract | Send the required version header |
| Internal graph/evaluation commands | Source-version dependent | v2 structural policy counts | No HTTP negotiation, run from matching source |
| Evaluation views and consumers | Legacy grounding metrics | v2 structural policy metrics | New console hides reports without v2 structural method, old external consumers must migrate |
| Health, readiness, dataset and provider reads | Existing read contracts | Compatible for migration purposes | No new version requirement |
| Similar-case search | v1 case fields | Additional explicit evidence labels | Existing common case fields retained, public corpus only |
| Old hosted Hugging Face UI | Independent historical v1 backend | Separate release required | Remains held on its historical revision |

Repository consumers are enumerated by searches for `/triage`, `/answer`,
`grounded` and `grounding_score`. External callers cannot be enumerated from
source alone. Owner approval must include the intentional v1 client retirement.

Both triage endpoints retain the v2 response schema and require
`X-ResolveOps-API-Version: 2`. Missing/unsupported versions receive HTTP 426
before workflow execution. This header negotiates a response contract and grants
no access rights. The default public demo still withholds every proposal without
approved policy and routes to human review. No legacy scores are synthesized.

The current v1 backend ignores the new header. The candidate frontend detects
legacy result fields or missing policy fields and displays a controlled version
mismatch without a decision or automatic POST retry. This also protects a newer
cached console during backend rollback. A service-unavailable period is expected
between the two manual releases. Zero downtime is not an acceptance claim.

## Exact runtime security gate

Render currently installs `requirements.txt` and CPU Torch through
`install-cpu-deps.sh`. The existing Python CI requirements audit targets
`requirements.production.txt`. A clean production requirements audit or a clean
Dockerfile.hf audit cannot attest the complete installed native Render runtime.

For the v2 native API release, change only its build command to
`sh scripts/install-render-deps.sh` after approval. The start command and source
branch remain as recorded. The new command installs existing ONNX production
requirements, runs `pip check`, freezes all installed packages including bootstrap
packages, and strictly audits that manifest before activation. Its auditor runs
in a temporary separate virtual environment. The auditor resolves the exact
installed manifest on the same Python/platform, with consistency independently
checked by `pip check`. Package names and exact versions are emitted as JSON
to the build log before the audit, without install URLs or environment values.
The Docker smoke CI job also executes this installer in the API image.

Local Dockerfile.api image audit and synthetic tests provide candidate evidence.
Native Render's actual installed versions must pass its own pre-activation audit.
Record the successful build/deploy IDs and dependency manifest as release evidence.
Do not describe the local Docker image ID as a deployed Render image digest.

## Coordinated sequence after approval

1. Recheck both deployed revisions and settings against the observations above.
   Freeze concurrent releases. Set Auto Deploy to Off on both services and verify
   no deployments are queued or building before merging. Obtain approval for this
   configuration change and the bounded interruption.
2. Commit/push the reviewed compatibility patch to PR #121 only after approval.
   Wait for all five jobs and installed-image/security gates on the new exact SHA.
   Approve and merge separately, record the merge SHA, and wait for exact-main CI.
3. Verify the frontend's public API base resolves to the existing API origin.
   Deploy the frontend manually at that exact merge SHA while API v1 stays live.
   Confirm a synthetic triage yields the controlled version-mismatch message.
   Evaluation must show unavailable instead of presenting legacy policy metrics.
   A cached old console can continue against v1 during this phase.
4. Apply the approved native build-command change with Auto Deploy still Off.
   Keep the existing Free plan and ONNX/demo/memory/public-ingestion-denied
   configuration. Do not inspect/reveal credentials or enable external inference.
   Deploy API manually at the same exact merge SHA. Its strict installed-runtime
   audit must succeed before activation. A failed build leaves the old API active.
5. Verify the live deploy IDs and SHAs independently for both services. Check
   OpenAPI v2, both triage endpoints with the version header, 27 indexed fixture
   records, seven ordered stages, manual review, no verified proposals, matching
   v2 evaluation and anonymous ingestion denial. Test old clients receive 426
   and the new console succeeds at desktop/mobile sizes. Use synthetic data only.
6. Check frontend error/timeout behavior and manually verify keyboard/focus,
   screen-reader reading order and 200% browser zoom required by Issue #89.
   Leave Auto Deploy Off until owner accepts the coordinated release evidence.
   Any later re-enable requires explicit approval.

## Rollback

Keep both baseline deploy IDs above and the source SHA available before cutover.
If the new frontend fails while API v1 is still live, restore only the recorded
frontend deployment and verify the original v1 pair.

After API v2 activation, stop release activity and keep Auto Deploy Off. Restore
the recorded native API deployment first. The candidate frontend will reject its
legacy payload safely. Restore the recorded static frontend deployment next.
Confirm both live revisions equal the baseline, then run the synthetic v1 smoke.
Restore the original API build command only through the approved configuration
rollback. A rebuild may resolve different dependencies and needs another audit.

If a recorded deployment cannot be restored, stop and report the failure before
trying another source revision or changing resource plans. Avoid force pushes
and ad-hoc main changes. Existing open v2 tabs can require reload after rollback.

## Remaining release gates

Issue #89 remains open for human accessibility and live revision/rollback proof.
Issue #93 is historically closed by the owner. The new runtime audit covers its
actual ONNX dependency set, while historical deployed FastEmbed/Pillow evidence
remains a separate unresolved release concern. Do not close or rewrite either
issue from local-only evidence.

The historical Hugging Face revision remains
`a2661562ff1a2a7b7f15e4b9145cb007c98444a5`, with Hub metadata reporting SLEEPING.
No request to the Space application, wake, rebuild or deployment is part of this
plan. Existing-Space no-charge eligibility and owner release approval are still
required before that separate workflow.

Semantic grounding remains unverified. SQLite provider-response caching stores
plaintext with lazy expiry. Private tenant/source authorization is absent. The
release is restricted to synthetic/public demo content and deterministic local
inference. Approval does not expand it to customer records or private tenancy.
