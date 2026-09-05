# ResolveOps v3 Slice C — Shell and Responsive Navigation

## Scope

Redesign only the application shell, navigation hierarchy, responsive navigation, and system-status placement. Preserve all feature-page internals, API behavior, data semantics, and evaluation content.

## Tasks

- [ ] Baseline: run frontend install, audit, lint, unit, build, Storybook, and Playwright gates.
- [ ] Inventory current shell, view state, navigation styles, and accessibility behavior.
- [ ] Define grouped primary workflow and subordinate tools information architecture.
- [ ] Extract shell responsibilities into focused components without introducing routing.
- [ ] Implement labelled desktop navigation with semantic current state and status.
- [ ] Implement compact responsive header and labelled primary navigation.
- [ ] Implement accessible React Aria-compatible More control for secondary tools.
- [ ] Add keyboard, focus-visible, Escape, and focus-return tests.
- [ ] Add shell Storybook stories for desktop, mobile, and More-open states.
- [ ] Add unit and semantic browser coverage at 390, 768, and 1440px.
- [ ] Run visual tests without snapshot updates; inspect and classify shell-only diffs.
- [ ] Refresh only inspected shell baselines if required.
- [ ] Capture the seven-image local owner-review archive and contact sheet outside the repo.
- [ ] Run full frontend and unchanged backend safety matrices.
- [ ] Scrutinize scope, accessibility, CSS, and feature regressions.
- [ ] Commit logically, push the Slice C branch, open the Issue #74 PR, and wait for final-head CI.

## Commands

From `frontend`: `npm ci`, `npm audit`, `npm run lint`, `npm test`, `npm run build`, `npm run build-storybook`, `npm run test:e2e`.

From repository root: `ruff check src tests`, `ruff format --check src tests`, `python -m pytest`, adversarial evaluation with a temporary report, and `make demo`.

## Do not touch

Backend, RAG, API, prompts, data, deployment, evaluation semantics, Triage DecisionWorkspace, Evidence, Trace, Evaluation internals, or Slice D work.
