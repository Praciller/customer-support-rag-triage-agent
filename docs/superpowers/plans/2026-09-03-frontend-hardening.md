# Frontend Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Keep write work sequential; use fresh read-only review after meaningful slices.

**Goal:** Decompose the monolithic React frontend into app/feature/domain-component boundaries, then implement the approved ResolveOps design system without changing the backend API contract.

**Architecture:** First perform behavior-preserving extraction under existing tests. Then introduce reusable semantic primitives and CSS design tokens. Business semantics such as grounding, escalation, fallback, and evidence integrity remain in feature/domain components rather than generic visual primitives.

**Tech Stack:** React 19, TypeScript, Vite, Vitest, Testing Library, Lucide React, Recharts, CSS custom properties.

**Spec:** `docs/superpowers/specs/2026-09-03-sdlc-professional-hardening-design.md`

## Global Constraints

- Preserve the current endpoint and TypeScript response contracts.
- Preserve current deterministic demo fixtures and public copy boundaries.
- Do not add React Router, a global state-management library, a component mega-library, or a framework migration.
- Status must be understandable without color alone.
- The UI hierarchy is customer message → decision/human action → grounding/escalation → evidence → trace/runtime metadata.
- No page-level horizontal overflow at 390px, 768px, or 1440px.

---

## Target file map

```text
frontend/src/
  app/
    App.tsx
    navigation.ts
    shell/AppShell.tsx
    shell/Sidebar.tsx
    shell/Topbar.tsx
  features/
    overview/OverviewView.tsx
    triage/TriageView.tsx
    triage/TicketComposer.tsx
    triage/TriageDecision.tsx
    triage/TriageMetadata.tsx
    search/SearchView.tsx
    trace/TraceView.tsx
    evaluation/EvaluationView.tsx
    evaluation/EvaluationChart.tsx
    dataset/DatasetView.tsx
    providers/ProviderView.tsx
  components/
    ui/Badge.tsx
    ui/Button.tsx
    ui/EmptyState.tsx
    ui/ErrorNotice.tsx
    ui/Field.tsx
    ui/Panel.tsx
    ui/StatusIndicator.tsx
    evidence/CaseList.tsx
    trace/TraceList.tsx
  lib/api.ts
  types/api.ts
  styles/tokens.css
  styles/base.css
  styles/components.css
  styles/features.css
  test/fixtures.ts
  App.test.tsx
  main.tsx
```

Existing file ownership during migration:
- `App.tsx` → orchestration plus all current view implementations; split incrementally.
- `components.tsx` → Badge, MetricCard, CaseList, TraceList, ErrorNotice; replace with focused files.
- `api.ts` → move unchanged to `lib/api.ts` and update imports.
- `types.ts` → move unchanged to `types/api.ts` and update imports.
- `EvaluationChart.tsx` → move to evaluation feature.
- `styles.css` → split only after component boundaries are stable.

---

### Task 1: Protect current behavior with reusable test fixtures

**Files:**
- Create: `frontend/src/test/fixtures.ts`
- Modify: `frontend/src/App.test.tsx`

**Interfaces:**
- Produces: `makeTriageResult()` and `makeEvaluation()` fixture factories used by focused tests and later Storybook stories.

- [ ] **Step 1: Write tests that import fixture factories before they exist**

At the top of `App.test.tsx`, add:

```ts
import { makeEvaluation, makeTriageResult } from "./test/fixtures";
```

Replace the large inline triage/evaluation objects with:

```ts
vi.mocked(api.triage).mockResolvedValue(makeTriageResult());
vi.mocked(api.evaluation).mockResolvedValue(makeEvaluation());
```

- [ ] **Step 2: Run the focused test and confirm red state**

```bash
cd frontend
npm test -- --run src/App.test.tsx
```

Expected: FAIL because `./test/fixtures` does not exist.

- [ ] **Step 3: Implement deterministic fixture factories**

Create `frontend/src/test/fixtures.ts` exporting typed functions. `makeTriageResult()` must return the existing delivery fixture with seven trace nodes and `18.4` total latency. `makeEvaluation()` must return the current deterministic mock values already asserted in `App.test.tsx`. Import types from `../types` until Task 4 moves them.

Function signatures:

```ts
export function makeTriageResult(): TriageResult
export function makeEvaluation(): Evaluation
```

- [ ] **Step 4: Run tests/lint/build**

```bash
npm test -- --run src/App.test.tsx
npm run lint
npm run build
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/test/fixtures.ts frontend/src/App.test.tsx
git commit -m "test: centralize frontend deterministic fixtures"
```

---

### Task 2: Extract navigation and application shell

**Files:**
- Create: `frontend/src/app/navigation.ts`
- Create: `frontend/src/app/shell/AppShell.tsx`
- Create: `frontend/src/app/shell/Sidebar.tsx`
- Create: `frontend/src/app/shell/Topbar.tsx`
- Create: `frontend/src/app/App.tsx`
- Modify: `frontend/src/main.tsx`
- Modify: `frontend/src/App.test.tsx`

**Interfaces:**
- `navigation.ts` exports `View` and `nav`.
- `AppShell` receives `view`, `setView`, `apiStatus`, and `children`.
- Root `app/App.tsx` owns current view state, health check, triage request state, and feature composition.

- [ ] **Step 1: Add shell-level test assertions before extraction**

Keep these App expectations explicit:

```ts
expect(screen.getByRole("navigation", { name: /main navigation/i })).toBeInTheDocument();
expect(screen.getByText(/deterministic demo/i)).toBeInTheDocument();
expect(screen.getByText(/api connected/i)).toBeInTheDocument();
```

Use `findByText` for API connected because health is async.

- [ ] **Step 2: Run App test green before refactor**

```bash
npm test -- --run src/App.test.tsx
```

Expected: PASS.

- [ ] **Step 3: Create `navigation.ts`**

Move the existing `View` union and nav definitions unchanged. Export:

```ts
export type View = "overview" | "triage" | "search" | "trace" | "evaluation" | "dataset" | "providers";
export const nav: { id: View; label: string; icon: typeof LayoutDashboard }[] = [...];
```

- [ ] **Step 4: Extract Sidebar and Topbar**

`Sidebar` renders brand, eyebrow, nav buttons, deterministic-demo system card. `Topbar` renders breadcrumb/title and API badge. Preserve existing accessible names and text.

- [ ] **Step 5: Create `AppShell` composition**

Signature:

```ts
export function AppShell(props: {
  view: View;
  setView: (view: View) => void;
  apiStatus: "checking" | "connected" | "unavailable";
  children: React.ReactNode;
}): React.ReactElement
```

- [ ] **Step 6: Move root component to `app/App.tsx` and update `main.tsx`**

`main.tsx` imports `App` from `./app/App`. Do not change runtime behavior.

- [ ] **Step 7: Run verification**

```bash
npm test
npm run lint
npm run build
```

Expected: PASS with the same user-visible assertions.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/app frontend/src/main.tsx frontend/src/App.test.tsx
git commit -m "refactor: extract frontend application shell"
```

---

### Task 3: Extract feature views one bounded slice at a time

**Files:**
- Create the seven feature view files in the target map.
- Move `EvaluationChart.tsx` to `features/evaluation/EvaluationChart.tsx`.
- Modify: `frontend/src/app/App.tsx`
- Add focused tests as files are extracted, e.g. `features/triage/TriageView.test.tsx`, `features/search/SearchView.test.tsx`, `features/evaluation/EvaluationView.test.tsx`.

**Interfaces:**
- `TriageView` consumes `message`, setter, `run`, loading/result/error.
- `TraceView` consumes `TraceStep[]`.
- Search/Evaluation/Dataset/Provider views call the shared API module exactly as they do today.

- [ ] **Step 1: Extract OverviewView and verify**

Move existing JSX unchanged; run:

```bash
npm test -- --run src/App.test.tsx
```

Then commit `refactor: extract overview feature`.

- [ ] **Step 2: Write triage-focused behavior tests before extracting TriageView**

Test with `makeTriageResult()` that:
- customer message textbox is labeled;
- `Run triage` is enabled for non-empty input;
- result shows normalized message, next action, grounding, citation integrity, evidence, and seven-node trace;
- an escalated result includes visible `Escalate` text and escalation reason.

Use Testing Library role/label/text queries only.

- [ ] **Step 3: Extract triage feature components**

Create:
- `TriageView.tsx` for feature composition;
- `TicketComposer.tsx` for input/examples/run action;
- `TriageDecision.tsx` for intent/urgency/action/response/escalation/grounding;
- `TriageMetadata.tsx` for provider/model/cache/fallback/degraded/latency metadata.

Business rules remain data-driven from `TriageResult`; no new grounding/escalation decisions are invented in UI code.

- [ ] **Step 4: Run triage tests plus App regression**

```bash
npm test -- --run src/features/triage/TriageView.test.tsx src/App.test.tsx
npm run lint
npm run build
```

Expected: PASS. Commit `refactor: extract triage feature`.

- [ ] **Step 5: Extract Search and Trace with focused tests**

Search test preserves accessible textbox `Search support tickets` and combobox `Intent filter`. Trace test verifies empty state and numbered seven-node sequence using a deterministic fixture.

Run focused tests after each extraction; commit Search and Trace separately.

- [ ] **Step 6: Extract Evaluation, Dataset, Provider views**

Evaluation test preserves `deterministic mock`, precision column header, and limitation copy. Dataset/Provider tests cover loading/error/success states already present in the current UI.

- [ ] **Step 7: Run full frontend baseline**

```bash
npm test
npm run lint
npm run build
```

Expected: PASS; `app/App.tsx` is now orchestration/composition rather than containing feature implementations.

---

### Task 4: Move API/types to stable shared boundaries

**Files:**
- Move: `frontend/src/api.ts` → `frontend/src/lib/api.ts`
- Move: `frontend/src/types.ts` → `frontend/src/types/api.ts`
- Update imports across `frontend/src/**`.

**Interfaces:**
- `api` object method names and endpoint paths remain unchanged.
- Existing exported public response types retain names/properties.

- [ ] **Step 1: Add a no-contract-change guard**

Before moving, run:

```bash
cp frontend/src/api.ts /tmp/api.before.ts
cp frontend/src/types.ts /tmp/types.before.ts
```

- [ ] **Step 2: Move files and update imports only**

Do not edit endpoint strings or type property names during the move.

- [ ] **Step 3: Compare content excluding import-path-only changes**

Review:

```bash
git diff -- frontend/src/lib/api.ts frontend/src/types/api.ts frontend/src
```

Reject any accidental endpoint/type semantic change.

- [ ] **Step 4: Run full frontend verification**

```bash
cd frontend
npm test
npm run lint
npm run build
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src
git commit -m "refactor: centralize frontend API contracts"
```

---

### Task 5: Introduce semantic UI/domain component boundaries

**Files:**
- Create UI files from target map.
- Create: `components/evidence/CaseList.tsx`
- Create: `components/trace/TraceList.tsx`
- Remove old `components.tsx` after imports reach zero.

**Interfaces:**

```ts
export type StatusTone = "neutral" | "success" | "warning" | "danger";
```

`Badge` and `StatusIndicator` accept `tone` plus visible children/label; they never decide grounding/escalation themselves.

- [ ] **Step 1: Write primitive component tests**

Tests must verify:
- Button disabled/loading states expose accessible button semantics;
- StatusIndicator renders visible label for every tone;
- ErrorNotice uses `role="alert"`;
- EmptyState has visible descriptive text.

- [ ] **Step 2: Implement minimal primitives and run focused tests**

```bash
npm test -- --run src/components/ui
```

Expected: PASS.

- [ ] **Step 3: Move CaseList and TraceList into domain component folders**

Preserve data semantics. Trace list continues to display component/provider/cache/fallback/degraded metadata and durations.

- [ ] **Step 4: Replace imports and remove `components.tsx` only when unused**

```bash
grep -R 'from "./components"\|from "../components"' frontend/src || true
```

Expected before deletion: no old import matches.

- [ ] **Step 5: Run full verification and commit**

```bash
npm test
npm run lint
npm run build
git add frontend/src
git commit -m "refactor: establish semantic UI components"
```

---

### Task 6: Implement ResolveOps design tokens and style split

**Files:**
- Create: `frontend/src/styles/tokens.css`
- Create: `frontend/src/styles/base.css`
- Create: `frontend/src/styles/components.css`
- Create: `frontend/src/styles/features.css`
- Modify: `frontend/src/main.tsx`
- Remove: `frontend/src/styles.css` after migration.

**Interfaces:**
- CSS custom property names mirror `DESIGN.md` token names with `--color-*`, `--space-*`, `--radius-*`, and `--motion-*` prefixes.

- [ ] **Step 1: Add token file from `DESIGN.md` v2**

Minimum variables:

```css
:root {
  --color-canvas: oklch(0.975 0.006 245);
  --color-surface: oklch(0.995 0.004 245);
  --color-surface-muted: oklch(0.948 0.010 245);
  --color-foreground: oklch(0.245 0.025 250);
  --color-foreground-muted: oklch(0.510 0.025 250);
  --color-border: oklch(0.875 0.018 245);
  --color-primary: oklch(0.555 0.180 258);
  --color-success: oklch(0.565 0.125 154);
  --color-warning: oklch(0.700 0.145 76);
  --color-danger: oklch(0.560 0.190 28);
  --focus-ring: 0 0 0 3px color-mix(in oklch, var(--color-primary) 28%, transparent);
}
```

- [ ] **Step 2: Split existing styles by responsibility without redesigning selectors in the same step**

Move global/reset/layout foundations to `base.css`, reusable component rules to `components.css`, feature/page layout to `features.css`. Import in `main.tsx` in this order: tokens → base → components → features.

- [ ] **Step 3: Replace repeated hard-coded palette/spacing values with tokens**

Do not alter semantic status mapping. Provider/runtime metadata remains lower contrast/weight than decision/evidence.

- [ ] **Step 4: Encode focus/reduced-motion/responsive rules**

Include:

```css
:focus-visible { outline: none; box-shadow: var(--focus-ring); }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; }
}
```

At narrow widths, stack decision before evidence/trace and ensure flexible children use `min-width: 0` where needed.

- [ ] **Step 5: Add a static hard-coded-color guard for migrated styles**

Run:

```bash
python - <<'PY'
from pathlib import Path
for p in Path('frontend/src/styles').glob('*.css'):
    text = p.read_text(encoding='utf-8')
    if p.name != 'tokens.css':
        assert 'oklch(' not in text, f'hard-coded design color in {p}'
print('style token guard OK')
PY
```

Expected: `style token guard OK`.

- [ ] **Step 6: Run frontend verification and commit**

```bash
cd frontend
npm test
npm run lint
npm run build
git add src

git commit -m "feat: implement ResolveOps design system"
```

---

## Phase review gate

Run:

```bash
cd frontend
npm test
npm run lint
npm run build
```

Then inspect the diff for accidental API/type/business-rule changes. Independent review must specifically check accessibility semantics, evidence/grounding copy, component boundaries, hard-coded styling, and scope creep. Browser/responsive proof is added in the next plan rather than claimed here.