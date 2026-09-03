# SDLC Professional Hardening — Implementation Plan Index

Approved design: [`../specs/2026-09-03-sdlc-professional-hardening-design.md`](../specs/2026-09-03-sdlc-professional-hardening-design.md)

Execution order is sequential. Each plan must pass its review gate before the next plan begins.

1. [`2026-09-03-context-guardrails.md`](2026-09-03-context-guardrails.md) — root agent context, ADRs, `DESIGN.md` v2, GitHub review templates, Definition of Done. Tracks phase issue #11.
2. [`2026-09-03-frontend-hardening.md`](2026-09-03-frontend-hardening.md) — behavior-preserving frontend decomposition, shared contracts, semantic components, ResolveOps tokens/styles. Tracks phase issue #12.
3. [`2026-09-03-ui-verification-ci.md`](2026-09-03-ui-verification-ci.md) — Storybook 10.x, Playwright 1.61+ deterministic E2E, visual/responsive regression, CI evidence gates. Tracks phase issue #13.
4. [`2026-09-03-deployment-evidence.md`](2026-09-03-deployment-evidence.md) — canonical container proof, owner-authenticated Space synchronization, live verification, screenshots, README/deployment evidence, final security/claim review. Tracks phase issue #14.

Program epic: #10.

## Execution policy

- Keep implementation write-heavy work bounded and sequential.
- Start each slice from the approved spec plus only the relevant plan/context files.
- Use tests/acceptance criteria before behavior changes and commit each independently reviewable deliverable.
- Use Matt Pocock and Thananon/9arm skills progressively when the current task matches; do not load every skill into every session.
- Use an independent read-only review after major slices.
- `/graftify` remains excluded until its canonical source, maintainer, license, and actual skill contents are verified.
- Stop rather than silently widen scope when a public backend contract, evidence/security invariant, unplanned dependency/framework, external credential, unrelated failing test, or owner-authenticated deployment action becomes necessary.