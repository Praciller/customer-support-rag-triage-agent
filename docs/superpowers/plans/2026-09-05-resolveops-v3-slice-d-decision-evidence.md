# ResolveOps v3 Slice D Decision and Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recompose the triage page so the human decision dominates the customer request, evidence is first-class but lighter, and technical metadata is subordinate without changing runtime semantics.

**Architecture:** Preserve `TriageView`’s existing `TriageResult` contract and production components, extracting bounded `DecisionWorkspace` and `TechnicalDetails` composition around the existing `TriageDecision` data. Replace the equal-weight result grid with a vertical semantic flow and make `CaseList` a reviewable evidence list; keep `TraceList`, backend, API, fixtures, and navigation unchanged.

**Tech Stack:** React 19, TypeScript, Vite, Vitest, React Testing Library, Storybook, Playwright, existing React Aria Components, self-hosted Geist typography, CSS tokens.

**Spec:** `docs/superpowers/specs/2026-09-05-resolveops-design-system-v3-design.md`

## Global Constraints

- Tailwind: `3.4.19` retained; no dependency upgrades or new packages.
- Primitive base: existing React Aria Components; native `<details>` is acceptable for technical metadata.
- Preserve backend/API/LangGraph/RAG/retrieval/evaluation semantics, fixtures, prompts, shell/navigation, Trace, and Evaluation.
- Keep human-review, grounding, escalation, provenance, and similarity-score meanings unchanged.
- Verify 390px, 768px, and 1440px with no horizontal overflow.
- Do not update visual baselines until intentional diffs are inspected.

### Task 1: Baseline and contract inventory

**Files:**
- Read: `frontend/src/features/triage/TriageView.tsx`, `frontend/src/features/triage/TriageView.test.tsx`, `frontend/src/features/triage/TriageDecision.tsx`, `frontend/src/components/evidence/CaseList.tsx`, `frontend/src/types/api.ts`, `frontend/src/test/fixtures.ts`
- Create: this plan file

- [ ] **Step 1: Verify the isolated base**

Run from the worktree root: `git branch --show-current; git rev-parse HEAD; git status --short`. Expected branch `feat/resolveops-v3-decision-evidence`, HEAD `2144f64f7f56c0057ade4327bdafcc6b800f1b00`, and no tracked changes before this plan.

- [ ] **Step 2: Run the fresh frontend baseline**

Run from `frontend`: `npm ci; npm audit; npm run lint; npm test; npm run build; npm run build-storybook; npm run test:e2e`. Record actual counts; stop for unrelated baseline failures.

- [ ] **Step 3: Run the backend safety baseline**

Run from root with the configured project Python: `ruff check src tests; ruff format --check src tests; python -m pytest`. Run adversarial evaluation to a temporary non-committed report and `make demo`; remove only that temporary report and generated files caused by the command.

### Task 2: Decision behavior tests first

**Files:**
- Test: `frontend/src/features/triage/TriageView.test.tsx`
- Test: `frontend/src/features/triage/TriageDecision.test.tsx` if the existing component has a focused test seam

- [ ] **Step 1: Add failing public-interface assertions**

Through rendered TriageView, assert completed grounded results expose a `primary-decision` region with the existing next action, suggested response, grounding text/score, urgency text, and evidence heading; assert technical values are under a named Technical details disclosure rather than the primary decision heading.

- [ ] **Step 2: Add failing state assertions**

Assert high-risk results retain visible escalation/manual-review text and escalation reason; ungrounded/degraded results retain manual-review semantics; a null result shows compact guidance and no fake next action or response.

- [ ] **Step 3: Run the focused tests and confirm red**

Run: `npm test -- --run src/features/triage/TriageView.test.tsx`. Expected: new hierarchy/state assertions fail against the current equal-weight composition.

### Task 3: DecisionWorkspace and technical hierarchy

**Files:**
- Create or modify: `frontend/src/features/triage/DecisionWorkspace.tsx`
- Modify: `frontend/src/features/triage/TriageDecision.tsx`, `frontend/src/features/triage/TriageView.tsx`
- Modify: bounded triage styles in `frontend/src/styles/features.css`

- [ ] **Step 1: Implement the primary decision surface**

Compose customer request, recommended action, suggested response, grounding, urgency, and escalation inside one `primary-decision` region using existing result fields and wording. Keep action text at least 14px and preserve visible non-color status semantics.

- [ ] **Step 2: Implement compact null/loading state**

Render purposeful pre-run guidance such as “Run triage to generate a recommended action and evidence”; do not fabricate result content or reserve excessive empty-card height.

- [ ] **Step 3: Move runtime fields into TechnicalDetails**

Use a native `<details>` disclosure named “Technical details”, rendering only present provider/model/cache/latency/normalized-input fields with technical mono styling. Preserve existing metadata values and avoid secrets, URLs, prompts, or exceptions.

- [ ] **Step 4: Run focused tests green**

Run the TriageView test file and confirm all decision/state assertions pass.

### Task 4: Evidence list redesign

**Files:**
- Modify: `frontend/src/components/evidence/CaseList.tsx`
- Modify: `frontend/src/features/triage/TriageView.tsx`
- Modify: bounded evidence styles in `frontend/src/styles/features.css`
- Test: `frontend/src/components/evidence/CaseList.test.tsx` or the existing evidence test file

- [ ] **Step 1: Add failing evidence tests**

Assert supported real fields only: reference identity, relevance/similarity when present, intent/category, source/provenance when present, excerpt/content, and the empty-evidence state. Assert the single visible caveat that retrieved cases are evidence/context, not support policy.

- [ ] **Step 2: Implement lighter semantic evidence rows**

Render a semantic list of subtle repeated items rather than equal-weight dashboard cards. Keep score values as similarity/relevance with Geist Mono/tabular numerals; do not relabel as confidence or invent provenance.

- [ ] **Step 3: Place evidence after the decision and before trace**

Change only TriageView composition so the order is customer request → DecisionWorkspace → evidence → existing trace → TechnicalDetails context, with no TraceList internals changed.

- [ ] **Step 4: Run evidence and Triage tests green**

Run the focused evidence and Triage test files.

### Task 5: Responsive composition and accessibility

**Files:**
- Modify: bounded triage styles in `frontend/src/styles/features.css`
- Test: `frontend/e2e/triage.spec.ts`

- [ ] **Step 1: Add semantic DOM hierarchy assertions**

For the real Card not arrived flow, assert decision region precedes evidence, evidence precedes trace, and Technical details follows trace or is visibly subordinate adjacent context. Assert high-risk escalation and reason remain visible.

- [ ] **Step 2: Add responsive overflow and visual-order assertions**

At 390px, 768px, and 1440px assert document width does not overflow; at 390px assert decision bounding-box Y is before evidence and evidence before trace, and suggested response/evidence excerpts remain visible without clipping.

- [ ] **Step 3: Implement responsive styles**

Use the existing breakpoints and semantic surfaces to keep the primary action readable, allow response/evidence wrapping, and keep metadata subordinate. Do not alter shell, navigation, trace internals, or Evaluation CSS.

- [ ] **Step 4: Run focused browser tests**

Run: `npx playwright test e2e/triage.spec.ts`.

### Task 6: Storybook catalog

**Files:**
- Create/modify: `frontend/src/features/triage/DecisionWorkspace.stories.tsx`
- Create/modify: `frontend/src/components/evidence/CaseList.stories.tsx`

- [ ] **Step 1: Add production-component stories**

Expose Empty, Grounded, Escalated, and real Ungrounded/Manual Review states from existing deterministic fixtures. Add Evidence/ThreeResults and Evidence/Empty using the production evidence component.

- [ ] **Step 2: Add desktop/mobile composition coverage**

Provide explicit 390px viewport coverage for DecisionWorkspace or the Triage composition and verify the same information order without fake markup.

- [ ] **Step 3: Build Storybook**

Run: `npm run build-storybook`. Any a11y issue in changed stories is a blocker unless it is a documented false positive.

### Task 7: Visual regression and owner evidence

**Files:**
- Modify only reviewed Triage snapshots under `frontend/e2e/visual.spec.ts-snapshots/`
- Temporary external capture script: outside the repository; delete after capture

- [ ] **Step 1: Run visual tests without updating**

Run: `npx playwright test e2e/visual.spec.ts`. Inspect every expected/actual/diff; Evaluation baseline changes are suspicious and require investigation.

- [ ] **Step 2: Refresh only intentional Triage baselines**

Run `npx playwright test e2e/visual.spec.ts --update-snapshots` only after review, then record exact changed PNGs and rerun `npm run test:e2e`.

- [ ] **Step 3: Capture external owner archive**

Capture the seven required grounded/escalated desktop, tablet, and mobile states with page identity, completed workflow, no loading state, and zero console errors/warnings/page errors/failed requests. Create `00-contact-sheet.jpg`, `metadata/review-notes.md`, and a readable `resolveops-v3-slice-d-review.zip` containing only screenshots/metadata/contact sheet.

### Task 8: Final matrix, scrutiny, PR, and final-head CI

**Files:**
- Modify: no source files unless a verified in-scope defect remains

- [ ] **Step 1: Run the complete frontend matrix**

Run fresh: `npm ci; npm audit; npm run lint; npm test; npm run build; npm run build-storybook; npm run test:e2e`. Record counts and Button CSS verification.

- [ ] **Step 2: Run backend safety checks**

Run Ruff, format check, pytest, adversarial evaluation to a temporary report, and `make demo`; delete temporary artifacts and confirm no backend/API/data changes.

- [ ] **Step 3: Review final diff from an outsider perspective**

Trace TriageView → DecisionWorkspace → evidence → TraceList → TechnicalDetails, verify no card wall, no semantic relabeling, no shell/Trace/Evaluation/backend changes, and no private paths/secrets in tracked files.

- [ ] **Step 4: Commit and open the bounded PR**

Use focused commits, push `feat/resolveops-v3-decision-evidence`, open PR `feat: redesign ResolveOps decision workspace and evidence` against `main`, reference #76 and #69, and report only verified claims.

- [ ] **Step 5: Wait for final-head CI**

Record the new final-head run ID and require backend, frontend, and browser success before stopping. Do not merge, close #76, or begin Slice E.
