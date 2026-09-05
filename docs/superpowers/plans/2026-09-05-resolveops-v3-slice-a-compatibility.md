# ResolveOps v3 Slice A Compatibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Determine the least-risk integration path for shadcn/ui with the React Aria base, Tailwind, and self-hosted Geist typography in the existing React 19 + Vite ResolveOps frontend without changing production UI behavior.

**Architecture:** Run all compatibility probes in disposable copies outside the repository. Compare the current Tailwind 3 path with a controlled Tailwind 4 path only when evidence requires it. Commit only one compatibility decision report; no production source, package manifest, Storybook, Playwright baseline, backend, deployment, or screenshot changes belong in Slice A.

**Tech Stack:** React 19, Vite 8, TypeScript 5.7, Tailwind 3.4.17 baseline, PostCSS, Storybook 10.6, Playwright 1.61, current shadcn CLI, React Aria base, `@fontsource-variable/geist`, `@fontsource-variable/geist-mono`.

**Spec:** `docs/superpowers/specs/2026-09-05-resolveops-design-system-v3-design.md`

## Global Constraints

- Base Slice A on the canonical `main` commit that contains the approved ResolveOps v3 spec.
- Do not modify backend, LangGraph, RAG, evaluation, deployment, screenshots, visual baselines, or business semantics.
- Geist Sans/Variable is the selected UI font; Geist Mono is the selected technical font.
- Font assets must be self-hosted through the application bundle; no runtime web-font CDN.
- shadcn must use the React Aria base (`--base aria`).
- Mira is density inspiration only; generated theme defaults are not ResolveOps design decisions.
- Do not run `npm audit fix --force`.
- Do not update Playwright snapshots.
- Do not commit temporary probe projects, `node_modules`, `dist`, `storybook-static`, browser artifacts, or machine-specific paths.
- A compatibility failure is evidence, not permission to weaken tests or broaden dependency upgrades.

---

### Task 1: Establish the clean baseline and disposable probe workspace

**Files:**
- Read: `frontend/package.json`
- Read: `frontend/package-lock.json`
- Read: `frontend/tailwind.config.js`
- Read: `frontend/postcss.config.js`
- Read: `frontend/vite.config.ts`
- Read: `frontend/tsconfig.json`
- Read: `frontend/tsconfig.app.json`
- Read: `frontend/src/main.tsx`
- Read: `frontend/src/styles/base.css`
- Read: `frontend/src/styles/tokens.css`
- Temporary outside repo: `%TEMP%/resolveops-v3-probes/tw3/`
- Temporary if needed: `%TEMP%/resolveops-v3-probes/tw4/`

**Interfaces:**
- Consumes: the current repository frontend configuration.
- Produces: isolated probe workspaces that can be destroyed without touching git state.

- [ ] **Step 1: Verify repository identity and task-branch cleanliness**

Run:

```powershell
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git status --short
```

Stop if unexpected changes exist.

- [ ] **Step 2: Capture exact toolchain versions**

From `frontend/` run:

```powershell
node --version
npm --version
npm ls react react-dom vite typescript tailwindcss postcss autoprefixer --depth=0
npx shadcn@latest --version
```

Keep the exact output in working notes for the final report.

- [ ] **Step 3: Capture baseline frontend health**

Run:

```powershell
npm ci
npm audit
npm run lint
npm test
npm run build
```

Expected current baseline: install succeeds, audit reports zero vulnerabilities, lint succeeds, 34 unit tests pass, and production build succeeds. If the real baseline is broken, stop before probing and report the failure.

- [ ] **Step 4: Create a disposable Tailwind 3 probe**

From `frontend/`:

```powershell
$probeRoot = Join-Path $env:TEMP 'resolveops-v3-probes'
$tw3 = Join-Path $probeRoot 'tw3'
Remove-Item $tw3 -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $tw3 | Out-Null
robocopy . $tw3 /E /XD node_modules dist storybook-static playwright-report test-results /XF *.log
if ($LASTEXITCODE -gt 7) { throw "robocopy failed: $LASTEXITCODE" }
```

Confirm `$tw3` is outside the repository.

- [ ] **Step 5: Verify Task 1 left git unchanged**

Run:

```powershell
git status --short
```

Expected: no task-created repository changes.

---

### Task 2: Verify self-hosted Geist Sans and Geist Mono on the current Vite stack

**Files:**
- Temporary only: `%TEMP%/resolveops-v3-probes/tw3/package.json`
- Temporary only: `%TEMP%/resolveops-v3-probes/tw3/package-lock.json`
- Temporary only: `%TEMP%/resolveops-v3-probes/tw3/src/main.tsx`
- Temporary only: `%TEMP%/resolveops-v3-probes/tw3/src/styles/tokens.css`

**Interfaces:**
- Consumes: the existing Vite entry point and CSS token mechanism.
- Produces: proof that both selected fonts bundle locally and can be referenced through semantic tokens.

- [ ] **Step 1: Install only the selected font packages in the disposable probe**

```powershell
npm install @fontsource-variable/geist @fontsource-variable/geist-mono
npm ls @fontsource-variable/geist @fontsource-variable/geist-mono --depth=0
```

Record exact installed versions.

- [ ] **Step 2: Add temporary font imports in the probe only**

At the top of probe `src/main.tsx` add:

```ts
import "@fontsource-variable/geist/wght.css";
import "@fontsource-variable/geist-mono/wght.css";
```

- [ ] **Step 3: Override only the probe font tokens**

In probe `src/styles/tokens.css` set:

```css
--font-ui: "Geist Variable", ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
--font-code: "Geist Mono Variable", ui-monospace, SFMono-Regular, Consolas, monospace;
```

- [ ] **Step 4: Build the probe**

```powershell
npm run build
```

Expected: Vite succeeds.

- [ ] **Step 5: Prove font assets are local**

Run:

```powershell
Get-ChildItem dist\assets -File | Where-Object { $_.Extension -match '\.(woff2|woff|ttf|otf)$' }
Get-ChildItem dist -Recurse -File | Select-String -Pattern 'fonts.googleapis.com|fonts.gstatic.com'
```

Expected: local font assets are emitted and no Google Fonts runtime URL appears.

- [ ] **Step 6: Record the font conclusion in working notes**

Record exact package versions, build result, whether local font assets were emitted, whether an external font CDN appeared, and Vite build-size output.

Do not commit probe changes.

---

### Task 3: Probe shadcn React Aria against the existing Tailwind 3 project

**Files:**
- Temporary only: `%TEMP%/resolveops-v3-probes/tw3/**`

**Interfaces:**
- Consumes: existing Tailwind 3 + PostCSS + Vite project shape.
- Produces: one Tailwind 3 classification: `SUPPORTED`, `UNSUPPORTED`, or `SUPPORTED_WITH_CHURN`.

- [ ] **Step 1: Recreate the Tailwind 3 probe from the repository**

Delete and recopy the probe so the Geist test does not contaminate shadcn evidence.

- [ ] **Step 2: Inspect current CLI capability**

```powershell
npx shadcn@latest --version
npx shadcn@latest init --help
```

Confirm `--base aria` is recognized.

- [ ] **Step 3: Initialize React Aria in the disposable probe**

```powershell
npx shadcn@latest init --base aria
```

Use existing-project/Vite-compatible answers only. If the CLI rejects the current Tailwind setup, capture the exact safe error and do not force the command.

- [ ] **Step 4: Inspect all generated changes in the probe**

Record whether the CLI:

- requires or upgrades Tailwind;
- adds `@tailwindcss/vite`;
- rewrites PostCSS;
- rewrites the CSS entry to `@import "tailwindcss"`;
- creates `components.json`;
- adds TypeScript/Vite aliases;
- adds runtime packages;
- overwrites ResolveOps tokens;
- touches unrelated application source.

- [ ] **Step 5: Add one representative primitive if init succeeds**

```powershell
npx shadcn@latest add button
```

Use Button, not Card, because v3 explicitly rejects card-first composition.

- [ ] **Step 6: Verify the Tailwind 3 probe**

```powershell
npm run lint
npm test
npm run build
```

Record actual outcomes.

- [ ] **Step 7: Classify Tailwind 3**

Choose exactly one:

```text
SUPPORTED
UNSUPPORTED
SUPPORTED_WITH_CHURN
```

Use `SUPPORTED_WITH_CHURN` when the CLI technically works but forces broad configuration/dependency changes that make a controlled Tailwind 4 migration clearer and safer.

---

### Task 4: Probe a controlled Tailwind 4 path only when Task 3 justifies it

**Files:**
- Temporary only: `%TEMP%/resolveops-v3-probes/tw4/**`

**Interfaces:**
- Consumes: Task 3 evidence.
- Produces: a minimal Tailwind 4 migration delta and proof that React Aria + Geist coexist with the current application.

- [ ] **Step 1: Decide whether Tailwind 4 must be probed**

Run this task only if Task 3 is `UNSUPPORTED` or `SUPPORTED_WITH_CHURN`, or current official Vite/shadcn setup clearly requires the modern Tailwind Vite plugin path.

If Task 3 is cleanly `SUPPORTED`, record `TAILWIND4_PROBE=NOT_REQUIRED` and skip Tasks 4.2-4.6.

- [ ] **Step 2: Create a fresh Tailwind 4 disposable copy**

Use the same copy exclusions as Task 1.

- [ ] **Step 3: Apply only the documented modern Vite/Tailwind prerequisites in the probe**

```powershell
npm install -D tailwindcss @tailwindcss/vite
```

Adapt the real `vite.config.ts` so its plugin array includes:

```ts
import tailwindcss from "@tailwindcss/vite";
```

and:

```ts
plugins: [react(), tailwindcss()]
```

Preserve all existing non-Tailwind Vite configuration.

Replace the probe CSS Tailwind directives with:

```css
@import "tailwindcss";
```

Do not copy generated theme values over ResolveOps tokens.

- [ ] **Step 4: Initialize shadcn React Aria and add Button**

```powershell
npx shadcn@latest init --base aria
npx shadcn@latest add button
```

Inspect all generated dependencies and files.

- [ ] **Step 5: Add Geist packages to the Tailwind 4 probe**

```powershell
npm install @fontsource-variable/geist @fontsource-variable/geist-mono
```

Use the same temporary imports and CSS font-token values from Task 2.

- [ ] **Step 6: Verify the Tailwind 4 probe**

```powershell
npm audit
npm run lint
npm test
npm run build
npm run build-storybook
```

If `storybook-static` already exists in the disposable probe, remove only that generated directory and rerun Storybook. Do not modify Storybook source/config merely to work around an output collision.

Record the exact minimal package/config delta that would be required for Slice B.

---

### Task 5: Write the compatibility decision report

**Files:**
- Create: `reports/design/2026-09-05-resolveops-v3-compatibility.md`

**Interfaces:**
- Consumes: Tasks 1-4 evidence.
- Produces: the binding technical decision used by Slice B.

- [ ] **Step 1: Create the report sections**

The report must contain these sections in this order:

```markdown
# ResolveOps v3 compatibility decision

## Baseline
## Geist self-hosting
## Tailwind 3 + shadcn React Aria
## Tailwind 4 probe
## Decision
## Guardrails for Slice B
## Limitations
```

- [ ] **Step 2: Fill Baseline from fresh command output**

Under `## Baseline`, record the exact output values from:

```powershell
git rev-parse HEAD
node --version
npm --version
npm ls react vite tailwindcss --depth=0
npx shadcn@latest --version
```

Do not copy expected values from this plan when fresh output differs.

- [ ] **Step 3: Fill Geist self-hosting from Task 2**

Record exact installed package versions, Vite build pass/fail, whether local font assets were emitted, whether any runtime external font CDN was found, and any relevant build-size observation.

The package names must be written exactly:

```text
@fontsource-variable/geist
@fontsource-variable/geist-mono
```

- [ ] **Step 4: Fill Tailwind 3 + shadcn React Aria from Task 3**

Record:

```text
Classification: SUPPORTED | UNSUPPORTED | SUPPORTED_WITH_CHURN
--base aria recognized: YES | NO
Button primitive generated: YES | NO
Lint: PASS | FAIL | NOT_RUN
Unit: PASS | FAIL | NOT_RUN
Build: PASS | FAIL | NOT_RUN
```

Then list the exact config/dependency changes the CLI attempted.

- [ ] **Step 5: Fill Tailwind 4 probe from Task 4**

Record:

```text
Required: YES | NO
Result: PASS | FAIL | NOT_REQUIRED
```

If run, list exact files/packages required by the minimal successful path and the actual lint/unit/build/Storybook results.

- [ ] **Step 6: Make the binding decision**

Under `## Decision`, choose exactly one Tailwind path:

```text
KEEP_3
MIGRATE_4
```

Also choose:

```text
React Aria base: ADOPT | BLOCKED
Geist typography: ADOPT | BLOCKED
```

Write one short evidence-backed rationale paragraph. Do not choose a path merely because it is newer.

- [ ] **Step 7: Write exact Slice B guardrails**

Convert probe evidence into concrete constraints, for example which config files must change, which generated defaults must not be retained, and whether Tailwind migration must be isolated before component migration.

- [ ] **Step 8: Secret/path review**

Search the report for auth values, npm tokens, cookies, absolute user paths, browser profile paths, and local temp paths. Remove private details before commit.

---

### Task 6: Final Slice A verification and PR

**Files:**
- Create: `reports/design/2026-09-05-resolveops-v3-compatibility.md`
- No other repository changes expected.

**Interfaces:**
- Consumes: the completed compatibility report.
- Produces: a reviewable docs-only Slice A PR.

- [ ] **Step 1: Delete only disposable probe material**

Remove the temporary probe directories outside the repository. If any task-created temporary file accidentally exists inside the repository, inspect and remove only that file.

- [ ] **Step 2: Verify repository scope**

```powershell
git status --short
git diff --stat
git diff --check
```

Expected task-created repository diff:

```text
reports/design/2026-09-05-resolveops-v3-compatibility.md
```

No package files, frontend source/config, screenshots, visual baselines, backend, or deployment files may change in Slice A.

- [ ] **Step 3: Re-run canonical frontend baseline in the real repository**

```powershell
npm ci
npm audit
npm run lint
npm test
npm run build
```

Expected: same healthy result as Task 1. If the actual baseline differs, report the real result instead of claiming success.

- [ ] **Step 4: Commit only the report**

```powershell
git add reports/design/2026-09-05-resolveops-v3-compatibility.md
git commit -m "docs: record ResolveOps v3 compatibility decision"
```

- [ ] **Step 5: Push and open the Slice A PR**

PR title:

```text
docs: record ResolveOps v3 compatibility decision
```

PR body must state:

```text
Implements ResolveOps v3 Slice A compatibility spike.

- No production UI redesign in this PR.
- No backend/RAG/evaluation/deployment changes.
- Probe work ran in disposable copies outside the repository.
- The report records the evidence-backed Tailwind path, shadcn React Aria compatibility, and self-hosted Geist decision for Slice B.
```

- [ ] **Step 6: Wait for final-head CI**

Require the existing stable jobs to pass:

```text
backend
frontend
browser
```

Confirm Storybook succeeds in the frontend job and Playwright remains 14/14 in the browser job.

- [ ] **Step 7: Stop before merge**

Do not merge Slice A. Return the PR and report for owner/ChatGPT review. Slice B starts only after the compatibility decision is independently checked.

## Plan self-review

- Spec coverage: Slice A covers Tailwind compatibility, React Aria initialization, Geist self-hosting, dependency-churn control, and existing quality gates.
- Placeholder scan: no TODO/TBD or value placeholders remain; all unknown values must come from named fresh commands.
- Type/config consistency: Slice A intentionally defines no permanent component API; permanent implementation starts in Slice B after the compatibility decision.
