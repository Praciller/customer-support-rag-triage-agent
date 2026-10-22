# GitHub main-branch governance and release gates

This is an owner-operated checklist, not a report that protections are already enabled.

## Verified starting point

- On October 23, 2026, the GitHub repository's `main` branch reported
  `protected: false`, and the read-only repository ruleset listing was empty.
- The connected GitHub integration returned HTTP 403 for branch-protection
  administration and cannot install or modify repository rules.
- No repository setting was changed by this document.

## Configure the ruleset in GitHub

An owner with Settings access can navigate to **Settings → Rules → Rulesets →
New branch ruleset** and configure:

1. Target only `main`; mark the ruleset **Active** rather than Evaluate.
2. Require pull requests for changes to `main`. Do not require an approval from the
   PR author; if review approvals are mandated, confirm a separate reviewer is available.
3. Require passing checks corresponding to all four jobs in
   `.github/workflows/ci.yml`: `backend`, `frontend`, `browser`, and
   `docker-smoke`. Select the **actual check contexts and GitHub Actions source**
   as displayed by the Rulesets UI rather than copying a guessed check name.
4. Require the branch to be up to date with `main` before merging if the
   repository workflow can support it. Rerun tests after resolving conflicts.
5. Block force pushes and branch deletion. Limit bypass to a documented break-glass
   recovery policy, ideally with an audit trail; avoid broad everyday bypasses.
6. Save and inspect the ruleset configuration in read-only mode. Confirm it
   applies to `main` and does not unexpectedly block authorized maintenance.

Depending on repository ownership and the GitHub plan, some controls may not
be available; use the strongest supported settings and record that limitation.

## Verify enforcement

- Open a small, harmless pull request from a branch and ensure the four required
  checks appear. Confirm the merge gate blocks while any required check is pending
  or failing, and permits merge only when the applicable policy passes.
- Confirm that the rule is **active**, not simply saved, and that bypassers are explicit.
- Check that security fixes can still be delivered through a normal PR. Keep the
  current, known-good `main` SHA as a rollback reference.
- Do **not** test branch restrictions by force-pushing or deleting `main`.

## Separation of environments

A successful GitHub CI run does not constitute a Hugging Face deployment.
Treat changes to Hugging Face Spaces, authentication, datasets, secrets, and DNS
as separate approved operations. For any release:

- Record the reviewed GitHub merge SHA, the CI run URL, and the exact Space revision.
- Smoke-test live `/ready`, one deterministic triage path with seven trace nodes,
  public-ingestion rejection, desktop/mobile rendering, and no secrets in output.
- Keep a verified Space rollback revision before publishing.
- Never infer live benchmark quality from the 8-case mock dataset or from the
  offline human-review scoring tool until actual reviewed labels exist.

## Review record

| Item | State |
| --- | --- |
| GitHub ruleset protection for `main` | **Not configured at last read-only check** |
| Required four CI checks | Defined in workflow; owner must select live check contexts |
| External inference or sensitive real customer data | Not approved |
| Hugging Face production synchronization | Separate release approval required |

This document does not itself change any GitHub setting or production deployment.
