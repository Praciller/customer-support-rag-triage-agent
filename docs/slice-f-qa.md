# Slice F: keyboard, semantic UI and release-evidence gates

Last verified GitHub main: `5f84ae3dfaa24c8d457c1422777ad5372a4121b8`,
with all four GitHub Actions push-CI jobs successful on that exact SHA
([run 39943448783](https://github.com/Praciller/customer-support-rag-triage-agent/actions/runs/39943448783)).
This SHA describes the **repository**, not the Hugging Face Space.

## Offline, automated checks (no secrets or third-party API keys)

- Existing Playwright and Storybook checks remain authoritative for UI behavior.
- `frontend/e2e/slice-f-accessibility.spec.ts` adds repeatable smoke checks for a
  keyboard skip-navigation link at 390, 768 and 1440 pixels; mobile
  classification-table column semantics; degraded/ungrounded manual-review
  status; keyboard expansion of trace diagnostics; unavailable evaluation
  announcement; and reduced-motion CSS behavior.
- Continue the complete `npm run test:e2e` suite and the existing owner-reviewed
  Windows Chromium visual screenshots rather than regenerating baselines.
- `npm audit --audit-level=low` remains a blocking frontend CI command.
- `frontend/e2e/slice-f-contrast-reflow.spec.ts` adds 320px CSS-viewport
  reflow checks for Triage/Evaluation and a browser-computed text-contrast
  sample (neutral/success/warning/danger badge states; minimum 4.5:1).
- These deterministic checks are **not** a comprehensive WCAG 2.2 AA audit.
  They do not cover every foreground/background combination, actual browser
  zoom, screen-reader traversal, or assistive-technology combinations.

## Human accessibility review required

- Inspect focus indication against surrounding surfaces in keyboard navigation.
- Test a screen reader's landmarks, headings, table headings, disclosure,
  error-status announcement and focused navigation at desktop and mobile sizes.
- Verify contrast with actual computed foreground/background colors, including
  transparent/color-mixed text states, on the changed views.
- Verify real 200% browser zoom and 320px narrow reflow beyond the automated 320px CSS-viewport smoke; document any horizontal
  scroll container that is intentionally local instead of page-level overflow.
- Check reduced motion, focus retention during asynchronous triage, and empty,
  loading, success, degraded and error states.

## Production release gate (not satisfied by CI)

The Hugging Face Space is a **separate Git repository**. The README and
`docs/deployment.md` contain a September 2026 historical verification,
not proof that the new GitHub SHA is currently live.

Before publishing updated portfolio captures:

1. Obtain Space write authorization and verify the currently deployed Space
   revision, container health and a tested rollback revision. Avoid paid
   compute and avoid writing secrets to public release evidence.
2. Build from an **exact reviewed GitHub commit**, and record the source SHA,
   artifact checksum, the resulting exact Space Git revision/image digest,
   and deployment timestamp. Do not infer source SHA from the UI appearance.
3. Check live `/ready` (HTTP 200 and 27 bounded demo records), `/triage`
   (seven trace stages with synthetic message), `/ingest` (403 for
   unauthenticated requests), and measured Evaluation limitations.
4. Verify landing page identity, 390/768/1440 layouts, navigation, keyboard
   flow, console errors, and mobile table text from the deployed revision.
5. Only then capture *live* screenshots, update release documentation, and
   mark the production section of Issue #89 complete. Record rollback steps.

No screenshot, saved deterministic fixture, or successful GitHub CI run by
itself certifies the live Space. Never claim semantic policy correctness or
human review without actual independently adjudicated evidence.

## Governance verification still pending

GitHub `main` is now protected by active ruleset `25716747`, requiring PRs,
up-to-date passing `backend`, `frontend`, `browser`, and `docker-smoke` checks,
and blocking deletion/force pushes. Read-back confirmed `protected: true`
after owner-authenticated configuration on October 23, 2026. The negative
check-enforcement test (pending/failing check prevents merge) is still
outstanding; Issue #84 remains open. See `docs/repository-governance.md`.
This repository protection does not authorize any Hugging Face deployment.

## Python advisory visibility (unresolved security gate)

The `backend` workflow adds a reporting-only
`pip-audit==2.10.1` scan for `requirements.production.txt`.
It is deliberately **nonblocking** because [Issue #93](https://github.com/Praciller/customer-support-rag-triage-agent/issues/93)
tracks 35 remaining advisory records in Pillow after [PR #94](https://github.com/Praciller/customer-support-rag-triage-agent/pull/94)
patched Datasets and fsspec compatibility. FastEmbed 0.9.0 still requires
`Pillow<13`, while reported Pillow fixes require version 13. The direct
forced-version attempt previously failed Docker/Windows dependency
resolution and was reverted. [PR #95](https://github.com/Praciller/customer-support-rag-triage-agent/pull/95)
adds text-ingress guards and static risk documentation, not a Pillow fix.
This does not grant a risk exception or attest deployed-image safety.
A clean audit must become a required gate once supported remediation is verified.
