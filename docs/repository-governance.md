# GitHub main-branch governance and release gates

This document records the repository's **active** main ruleset and the
remaining verification required by [Issue #84](https://github.com/Praciller/customer-support-rag-triage-agent/issues/84).

## Verified current configuration — October 23, 2026

- Repository ruleset `25716747`, **Main PR and four CI checks**, has
  `enforcement: active` and targets only `refs/heads/main`.
- A separate read of `GET /branches/main` returned `protected: true`.
- The ruleset requires pull requests and zero approvals (compatible with a
  solo maintainer). Review threads must be resolved; a separate reviewer
  is not silently required for ordinary maintenance.
- Required GitHub Actions check contexts are `backend`, `frontend`,
  `browser`, and `docker-smoke`; each pins the GitHub Actions app
  integration ID `15368`. Strict up-to-date checks are enabled.
- Deletion and non-fast-forward pushes to `main` are forbidden. The
  ruleset has no bypass actors.
- This was applied with the repository owner's authenticated GitHub CLI
  session. The separate GitHub App integration can inspect the result,
  but does not have permission to administer GitHub rulesets.
- [PR #95](https://github.com/Praciller/customer-support-rag-triage-agent/pull/95)
  merged through the standard pull-request path at GitHub commit
  `5f84ae3dfaa24c8d457c1422777ad5372a4121b8`, after all four
  exact-head jobs passed.

## Remaining enforcement verification

The harmless [PR #96](https://github.com/Praciller/customer-support-rag-triage-agent/pull/96)
provided a **pending-check negative case**: GitHub returned
`mergeable: true` but `mergeable_state: blocked` for exact head
`d35825bd4d1235b21b8696d5dad2d14112ec8572` while all four
required CI jobs were still in progress. This is a read-only GitHub
merge-gate observation, not an attempted unsafe merge or a test of
failing-check behavior. Confirm the same PR changes to eligible once
all four required jobs pass before closing Issue #84.

A repository owner can review and maintain the rule under
**Settings → Rules → Rulesets → Main PR and four CI checks**.
Keep the required contexts aligned with the actual check-run names
and GitHub Actions source. When changing CI job names, update and
re-verify the ruleset before merging the workflow rename.

## Safe operation

1. Open a pull request for each source or documentation change.
2. Confirm all four required checks pass on the exact PR head and that
   the head is up to date with `main`; resolve review threads.
3. Merge only after GitHub marks the branch eligible. Record the merged
   SHA and verify the post-merge CI push run separately.
4. For a security emergency, document the owner-approved recovery
   path and audit trail before changing protections. Never use a
   routine force-push or delete `main` to test protection.
5. Keep the last known-good `main` commit and release revision available
   for ordinary revert-based recovery.

## Independent Hugging Face Space release

GitHub and Hugging Face Spaces are separate Git repositories. A merged
PR or successful GitHub CI **does not** deploy to the live Space.

- Record the reviewed GitHub source SHA, exact Space Git revision or
  image digest, deploy timestamp, and tested rollback target.
- Verify live `/ready`, the synthetic seven-node triage, unauthenticated
  ingestion rejection, page identity, 390/768/1440 rendering, browser
  console errors, and accessibility before claiming a v3 release.
- Keep unverified Python/Pillow advisories and the deterministic
  8-ticket evaluation limitations visible.
- Never publish credentials, customer-sensitive test records, or raw
  prompt contents; do not trigger paid Hugging Face resources.

As of October 23, 2026 the live Space remains on the older revision
`a2661562ff1a2a7b7f15e4b9145cb007c98444a5`, which is **not** the
current GitHub main commit. Refer to [Issue #89](https://github.com/Praciller/customer-support-rag-triage-agent/issues/89)
for remaining live-release and manual accessibility gates.

## Review record

| Item | State |
| --- | --- |
| Ruleset `25716747` on `main` | **Active**, branch `protected: true` |
| Required CI checks | Four checks, pinned to GitHub Actions integration 15368 |
| Normal PR merge | Verified on PR #95 |
| Pending-check merge block | **Observed** on PR #96 (`mergeable_state: blocked`) |
| Failing-check merge block | Not separately tested; do not forge failures |
| Python dependency risk | Pillow issue #93 unresolved; no exception granted |
| Hugging Face main-to-Space synchronization | Not performed; separate owner release |
