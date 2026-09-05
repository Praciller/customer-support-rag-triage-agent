# ResolveOps v3 Slice B Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Permanently establish the approved ResolveOps v3 frontend foundation: Geist typography, semantic tokens, React Aria/shadcn Button primitives, compatibility adapters, and a small Storybook catalog without redesigning product pages.

**Architecture:** Keep Tailwind 3 and the existing ResolveOps OKLCH palette. Add the verified `@/*` alias contract, self-hosted Fontsource Geist assets, and shadcn React Aria source under `src/components/aria-ui`; preserve the existing domain-facing `src/components/ui/Button.tsx` API as an adapter. Keep generated registry CSS subordinate to ResolveOps-owned tokens.

**Tech Stack:** React 19, Vite 8, TypeScript 5.7, Tailwind 3.4.19, Storybook 10.6, Vitest, Playwright, shadcn CLI 4.21.0, React Aria Components 1.21.1, Fontsource Geist 5.3.0.

**Spec:** `docs/superpowers/specs/2026-09-05-resolveops-design-system-v3-design.md`

## Global Constraints

- Do not migrate Tailwind 4 or add `@tailwindcss/vite`.
- Do not change backend, API, LangGraph, RAG, evaluation semantics, deployment, shell, navigation, or page composition.
- Use `@fontsource-variable/geist@5.3.0` and `@fontsource-variable/geist-mono@5.3.0`; no runtime font CDN.
- Use shadcn React Aria (`--base aria`) and keep generated source separate from `src/components/ui/Button.tsx` on Windows.
- Preserve the existing ResolveOps OKLCH palette and human-review/evidence boundaries.
- Run tests before visual snapshot updates; update only reviewed foundation-driven baselines.

---

### Task 1: Clean baseline and plan verification

**Files:** Read repository and frontend files listed in the Slice B brief; modify only this plan initially.

- [ ] Verify branch, exact base SHA, and clean status.
- [ ] Run `npm ci`, `npm audit`, lint, unit tests, build, Storybook build, and full Playwright E2E; record counts.
- [ ] Stop if the baseline is unexpectedly broken.

### Task 2: Install the verified foundation packages

**Files:** `frontend/package.json`, `frontend/package-lock.json`, `frontend/tsconfig.json`, `frontend/tsconfig.app.json`, `frontend/vite.config.ts`.

- [ ] Add the root/app `@/*` TypeScript paths while preserving project references and compiler options.
- [ ] Add Vite `resolve.alias` using `path.resolve(__dirname, "./src")`, preserving React, proxy, and Vitest configuration.
- [ ] Install only the exact Geist packages and the verified React Aria/shadcn Button dependency set required by the generated primitive.
- [ ] Run `npm run build` before proceeding.

### Task 3: Add self-hosted Geist imports and tokens

**Files:** `frontend/src/main.tsx`, `frontend/src/styles/tokens.css`, `frontend/tailwind.config.js`.

- [ ] Import Geist Sans and Geist Mono WOFF2 CSS before project styles.
- [ ] Replace Inter-first UI tokens with the approved Geist fallback stacks.
- [ ] Map Tailwind `sans` and `mono` families to the semantic Geist tokens/families without changing unrelated theme values.
- [ ] Build and inspect emitted local font assets; confirm no Google Fonts URLs.

### Task 4: Establish DESIGN.md v3 foundation rules

**Files:** `DESIGN.md`.

- [ ] Record v3 foundation status, Geist families, Tailwind 3 retention, shadcn source ownership, React Aria base, and alias architecture.
- [ ] Document semantic token rules, type roles, technical numerals, density, surface hierarchy, focus behavior, direct labels, and generated-default boundaries.
- [ ] Distinguish implemented foundation from future Slice C/D/E page migration; do not claim page redesigns are implemented.

### Task 5: Implement semantic token and utility mapping

**Files:** `frontend/src/styles/tokens.css`, `frontend/src/styles/base.css`, `frontend/tailwind.config.js`, `frontend/src/lib/utils.ts`.

- [ ] Add only required surface, foreground, border, state, selected, disabled, type-role, and technical-number tokens using the existing palette.
- [ ] Preserve Tailwind 3 directives, focus-visible behavior, reduced motion, and existing scale compatibility.
- [ ] Add a small reusable technical text/numeric class with Geist Mono and tabular numerals.
- [ ] Run lint, unit, and build.

### Task 6: Initialize controlled shadcn React Aria configuration

**Files:** `frontend/components.json`, generated `frontend/src/lib/utils.ts`; inspect all generated diffs.

- [ ] Run `npx shadcn@4.21.0 init --base aria` only after aliases build successfully.
- [ ] Retain `aria-nova`/React Aria metadata but remove generated CSS that conflicts with ResolveOps tokens or Tailwind 3.
- [ ] Set the UI alias to `@/components/aria-ui` and preserve aliases consistently.
- [ ] Confirm no Tailwind 4 packages or CSS entry are introduced.

### Task 7: Add the React Aria Button primitive

**Files:** `frontend/src/components/aria-ui/button.tsx`.

- [ ] Run `npx shadcn@4.21.0 add button` and verify imports from `react-aria-components`.
- [ ] Keep the primitive in `aria-ui` so it cannot collide with uppercase `ui/Button.tsx` on Windows.
- [ ] Adapt generated variants/classes to the existing Tailwind 3 semantic mapping without copying an unreviewed theme.
- [ ] Run typecheck/build.

### Task 8: Write tests first, then implement the compatibility adapter

**Files:** `frontend/src/components/ui/Button.tsx`, existing/new Button tests.

- [ ] Add failing tests for accessible name, press/click, keyboard activation, primary/secondary variants, disabled, loading, `aria-busy`, and class composition.
- [ ] Run the focused tests and confirm the expected failures.
- [ ] Implement the adapter using the React Aria primitive while preserving `variant`, `disabled`, `loading`, `children`, and `className` callers.
- [ ] Run focused tests, then the complete Vitest suite.

### Task 9: Add foundation Storybook catalog

**Files:** New/updated stories under `frontend/src/components` or `frontend/.storybook` only as needed.

- [ ] Add `Foundations/Typography` showing page title, section title, primary decision, body, control, metadata, Geist Mono, and tabular metrics.
- [ ] Add `Foundations/Colors`, `Foundations/Surfaces`, and `Foundations/Spacing` with Canvas, Workspace, primary decision, standard, subtle, and technical surfaces.
- [ ] Update `UI/Button` stories for primary, secondary, disabled, loading, long label, and focus-visible states.
- [ ] Run Storybook a11y checks and static build.

### Task 10: Browser font and semantic verification

**Files:** Temporary scripts outside the repository; no committed screenshots yet.

- [ ] Run the local branch app and inspect computed `font-family` for body, heading, Button, and technical sample.
- [ ] Confirm Geist Sans on body/Button, Geist Mono on technical text, visible focus, disabled semantics, and no console/page errors.
- [ ] Run non-visual semantic Playwright tests before visual baseline review.

### Task 11: Review and refresh approved visual baselines

**Files:** Existing affected visual baseline PNGs only after review.

- [ ] Run visual tests without snapshot updates and inspect every failure/diff.
- [ ] Classify each difference as foundation-only, unrelated regression, or unknown.
- [ ] Fix in-scope regressions without redesigning pages; stop on unknown/unrelated changes.
- [ ] Update only approved foundation-driven snapshots, then run the full Playwright suite.

### Task 12: Capture external owner review ZIP

**Files:** External directory `C:/Users/pakon/OneDrive/Desktop/resolveops-v3-slice-b-review`; no repository artifacts.

- [ ] Capture local branch typography, surfaces, Button states, triage desktop, evaluation desktop, and triage mobile screenshots.
- [ ] Include safe metadata stating branch SHA, packages, capture method, and `LOCAL SLICE B REVIEW / NOT DEPLOYMENT EVIDENCE`.
- [ ] Validate dimensions/content, create a labeled contact sheet, zip screenshots/metadata only, and verify archive readability.

### Task 13: Complete backend/frontend/security gates

**Files:** No additional production files.

- [ ] Run fresh frontend matrix: ci, audit, lint, unit, build, Storybook, full E2E.
- [ ] Run backend Ruff, format, pytest, adversarial evaluation with a temporary report, and `make demo`; delete only temporary output.
- [ ] Review dependency diff, secret/path scan, `Inter` references, and complete git scope checks.
- [ ] Run an independent scrutinize pass over the final diff.

### Task 14: Commit, PR, and final CI

**Files:** All approved Slice B files only.

- [ ] Commit the plan and implementation in small logical commits without unrelated changes.
- [ ] Push `feat/resolveops-v3-foundation` and open one PR titled `feat: establish ResolveOps v3 design foundation`, referencing #72 and #69.
- [ ] Wait for final-head backend, frontend, and browser checks; confirm Storybook success and full Playwright pass.
- [ ] Stop before merge and before Slice C.
