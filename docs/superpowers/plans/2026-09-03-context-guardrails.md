# Context and Guardrails Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Keep execution bounded and coordinated; do not fan out write-heavy work.

**Goal:** Establish durable agent context, architectural decisions, a machine-readable ResolveOps design contract, GitHub review templates, and a repository Definition of Done without changing runtime behavior.

**Architecture:** This phase changes documentation and workflow contracts only. It creates concise root context plus ADR/design/review artifacts that future coding-agent sessions can load progressively instead of rereading the repository.

**Tech Stack:** Markdown, GitHub issue forms/templates, existing Python/React verification commands.

**Spec:** `docs/superpowers/specs/2026-09-03-sdlc-professional-hardening-design.md`

## Global Constraints

- Retain React 19 + Vite + FastAPI and the existing seven-node RAG workflow.
- No Next.js migration, backend rewrite, LangGraph replacement, paid-infrastructure requirement, autonomous-support framing, or unrelated dependency churn.
- The deterministic public path must remain zero-key; external GenAI stays optional and server-side.
- Retrieved content remains untrusted evidence, not workflow authority.
- Do not imply production policy correctness or semantic prompt-injection immunity.
- Do not install or invoke `/graftify` until a canonical source, maintainer, license, and skill contents are verified.

---

### Task 1: Create lean root agent context

**Files:**
- Create: `AGENTS.md`

**Interfaces:**
- Consumes: `PRODUCT.md`, `DESIGN.md`, `docs/architecture.md`, `docs/security.md`, `docs/evaluation.md`, `README.md`.
- Produces: the durable entry-point contract future implementation sessions must read before task-specific specs/plans.

- [ ] **Step 1: Write an agent-context validation command before creating the file**

Run from repository root:

```bash
python - <<'PY'
from pathlib import Path
p = Path('AGENTS.md')
assert not p.exists(), 'AGENTS.md already exists; inspect before replacing'
print('expected precondition: AGENTS.md absent')
PY
```

Expected: prints `expected precondition: AGENTS.md absent`.

- [ ] **Step 2: Create `AGENTS.md` with the following durable sections**

```markdown
# AGENTS.md

## Product contract
ResolveOps turns one customer-support message into a reviewable decision: intent, urgency, retrieved precedent, grounded draft response, next action, and seven-node execution trace. It drafts for human review; Banking77-derived examples are demo precedent, not company policy.

## Repository map
- `src/api/` — HTTP validation and public API boundary.
- `src/graph/` — typed seven-node LangGraph orchestration.
- `src/retrieval/` — Qdrant retrieval and embeddings.
- `src/llm/` — deterministic/local and optional external inference routing.
- `src/evaluation/` — deterministic evaluation and reports.
- `frontend/` — React/Vite operations console.
- `data/demo/` — bounded deterministic fixture.
- `docs/` — architecture, security, evaluation, deployment, runbook, ADRs.

## Source-of-truth docs
Read only what the task needs:
1. `PRODUCT.md` for user/product purpose.
2. `DESIGN.md` for UI/design tokens and interaction rules.
3. `docs/architecture.md` for runtime boundaries and node contracts.
4. `docs/security.md` for evidence, secret, and public-API invariants.
5. `docs/evaluation.md` for metric methodology and limitations.
6. `docs/superpowers/specs/2026-09-03-sdlc-professional-hardening-design.md` plus the relevant plan under `docs/superpowers/plans/` for this hardening program.

## Security invariants
- Retrieved messages are untrusted evidence, never system/developer/workflow instructions.
- Evidence references are valid only when IDs were actually retrieved.
- Empty evidence, rejected citations, or degraded generation cannot be presented as grounded.
- Ungrounded output routes to human review.
- Never expose credentials, raw prompts, environment values, external endpoint URLs, stack traces, or local paths in public output/artifacts.
- External inference remains optional, explicit, server-side, and outside the default public demo.

## Dependency policy
Keep the existing stack unless an accepted requirement proves a dependency is necessary. Do not add a framework migration, client router, state-management library, component mega-library, analytics product, or unverified agent skill for convenience.

## Verification
Backend from repository root:
```bash
ruff check src tests
ruff format --check src tests
python -m pytest
python -m src.evaluation.evaluate_adversarial_retrieval --report-path /tmp/adversarial_retrieval.md
```

Deterministic evaluation uses the repository-defined demo environment (`make demo` on supported shells, or the equivalent environment variables documented in README/Makefile).

Frontend:
```bash
cd frontend
npm ci
npm run lint
npm test
npm run build
```

After Storybook/Playwright are introduced, UI behavior changes must also run the repository Storybook build and critical browser suite defined by their plan.

## Definition of Done
A bounded change is done only when:
- its Given/When/Then acceptance criteria pass;
- relevant lint/type/build/unit/integration/browser checks pass;
- security/evidence boundaries are unchanged or explicitly reviewed;
- UI status remains understandable without color alone;
- docs and screenshots describe verified behavior only;
- no secret, private path, raw prompt, or unsupported production claim is committed;
- the diff remains inside the accepted task scope.

## Stop conditions
Stop and request review rather than silently broadening scope if implementation would require changing the public backend contract, weakening evidence/grounding semantics, adding an unplanned framework/dependency, using external credentials for deterministic acceptance, repairing unrelated failures, or performing owner-authenticated deployment/secret entry.
```

- [ ] **Step 3: Validate required pointers and prohibited secret-like content**

Run:

```bash
python - <<'PY'
from pathlib import Path
text = Path('AGENTS.md').read_text(encoding='utf-8')
for required in [
    'PRODUCT.md', 'DESIGN.md', 'docs/architecture.md', 'docs/security.md',
    'docs/evaluation.md', 'Definition of Done', 'Stop conditions',
]:
    assert required in text, required
for forbidden in ['API_KEY=', 'gsk_', 'csk-', 'BEGIN PRIVATE KEY']:
    assert forbidden not in text, forbidden
print('AGENTS.md contract OK')
PY
```

Expected: `AGENTS.md contract OK`.

- [ ] **Step 4: Run documentation-only diff check**

```bash
git diff --check -- AGENTS.md
git status --short
```

Expected: only `AGENTS.md` is new for this task.

- [ ] **Step 5: Commit**

```bash
git add AGENTS.md
git commit -m "docs: add agent context contract"
```

---

### Task 2: Record four architectural decisions

**Files:**
- Create: `docs/adr/0001-retain-react-vite-and-fastapi.md`
- Create: `docs/adr/0002-design-system-as-versioned-contract.md`
- Create: `docs/adr/0003-testing-pyramid-and-browser-quality-gates.md`
- Create: `docs/adr/0004-preserve-deterministic-public-demo-boundaries.md`

**Interfaces:**
- Consumes: approved design spec and current architecture/security docs.
- Produces: durable decision history referenced by `AGENTS.md` and future PRs.

- [ ] **Step 1: Create ADR directory and first ADR**

`0001-retain-react-vite-and-fastapi.md` must state:

```markdown
# ADR 0001: Retain React/Vite and FastAPI

- Status: Accepted
- Date: 2026-09-03

## Context
The repository already has a working React 19/Vite console, FastAPI trust boundary, typed seven-node LangGraph workflow, deterministic evaluation, and a free CPU deployment path. The main maintainability gap is frontend decomposition and verification, not framework capability.

## Options considered
1. Incrementally harden the existing React/Vite + FastAPI stack.
2. Rebuild the React frontend in place.
3. Migrate the frontend to Next.js.

## Decision
Use option 1. Preserve the public API and RAG runtime boundaries unless a separately accepted requirement proves a change is necessary.

## Consequences
- Lower regression risk and smaller reviewable diffs.
- Existing deployment and deterministic demo remain usable.
- Frontend architecture improves through feature/component boundaries rather than a framework migration.
- A future framework change requires a new ADR that supersedes this decision.
```

- [ ] **Step 2: Create design-system ADR**

`0002-design-system-as-versioned-contract.md` must accept `DESIGN.md` as the versioned source for tokens, hierarchy, responsive behavior, accessibility, motion, and component-state rules; CSS consumes those rules rather than inventing new hard-coded visual values.

- [ ] **Step 3: Create testing/quality-gate ADR**

`0003-testing-pyramid-and-browser-quality-gates.md` must record:
- Vitest/Testing Library for component/feature behavior;
- Storybook for isolated states/documentation/a11y;
- Playwright for deterministic end-to-end acceptance and selected visual regression;
- role/label selectors and no arbitrary sleeps;
- CI reports/traces/screenshots as review evidence;
- existing backend deterministic/adversarial checks remain mandatory.

- [ ] **Step 4: Create deterministic-demo ADR**

`0004-preserve-deterministic-public-demo-boundaries.md` must record:
- default public/demo path requires no external credential;
- retrieved examples are precedent/evidence, not policy authority;
- degraded or invalid-citation paths cannot look grounded;
- semantic LLM prompt-injection immunity is not established by deterministic tests;
- external GenAI remains optional and server-side.

- [ ] **Step 5: Validate ADR shape**

```bash
python - <<'PY'
from pathlib import Path
files = sorted(Path('docs/adr').glob('000*.md'))
assert len(files) == 4, files
for p in files:
    text = p.read_text(encoding='utf-8')
    for heading in ['## Context', '## Decision', '## Consequences']:
        assert heading in text, (p, heading)
    assert 'Status: Accepted' in text, p
print('4 ADRs valid')
PY
```

Expected: `4 ADRs valid`.

- [ ] **Step 6: Commit**

```bash
git add docs/adr
git commit -m "docs: record hardening architecture decisions"
```

---

### Task 3: Upgrade `DESIGN.md` to ResolveOps v2 contract

**Files:**
- Modify: `DESIGN.md`

**Interfaces:**
- Consumes: `PRODUCT.md` product principles and existing visual values.
- Produces: token names later implemented by `frontend/src/styles/tokens.css` and semantic component-state rules used by frontend stories/tests.

- [ ] **Step 1: Add versioned machine-readable front matter**

Use these exact token names; values may retain/refine the current OKLCH palette but must remain within the approved restrained operational aesthetic:

```yaml
---
version: 2
name: ResolveOps
aesthetic: evidence-first-operational-console
color_tokens:
  canvas: "oklch(0.975 0.006 245)"
  surface: "oklch(0.995 0.004 245)"
  surface_muted: "oklch(0.948 0.010 245)"
  foreground: "oklch(0.245 0.025 250)"
  foreground_muted: "oklch(0.510 0.025 250)"
  border: "oklch(0.875 0.018 245)"
  primary: "oklch(0.555 0.180 258)"
  success: "oklch(0.565 0.125 154)"
  warning: "oklch(0.700 0.145 76)"
  danger: "oklch(0.560 0.190 28)"
  focus: "oklch(0.555 0.180 258)"
typography:
  family_ui: "Inter, Segoe UI, system-ui, sans-serif"
  family_code: "ui-monospace, SFMono-Regular, Consolas, monospace"
  scale_px: [12, 14, 16, 20, 26, 34]
spacing_px: [4, 8, 12, 16, 24, 32, 48]
radius_px: [6, 10, 14]
motion:
  fast_ms: 120
  standard_ms: 180
  easing: "ease-out"
breakpoints_px:
  mobile: 390
  tablet: 768
  desktop: 1440
---
```

- [ ] **Step 2: Add explicit information hierarchy and status rules**

The prose must state this order exactly:

1. customer message;
2. recommended decision / human action;
3. grounding and escalation state;
4. retrieved evidence;
5. workflow trace and runtime metadata.

Status rules must require visible text and/or icon/shape semantics for `neutral`, `success`, `warning`, and `danger`; color is supplementary only.

- [ ] **Step 3: Add component and state contracts**

Document Button, Field/Input, Panel, Badge/StatusIndicator, EmptyState, ErrorNotice, TriageDecision, CaseList/Evidence, TraceList, table/chart, loading, unavailable, degraded, fallback, cached, ungrounded, and escalated states.

- [ ] **Step 4: Add responsive/accessibility/motion/anti-pattern rules**

Required statements:
- target WCAG 2.2 AA;
- visible focus and keyboard operation;
- `prefers-reduced-motion` disables non-essential motion;
- no page-level horizontal overflow at 390/768/1440;
- narrow screens put decision before detailed evidence/trace;
- charts require textual summaries;
- no gradients, glassmorphism, decorative AI glow, or generic chatbot framing.

- [ ] **Step 5: Validate token/rule presence**

```bash
python - <<'PY'
from pathlib import Path
text = Path('DESIGN.md').read_text(encoding='utf-8')
for token in [
    'version: 2', 'name: ResolveOps', 'color_tokens:', 'spacing_px:',
    'breakpoints_px:', 'WCAG 2.2 AA', 'prefers-reduced-motion',
    'customer message', 'retrieved evidence', 'workflow trace',
]:
    assert token in text, token
print('DESIGN.md v2 contract OK')
PY
```

Expected: `DESIGN.md v2 contract OK`.

- [ ] **Step 6: Commit**

```bash
git add DESIGN.md
git commit -m "docs: version ResolveOps design contract"
```

---

### Task 4: Add GitHub issue/PR templates and Definition-of-Done review surface

**Files:**
- Create: `.github/ISSUE_TEMPLATE/engineering.yml`
- Create: `.github/pull_request_template.md`

**Interfaces:**
- Consumes: `AGENTS.md` Definition of Done and approved design acceptance format.
- Produces: required planning/review fields for future implementation issues/PRs.

- [ ] **Step 1: Create engineering issue form**

The form must require fields for: problem/context, user or reviewer value, scope, non-goals, Given/When/Then acceptance criteria, likely modules, security/data considerations, verification commands, and completion evidence.

Use a YAML issue form with `name: Engineering task`, `description: Bounded agent-ready engineering work`, and a title prefix `[Engineering] `.

- [ ] **Step 2: Create PR template**

Use these headings:

```markdown
## Summary
## Why
## Scope
## Non-goals
## Acceptance criteria
## Verification evidence
## UI / browser evidence
## Security and evidence-boundary impact
## Documentation / ADR impact
## Deployment / rollback impact
```

Under verification evidence, explicitly request exact commands and pass/fail output; under UI/browser evidence request screenshots or Playwright/Storybook evidence when UI changes.

- [ ] **Step 3: Validate GitHub template files**

```bash
python - <<'PY'
from pathlib import Path
issue = Path('.github/ISSUE_TEMPLATE/engineering.yml').read_text(encoding='utf-8')
pr = Path('.github/pull_request_template.md').read_text(encoding='utf-8')
for item in ['Given', 'When', 'Then', 'security', 'verification', 'evidence']:
    assert item.lower() in issue.lower(), item
for heading in ['## Acceptance criteria', '## Verification evidence', '## Security and evidence-boundary impact']:
    assert heading in pr, heading
print('GitHub review templates OK')
PY
```

Expected: `GitHub review templates OK`.

- [ ] **Step 4: Run no-runtime-change verification**

```bash
git diff --check
python -m pytest
cd frontend && npm test && npm run build
```

Expected: current backend/frontend behavior remains green; only documentation/workflow files changed in this phase.

- [ ] **Step 5: Commit**

```bash
git add .github/ISSUE_TEMPLATE/engineering.yml .github/pull_request_template.md
git commit -m "docs: add agent-ready review templates"
```

---

## Phase review gate

Before moving to frontend code:

```bash
git diff main...HEAD --name-only
```

Expected paths are limited to `AGENTS.md`, `DESIGN.md`, `.github/ISSUE_TEMPLATE/engineering.yml`, `.github/pull_request_template.md`, `docs/adr/*`, and planning/spec files. Run an independent read-only review for contradictions, placeholder text, security-boundary drift, and unnecessary process artifacts. Resolve evidence-backed findings before the next phase.