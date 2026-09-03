# UI Verification and CI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Keep browser/CI changes sequential because configuration and snapshots share state.

**Goal:** Add an executable Storybook component catalog, deterministic Playwright acceptance tests, selected visual regression baselines, and CI artifacts without weakening existing backend/frontend gates.

**Architecture:** Storybook documents isolated reusable/domain states; Playwright exercises the real deterministic FastAPI + Vite integration for critical flows. Visual baselines cover only high-signal screens. GitHub Actions keeps backend, frontend, and browser failures separately diagnosable.

**Tech Stack:** Storybook 10.x React/Vite, `@storybook/addon-a11y`, Playwright Test 1.61+, Chromium, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-03-sdlc-professional-hardening-design.md`

## Global Constraints

- Current authoritative setup references are Storybook v10.2.x and Playwright v1.61.x official docs; if implementation resolves newer majors, inspect migration output before accepting it.
- Browser acceptance uses the real deterministic application path, not endpoint mocks, except the explicit API-unavailable scenario.
- No external GenAI credential is allowed in Storybook, E2E, visual regression, or CI.
- Use role/label/accessible-name locators; no arbitrary sleeps.
- Existing backend Ruff/pytest/adversarial/demo checks and frontend lint/Vitest/build checks remain intact.
- Visual baselines are updated only after explicit diff review.

---

### Task 1: Initialize Storybook for React/Vite

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/package-lock.json`
- Create/modify generated files: `frontend/.storybook/main.ts`, `frontend/.storybook/preview.ts`

**Interfaces:**
- Produces scripts `storybook` and `build-storybook`.
- Story patterns include `src/**/*.stories.@(ts|tsx)`.

- [ ] **Step 1: Run current frontend baseline**

```bash
cd frontend
npm ci
npm run lint
npm test
npm run build
```

Expected: PASS before Storybook setup.

- [ ] **Step 2: Initialize current official Storybook**

```bash
npx storybook@latest init
```

When the CLI detects the existing project, accept React/Vite. Do not allow it to replace Vite, React, or application source files.

- [ ] **Step 3: Add accessibility addon if the initializer did not**

```bash
npm install --save-dev @storybook/addon-a11y
```

Ensure `.storybook/main.ts` uses `@storybook/react-vite` and includes:

```ts
addons: ["@storybook/addon-a11y"]
```

- [ ] **Step 4: Normalize package scripts**

Ensure `frontend/package.json` contains:

```json
{
  "scripts": {
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build"
  }
}
```

Preserve existing `dev`, `build`, `test`, and `lint` scripts.

- [ ] **Step 5: Import application styles in Storybook preview**

`frontend/.storybook/preview.ts` imports the same four style files as the application in this order:

```ts
import "../src/styles/tokens.css";
import "../src/styles/base.css";
import "../src/styles/components.css";
import "../src/styles/features.css";
```

Set a default light background matching the canvas token; do not duplicate the token value in component stories.

- [ ] **Step 6: Build Storybook and verify no application regression**

```bash
npm run build-storybook
npm run lint
npm test
npm run build
```

Expected: all PASS and `storybook-static/` is generated locally but not committed.

- [ ] **Step 7: Commit**

```bash
git add package.json package-lock.json .storybook
git commit -m "test: add Storybook component workshop"
```

---

### Task 2: Add reusable UI stories with interaction/a11y-friendly semantics

**Files:**
- Create stories beside UI components under `frontend/src/components/ui/*.stories.tsx`.

**Interfaces:**
- Stories consume semantic component props only; no backend calls.

- [ ] **Step 1: Add Button stories**

`Button.stories.tsx` must expose Primary, Secondary, Disabled, and Loading states. A CSF3 interaction story uses Storybook 10's `storybook/test` API:

```tsx
import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, fn } from "storybook/test";
import { Button } from "./Button";

const meta = {
  component: Button,
  args: { children: "Run triage", onClick: fn() },
} satisfies Meta<typeof Button>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {};
export const Secondary: Story = { args: { variant: "secondary" } };
export const Disabled: Story = { args: { disabled: true } };
export const Loading: Story = { args: { loading: true } };
export const Clickable: Story = {
  play: async ({ args, canvas, userEvent }) => {
    await userEvent.click(canvas.getByRole("button", { name: /run triage/i }));
    await expect(args.onClick).toHaveBeenCalledOnce();
  },
};
```

- [ ] **Step 2: Add status/error/empty/field stories**

Required stories:
- Badge/StatusIndicator: Neutral, Success, Warning, Danger with visible labels.
- ErrorNotice: controlled API failure message.
- EmptyState: no matching indexed cases.
- Field: label, helper text, focusable control, validation/error state if supported by the final component contract.

- [ ] **Step 3: Run Storybook static build**

```bash
npm run build-storybook
```

Expected: PASS without browser console build errors.

- [ ] **Step 4: Commit**

```bash
git add src/components/ui

git commit -m "test: document reusable UI states"
```

---

### Task 3: Add domain stories for triage, evidence, trace, and evaluation

**Files:**
- Create: `frontend/src/features/triage/TicketComposer.stories.tsx`
- Create: `frontend/src/features/triage/TriageDecision.stories.tsx`
- Create: `frontend/src/components/evidence/CaseList.stories.tsx`
- Create: `frontend/src/components/trace/TraceList.stories.tsx`
- Create: `frontend/src/features/evaluation/EvaluationChart.stories.tsx` or the final evaluation metric component story.
- Reuse: `frontend/src/test/fixtures.ts`

**Interfaces:**
- Reuse deterministic fixture factories; add typed override helpers if needed rather than copying giant objects into stories.

- [ ] **Step 1: Extend fixture helper with typed overrides**

Refactor signatures to:

```ts
export function makeTriageResult(overrides: Partial<TriageResult> = {}): TriageResult
export function makeEvaluation(overrides: Partial<Evaluation> = {}): Evaluation
```

Return `{ ...base, ...overrides }` while keeping nested trace/classification fixtures stable unless explicitly overridden.

- [ ] **Step 2: Add TriageDecision stories**

Required named exports:
- `Standard`
- `Escalated`
- `Ungrounded`
- `Degraded`
- `Fallback`
- `Cached`

Use these semantic overrides:

```ts
Escalated: { escalate: true, urgency: "high", escalation_reason: "Urgent account-protection review required." }
Ungrounded: { grounded: false, grounding_score: 0.2, next_action: "manual_review", unsupported_claims: ["Evidence is insufficient."] }
Degraded: { degraded_mode: true, grounded: false, next_action: "manual_review" }
Fallback: { fallback_used: true }
Cached: { cached: true }
```

- [ ] **Step 3: Add CaseList and TraceList stories**

CaseList: `Populated`, `Empty`.
TraceList: `Normal`, `Fallback`, `Degraded`, `Empty`.

- [ ] **Step 4: Add evaluation story**

Use `makeEvaluation()` and ensure the story includes a textual metric/limitation summary, not chart-only information.

- [ ] **Step 5: Build Storybook and run unit regression**

```bash
npm run build-storybook
npm test
npm run lint
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/test/fixtures.ts src/features src/components

git commit -m "test: add support workflow Storybook states"
```

---

### Task 4: Install and configure Chromium-only Playwright acceptance tests

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/package-lock.json`
- Create: `frontend/playwright.config.ts`
- Create: `frontend/e2e/triage.spec.ts`
- Create: `frontend/e2e/evaluation.spec.ts`
- Create: `frontend/e2e/error-state.spec.ts`

**Interfaces:**
- Base URL: `http://127.0.0.1:5173`.
- Backend: `http://127.0.0.1:8000`, started in deterministic demo/mock mode.

- [ ] **Step 1: Install Playwright Test**

```bash
cd frontend
npm install --save-dev @playwright/test
npx playwright install chromium
```

Add scripts:

```json
{
  "test:e2e": "playwright test",
  "test:e2e:report": "playwright show-report"
}
```

- [ ] **Step 2: Create Playwright config**

Use:

```ts
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  expect: { timeout: 5_000 },
  retries: process.env.CI ? 1 : 0,
  reporter: [["html", { outputFolder: "playwright-report", open: "never" }]],
  use: {
    baseURL: "http://127.0.0.1:5173",
    trace: "on-first-retry",
    screenshot: { mode: "only-on-failure", fullPage: true },
    video: "on-first-retry",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"], channel: "chromium" } },
  ],
  webServer: [
    {
      command: "python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000",
      cwd: "..",
      url: "http://127.0.0.1:8000/health",
      reuseExistingServer: !process.env.CI,
      env: {
        DEMO_MODE: "true",
        MOCK_LLM_MODE: "true",
        QDRANT_MODE: "memory",
        EMBEDDING_PROVIDER: "hashing",
        RETRIEVAL_MIN_SCORE: "0",
        LLM_CACHE_ENABLED: "false",
      },
    },
    {
      command: "npm run dev -- --host 127.0.0.1",
      url: "http://127.0.0.1:5173",
      reuseExistingServer: !process.env.CI,
    },
  ],
});
```

If the installed Playwright type rejects `cwd`, do not invent a workaround in source code: verify current official WebServerConfig and use its supported working-directory option or a cross-platform repository script.

- [ ] **Step 3: Write the primary triage E2E test**

`triage.spec.ts` must:

```ts
import { expect, test } from "@playwright/test";

test("Card not arrived produces a reviewable evidence-grounded decision", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText(/api connected/i)).toBeVisible();
  await page.getByRole("button", { name: /card not arrived/i }).click();
  await page.getByRole("button", { name: /run triage/i }).click();
  await expect(page.getByText(/decision/i)).toBeVisible();
  await expect(page.getByText(/grounded/i)).toBeVisible();
  await expect(page.getByRole("heading", { name: /seven-node execution trace/i })).toBeVisible();
  await expect(page.getByText(/7\. suggest next action/i)).toBeVisible();
  await expect(page.getByText(/retrieved/i).first()).toBeVisible();
});
```

Adjust only ambiguous visible-text locators after inspecting the actual DOM; keep role/label semantics wherever possible.

- [ ] **Step 4: Add escalation E2E**

Select `Card stolen` or `Suspicious transaction`, run triage, assert visible escalation text/reason and high/urgent status. Do not assert only a CSS color/class.

- [ ] **Step 5: Add evaluation E2E**

Navigate with the `Evaluation` button; assert deterministic evaluation mode, a metric table/header, and limitations text.

- [ ] **Step 6: Add explicit API-unavailable test via network failure**

Use:

```ts
await page.route("**/health", (route) => route.abort());
await page.goto("/");
await expect(page.getByText(/api unavailable/i)).toBeVisible();
await expect(page.getByText(/traceback|api[_-]?key|localhost:\\Users/i)).toHaveCount(0);
```

- [ ] **Step 7: Run E2E locally**

```bash
npm run test:e2e
```

Expected: all required deterministic flows PASS with no external model key.

- [ ] **Step 8: Commit**

```bash
git add package.json package-lock.json playwright.config.ts e2e

git commit -m "test: add deterministic browser acceptance suite"
```

---

### Task 5: Add selected visual baselines and responsive overflow assertions

**Files:**
- Create: `frontend/e2e/visual.spec.ts`
- Commit generated Chromium baselines under Playwright's snapshot directory.

**Interfaces:**
- Baselines: triage initial desktop, triage success desktop, escalated result desktop, evaluation desktop, representative 390px mobile result.

- [ ] **Step 1: Add reusable stability helper inside visual spec**

```ts
async function stabilize(page: Page) {
  await page.addStyleTag({
    content: "*,*::before,*::after{animation:none!important;transition:none!important}",
  });
}
```

- [ ] **Step 2: Add desktop screenshot assertions**

For each approved state:

```ts
await stabilize(page);
await expect(page).toHaveScreenshot("triage-success.png", {
  fullPage: true,
  animations: "disabled",
  maxDiffPixelRatio: 0.01,
});
```

Mask only truly nondeterministic values after proving they vary; do not mask decision/evidence/status content.

- [ ] **Step 3: Add responsive overflow helper**

```ts
async function expectNoPageOverflow(page: Page) {
  const overflow = await page.evaluate(() =>
    document.documentElement.scrollWidth > document.documentElement.clientWidth
  );
  expect(overflow).toBe(false);
}
```

Run it at viewports `{ width: 390, height: 844 }`, `{ width: 768, height: 1024 }`, and `{ width: 1440, height: 1000 }` on primary triage/evaluation views.

- [ ] **Step 4: Generate first baselines intentionally**

```bash
npx playwright test e2e/visual.spec.ts --update-snapshots
```

Review every generated screenshot before `git add`.

- [ ] **Step 5: Re-run without update flag**

```bash
npx playwright test e2e/visual.spec.ts
```

Expected: PASS against committed baselines.

- [ ] **Step 6: Commit**

```bash
git add e2e/visual.spec.ts e2e/**/*-snapshots

git commit -m "test: add visual and responsive regression gates"
```

---

### Task 6: Extend GitHub Actions with Storybook and browser jobs

**Files:**
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Existing `backend` and `frontend` jobs stay recognizable.
- Add `npm run build-storybook` to frontend job.
- Add separate `browser` job depending on successful backend/frontend checks if appropriate.

- [ ] **Step 1: Add Storybook build to existing frontend job**

After `npm run build`, add:

```yaml
- run: npm run build-storybook
```

- [ ] **Step 2: Add Chromium browser job**

Use Node 24 consistent with existing frontend CI, Python 3.12 consistent with backend, install current CPU deps, `npm ci`, then:

```yaml
- run: npx playwright install --with-deps chromium
- run: npm run test:e2e
  env:
    CI: "true"
```

Playwright's configured web servers supply deterministic backend environment variables; do not add external LLM secrets.

- [ ] **Step 3: Upload actionable failure evidence**

Add `actions/upload-artifact@v4` with `if: failure()` for:
- `frontend/playwright-report/`
- `frontend/test-results/`

Use a short retention such as 7 days.

- [ ] **Step 4: Validate workflow syntax/references**

Review the YAML diff and run local frontend/Playwright suite. Do not claim CI green until GitHub Actions itself completes.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/ci.yml

git commit -m "ci: add UI component and browser quality gates"
```

---

## Phase review gate

Local complete UI matrix:

```bash
cd frontend
npm run lint
npm test
npm run build
npm run build-storybook
npm run test:e2e
```

Then push the focused branch and require GitHub Actions backend/frontend/browser jobs to pass. Review any screenshot baseline diff deliberately. Independent review should examine flaky-test risks, weak assertions, excessive masking, accessibility gaps, accidental credential dependence, and CI replacement of pre-existing gates.