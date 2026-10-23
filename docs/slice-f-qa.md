# Slice F: keyboard, semantic UI and release-evidence gates

Verified application baseline (October 23, 2026):
`2ebfe6b2b7f7259f0987d125837d81b826a7274a`, with all four
GitHub Actions push-CI jobs successful on that exact SHA
([run 39980406963](https://github.com/Praciller/customer-support-rag-triage-agent/actions/runs/39980406963)).
This historical checkpoint is **not** a dynamic latest-`main` status;
subsequent documentation commits need their own CI evidence.
The SHA describes the **GitHub repository**, not the Hugging Face Space.

## Offline, automated checks (no secrets or third-party API keys)

- Existing Playwright and Storybook checks remain authoritative for UI behavior.
- `frontend/e2e/slice-f-accessibility.spec.ts` adds repeatable smoke checks for a
  keyboard skip-navigation link at 390, 768 and 1440 pixels; mobile
  classification-table column semantics; degraded/ungrounded manual-review
  status; keyboard expansion of trace diagnostics; unavailable evaluation
  announcement; and reduced-motion CSS behavior.
- Continue the complete `npm run test:e2e` suite. Preserve owner-reviewed
  Windows Chromium screenshot baselines unless each proposed change has been
  separately inspected and explicitly accepted before merge.
- `npm audit --audit-level=low` remains a blocking frontend CI command.
- `frontend/e2e/slice-f-contrast-reflow.spec.ts` adds 320px CSS-viewport
  reflow checks for Triage/Evaluation and a browser-computed text-contrast
  sample (neutral/success/warning/danger badge states; minimum 4.5:1).
- `frontend/e2e/slice-f-axe.spec.ts` runs a browser-level axe-core WCAG A/AA
  regression scan of Triage and Evaluation at 390px and 1440px, with no
  rule suppression. It caught an actual contrast issue in the desktop sidebar
  demo footer, now corrected by lightening only that footer's small text.
- The owner **approved all four desktop screenshot baselines** for
  [PR #97](https://github.com/Praciller/customer-support-rag-triage-agent/pull/97)
  on October 23, 2026, before its protected-branch merge. The original
  baselines passed 11/11 with the previous CSS; the 1,329 changed RGB pixels
  per new desktop screenshot are confined to the same sidebar footer text box
  (x=28..190, width 163px, height 28px). The mobile baseline is unchanged.
  This explicit visual acceptance does **not** constitute WCAG certification.
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
`docs/deployment.md` contain a September 2026 historical verification.
The [October 23 live Space preflight](live-space-preflight-20261023.md)
confirmed the old Space revision `a2661562ff1a2a7b7f15e4b9145cb007c98444a5`
was still healthy; it does **not** prove the current GitHub SHA is live.

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

## Governance verification boundary

GitHub `main` is protected by active ruleset `25716747`, requiring PRs,
up-to-date passing `backend`, `frontend`, `browser`, and `docker-smoke` checks,
and blocking deletion/force pushes. Owner-authenticated readback confirmed
`protected: true` on October 23, 2026. A pending-check merge block was
observed on PR #96 while required checks ran. [Issue #84](https://github.com/Praciller/customer-support-rag-triage-agent/issues/84)
was closed after these verified checks; a deliberately failing-check test was
**not** performed. See `docs/repository-governance.md`.
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
