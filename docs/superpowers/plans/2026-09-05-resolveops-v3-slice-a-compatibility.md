# ResolveOps v3 Slice A Compatibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Determine the least-risk integration path for shadcn/ui with the React Aria base, Tailwind, and self-hosted Geist typography in the existing React 19 + Vite ResolveOps frontend without changing production UI behavior.

**Architecture:** Run compatibility probes in disposable copies outside the repository, compare the existing Tailwind 3 path with a controlled Tailwind 4 path only if needed, and commit only an evidence report plus any documentation-only decision records. No production source, package manifest, design token, Storybook, Playwright baseline, backend, deployment, or screenshot changes belong in Slice A.

**Tech Stack:** React 19, Vite 8, TypeScript 5.7, Tailwind 3.4.17 baseline, PostCSS, Storybook 10.6, Playwright 1.61, shadcn CLI current release, shadcn React Aria base, Fontsource Geist variable packages.

**Spec:** `docs/superpowers/specs/2026-09-05-resolveops-design-system-v3-design.md`

## Global Constraints

- Base Slice A on the canonical `main` commit that contains the approved ResolveOps v3 spec.
- Do not modify backend, LangGraph, RAG, evaluation, deployment, screenshots, visual baselines, or business semantics.
- Do not introduce a runtime external font CDN.
- The selected UI font family is Geist Sans/Variable; the selected technical font family is Geist Mono.
- Preferred self-hosted packages are `@fontsource-variable/geist` and `@fontsource-variable/geist-mono`.
- shadcn must use the React Aria base (`--base aria`) if the current CLI supports it as documented.
- Mira is density inspiration only; do not accept generated theme defaults as ResolveOps product decisions.
- Do not run `npm audit fix --force`.
- Do not update Playwright snapshots.
- Do not commit temporary probe projects, generated `node_modules`, build output, Storybook output, browser artifacts, or local paths.
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
- Create outside repo: `<temp>/resolveops-v3-probes/tw3/`
- Create only if needed: `<temp>/resolveops-v3-probes/tw4/`

**Interfaces:**
- Consumes: the current repository frontend configuration.
- Produces: two isolated probe workspaces that can be destroyed without touching git state.

- [ ] **Step 1: Verify repository identity and clean task branch**

Run:

```powershell
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git status --short
```

Expected: correct repository, expected Slice A branch, and no unexplained working-tree changes.

- [ ] **Step 2: Capture exact toolchain versions**

Run from `frontend/`:

```powershell
node --version
npm --version
npm ls react react-dom vite typescript tailwindcss postcss autoprefixer --depth=0
npx shadcn@latest --version
```

Record actual output in working notes. Do not commit machine-specific paths.

- [ ] **Step 3: Capture baseline frontend health**

Run:

```powershell
npm ci
npm audit
npm run lint
npm test
npm run build
```

Expected current healthy baseline: install succeeds, audit reports zero vulnerabilities, lint succeeds, 34 unit tests pass, and production build succeeds. If current output differs, record the actual evidence and stop before compatibility probing if the baseline itself is broken.

- [ ] **Step 4: Create a disposable Tailwind 3 probe copy outside the repo**

Copy only the frontend project files required to run npm/Vite into a temporary directory outside the repository. Exclude `.git`, `node_modules`, `dist`, `storybook-static`, `playwright-report`, and `test-results`.

Suggested PowerShell pattern:

```powershell
$probeRoot = Join-Path $env:TEMP 'resolveops-v3-probes'
$tw3 = Join-Path $probeRoot 'tw3'
Remove-Item $tw3 -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $tw3 | Out-Null
robocopy . $tw3 /E /XD node_modules dist storybook-static playwright-report test-results /XF *.log
if ($LASTEXITCODE -gt 7) { throw "robocopy failed: $LASTEXITCODE" }
```

Confirm the probe path is outside the git repository before running destructive probe commands.

- [ ] **Step 5: Commit nothing for Task 1**

Task 1 is environment setup only. Verify repository `git status --short` remains unchanged.

---

### Task 2: Verify self-hosted Geist Sans and Geist Mono on the current Vite stack

**Files:**
- Temporary only: `<temp>/resolveops-v3-probes/tw3/package.json`
- Temporary only: `<temp>/resolveops-v3-probes/tw3/package-lock.json`
- Temporary only: `<temp>/resolveops-v3-probes/tw3/src/main.tsx`
- Temporary only: `<temp>/resolveops-v3-probes/tw3/src/styles/tokens.css`
- Later report: `reports/design/2026-09-05-resolveops-v3-compatibility.md`

**Interfaces:**
- Consumes: Vite application entry and CSS token mechanism.
- Produces: evidence that Geist can be bundled locally with Vite and referenced through semantic font tokens.

- [ ] **Step 1: Install only the selected font packages in the disposable Tailwind 3 probe**

Run inside the probe:

```powershell
npm install @fontsource-variable/geist @fontsource-variable/geist-mono
```

Record exact installed versions from:

```powershell
npm ls @fontsource-variable/geist @fontsource-variable/geist-mono --depth=0
```

- [ ] **Step 2: Add temporary imports in the probe only**

At the top of the probe `src/main.tsx`, add:

```ts
import "@fontsource-variable/geist/wght.css";
import "@fontsource-variable/geist-mono/wght.css";
```

Do not make this edit in the repository during Slice A.

- [ ] **Step 3: Override probe font tokens**

In the probe `src/styles/tokens.css`, temporarily set:

```css
--font-ui: "Geist Variable", ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
--font-code: "Geist Mono Variable", ui-monospace, SFMono-Regular, Consolas, monospace;
```

Also add a temporary test rule if needed to confirm mono resolution:

```css
[data-font-probe="mono"] {
  font-family: var(--font-code);
  font-variant-numeric: tabular-nums;
}
```

- [ ] **Step 4: Build the probe**

Run:

```powershell
npm run build
```

Expected: Vite succeeds and bundles local font assets; no runtime Google Fonts or other external font URL is introduced.

- [ ] **Step 5: Inspect the built output for self-hosted assets**

Search the generated CSS/JS and HTML:

```powershell
Get-ChildItem dist -Recurse -File | Select-String -Pattern 'fonts.googleapis.com|fonts.gstatic.com|http://|https://' -SimpleMatch
Get-ChildItem dist\assets -File | Where-Object { $_.Extension -match '\.(woff2|woff|ttf|otf)$' }
```

The external-font search should not reveal a runtime web-font CDN. Font assets should be emitted locally.

- [ ] **Step 6: Record decision evidence**

Record package versions, build result, emitted local font asset evidence, and any bundle-size impact available from the Vite build summary.

Do not commit probe changes.

---

### Task 3: Probe shadcn React Aria against the existing Tailwind 3 project

**Files:**
- Temporary only: `<temp>/resolveops-v3-probes/tw3/**`
- Later report: `reports/design/2026-09-05-resolveops-v3-compatibility.md`

**Interfaces:**
- Consumes: existing Tailwind 3 + PostCSS + Vite project shape.
- Produces: a factual `TAILWIND3_SHADCN_ARIA=SUPPORTED | UNSUPPORTED | SUPPORTED_WITH_CHURN` decision.

- [ ] **Step 1: Reset the disposable Tailwind 3 probe to a clean copy**

Recreate the `tw3` probe from the repository so the font test does not contaminate shadcn evidence.

- [ ] **Step 2: Inspect shadcn CLI project analysis before accepting writes**

Run safe informational commands first:

```powershell
npx shadcn@latest info
npx shadcn@latest init --help
```

Confirm the CLI documents `--base aria` for the installed current release. Record its version.

- [ ] **Step 3: Initialize React Aria in the disposable Tailwind 3 probe**

Run in the probe only:

```powershell
npx shadcn@latest init --base aria
```

Use non-destructive/default choices appropriate to an existing Vite project. Do not accept or invent a framework migration.

If the CLI refuses because the existing Tailwind configuration is unsupported, capture the exact safe error and stop the Tailwind 3 probe there.

- [ ] **Step 4: Inspect the entire probe diff**

Because the probe is outside git, compare against the original frontend copy using a directory diff or copy the probe into a second temporary git-initialized directory before running `git diff --no-index`.

Record whether the CLI:

- requires or upgrades Tailwind;
- adds `@tailwindcss/vite`;
- rewrites PostCSS;
- rewrites the CSS entry to `@import "tailwindcss"`;
- creates `components.json`;
- adds aliases;
- adds runtime packages;
- rewrites existing ResolveOps tokens;
- touches application source unrelated to initialization.

- [ ] **Step 5: Add one low-risk primitive in the disposable probe**

If initialization succeeds without unacceptable churn, run:

```powershell
npx shadcn@latest add button
```

Do not use `card` as the representative probe because v3 explicitly rejects card-first composition.

- [ ] **Step 6: Build and test the disposable probe**

Run:

```powershell
npm run lint
npm test
npm run build
```

Record success/failure and any dependency or CSS collision.

- [ ] **Step 7: Classify the Tailwind 3 path**

Use exactly one classification:

```text
SUPPORTED
UNSUPPORTED
SUPPORTED_WITH_CHURN
```

`SUPPORTED_WITH_CHURN` means the CLI technically works but forces broad configuration/dependency changes that make a controlled Tailwind 4 slice safer and clearer.

---

### Task 4: Probe a controlled Tailwind 4 path only if Task 3 justifies it

**Files:**
- Temporary only: `<temp>/resolveops-v3-probes/tw4/**`
- Later report: `reports/design/2026-09-05-resolveops-v3-compatibility.md`

**Interfaces:**
- Consumes: current Vite project and Task 3 evidence.
- Produces: a minimal Tailwind 4 migration delta and proof that shadcn React Aria can coexist with existing ResolveOps behavior.

- [ ] **Step 1: Decide whether this task is required**

Run Task 4 only when Task 3 is `UNSUPPORTED` or `SUPPORTED_WITH_CHURN`, or when the current official Vite/shadcn configuration clearly requires the modern Tailwind Vite plugin path.

If Task 3 is cleanly `SUPPORTED`, record `TAILWIND4_PROBE=NOT_REQUIRED` and skip the remaining Task 4 steps.

- [ ] **Step 2: Create a fresh disposable Tailwind 4 probe copy**

Copy the repository frontend into `<temp>/resolveops-v3-probes/tw4` using the same exclusions as Task 1.

- [ ] **Step 3: Apply only the documented modern Vite/Tailwind prerequisites in the probe**

Install the documented Vite integration without unrelated upgrades:

```powershell
npm install -D tailwindcss @tailwindcss/vite
```

Update the probe Vite configuration to include the Tailwind plugin while preserving React and existing aliases/configuration.

Use this shape as the target concept, adapted to the actual existing file:

```ts
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // preserve existing configuration
});
```

Update the probe CSS entry to the current Tailwind 4 form only in the probe:

```css
@import "tailwindcss";
```

Do not copy generated shadcn theme values over ResolveOps product tokens.

- [ ] **Step 4: Initialize shadcn with React Aria in the Tailwind 4 probe**

Run:

```powershell
npx shadcn@latest init --base aria
npx shadcn@latest add button
```

Inspect all resulting files and dependencies.

- [ ] **Step 5: Add the two Geist variable packages to the Tailwind 4 probe**

Run:

```powershell
npm install @fontsource-variable/geist @fontsource-variable/geist-mono
```

Use the same temporary imports and font token values from Task 2.

- [ ] **Step 6: Run the frontend verification matrix in the Tailwind 4 probe**

Run:

```powershell
npm audit
npm run lint
npm test
npm run build
npm run build-storybook
```

If Storybook output exists from the copied project, remove only ignored/generated `storybook-static` in the disposable probe and rerun. Do not change Storybook source/config just to handle an output collision.

- [ ] **Step 7: Record the minimal migration delta**

List exact packages/config files required for the clean Tailwind 4 + React Aria + Geist path. Explicitly identify any generated defaults that must be replaced by ResolveOps semantic token mapping in Slice B.

---

### Task 5: Write the compatibility decision report

**Files:**
- Create: `reports/design/2026-09-05-resolveops-v3-compatibility.md`

**Interfaces:**
- Consumes: Tasks 1-4 probe evidence.
- Produces: the binding decision used by Slice B.

- [ ] **Step 1: Create the report with this exact structure**

```markdown
# ResolveOps v3 compatibility decision

## Baseline
- GitHub base SHA: `<actual>`
- Node: `<actual>`
- npm: `<actual>`
- React: `<actual>`
- Vite: `<actual>`
- Tailwind baseline: `<actual>`
- shadcn CLI: `<actual>`

## Geist self-hosting
- `@fontsource-variable/geist`: `<version>`
- `@fontsource-variable/geist-mono`: `<version>`
- Vite build: PASS | FAIL
- Local font assets emitted: YES | NO
- Runtime external font CDN: NO | YES
- Notes: `<evidence-backed only>`

## Tailwind 3 + shadcn React Aria
- Classification: SUPPORTED | UNSUPPORTED | SUPPORTED_WITH_CHURN
- `--base aria` recognized: YES | NO
- `button` primitive generated: YES | NO
- Lint/unit/build: `<actual>`
- Forced config/dependency changes: `<actual list>`

## Tailwind 4 probe
- Required: YES | NO
- Result: PASS | FAIL | NOT_REQUIRED
- Minimal migration files: `<actual list or None>`
- Lint/unit/build/Storybook: `<actual>`

## Decision
- Tailwind path for Slice B: KEEP_3 | MIGRATE_4
- React Aria base: ADOPT | BLOCKED
- Geist typography: ADOPT | BLOCKED
- Rationale: `<short evidence-backed paragraph>`

## Guardrails for Slice B
- `<exact constraints derived from evidence>`

## Limitations
- `<actual limitations only>`
```

- [ ] **Step 2: Do not claim a preferred Tailwind version before the probe evidence supports it**

The report must choose `KEEP_3` or `MIGRATE_4` from actual Task 3/4 evidence.

- [ ] **Step 3: Confirm the selected typography is exact**

The report must name both packages exactly when adoption succeeds:

```text
@fontsource-variable/geist
@fontsource-variable/geist-mono
```

- [ ] **Step 4: Validate the report for secrets/private paths**

Search the report for usernames, absolute local paths, auth headers, tokens, cookies, npm auth, and browser profile locations. Remove them before commit.

---

### Task 6: Final Slice A verification and commit

**Files:**
- Create: `reports/design/2026-09-05-resolveops-v3-compatibility.md`
- No other repository changes expected.

**Interfaces:**
- Consumes: compatibility report and original repository state.
- Produces: a reviewable docs-only Slice A PR.

- [ ] **Step 1: Remove all temporary probe material**

Delete only the disposable probe directories outside the repository. If a temporary file was accidentally created inside the repository, inspect it and remove only that task-created file.

- [ ] **Step 2: Verify repository scope**

Run:

```powershell
git status --short
git diff --stat
git diff --check
```

Expected repository diff for Slice A:

```text
reports/design/2026-09-05-resolveops-v3-compatibility.md
```

No package files, frontend source, configuration, screenshots, baselines, backend, or deployment files should be changed.

- [ ] **Step 3: Re-run enough canonical baseline checks to prove the repo itself was not modified by the probe**

From the real repository `frontend/`:

```powershell
npm ci
npm audit
npm run lint
npm test
npm run build
```

Expected: same healthy baseline as Task 1.

- [ ] **Step 4: Commit the report**

```powershell
git add reports/design/2026-09-05-resolveops-v3-compatibility.md
git commit -m "docs: record ResolveOps v3 compatibility decision"
```

- [ ] **Step 5: Push and open a Slice A PR**

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

Require current stable jobs to pass on the final PR head:

```text
backend
frontend
browser
```

Confirm Storybook succeeds in the frontend job and Playwright remains 14/14 in the browser job.

- [ ] **Step 7: Stop before merge**

Do not merge Slice A. Return the report and PR for owner/ChatGPT review. Slice B starts only after the compatibility decision is independently checked.

## Plan self-review

- Spec coverage: Slice A covers Tailwind compatibility, shadcn React Aria initialization, Geist self-hosting, dependency-churn control, and existing quality gates.
- Placeholder scan: angle-bracket values appear only in report templates where the implementer must substitute fresh measured evidence; no implementation behavior is left undefined.
- Type/config consistency: the plan does not establish permanent component APIs; all permanent implementation remains intentionally deferred to Slice B after the compatibility decision.
