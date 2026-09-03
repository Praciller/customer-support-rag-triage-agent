# SDLC Professional Hardening Design

- **Status:** Proposed for owner review
- **Date:** 2026-09-03
- **Repository:** `Praciller/customer-support-rag-triage-agent`
- **Decision:** Incrementally harden the existing React/Vite + FastAPI application instead of rewriting the RAG workflow or migrating frameworks.

## 1. Intent

Upgrade the repository from a strong AI-engineering demo into a reviewable, professional software-engineering portfolio project that follows an agent-assisted SDLC from planning through design, implementation, verification, deployment, and maintenance.

The upgrade must preserve the existing product promise: one customer message becomes a reviewable support decision with intent, urgency, retrieved evidence, a grounded draft, next action, and an inspectable seven-node trace. The system remains explicitly human-reviewed rather than being presented as an autonomous policy authority.

## 2. Why this approach

The current backend already has useful architectural boundaries:

- FastAPI owns trust-boundary validation, rate limiting, ingestion authorization, controlled errors, health/readiness, and the browser API boundary.
- `ApplicationServices` composes retrieval, inference, cache, and the LangGraph workflow.
- the graph has seven typed workflow nodes with evidence, grounding, fallback, degraded-mode, and trace contracts.
- deterministic demo and evaluation paths already exist.
- external GenAI is optional and server-side behind a neutral adapter.

Rewriting these pieces would increase regression risk without materially improving the project's AI-engineering signal.

The largest maintainability gap is the frontend: `frontend/src/App.tsx` currently owns navigation and the major Overview, Triage, Search, Trace, Evaluation, Dataset, and Provider views in one large file. The repository also has a useful but minimal `DESIGN.md`, frontend unit tests, and CI, but lacks an executable component catalog, browser E2E coverage, and visual regression gates.

The design therefore retains React 19 + Vite and focuses on boundaries, design-system governance, testability, and review evidence.

## 3. Goals

1. Make project context explicit and machine-readable for coding agents.
2. Convert the frontend into small feature and component boundaries without changing the backend contract unnecessarily.
3. Make `DESIGN.md` a real source of design-system rules and tokens.
4. Add a component catalog with documented states and accessibility checks.
5. Add browser-level acceptance tests and visual regression for critical flows.
6. Turn acceptance criteria into executable quality gates.
7. Improve GitHub review ergonomics with issue/PR templates, evidence, and reproducible verification commands.
8. Keep the zero-key deterministic demo reliable and deployable on the current free-CPU shape.
9. Preserve the current security and evidence-boundary claims; do not imply semantic prompt-injection immunity or production policy correctness.
10. Make the repository easier for an AI coding agent to change without loading the whole codebase into context.

## 4. Non-goals

- No Next.js migration.
- No backend framework rewrite.
- No LangGraph replacement.
- No managed database/vector-store migration solely for portfolio polish.
- No autonomous support-agent framing.
- No new paid infrastructure requirement.
- No broad dependency churn unrelated to the hardening work.
- No unverified third-party coding-agent skill committed or installed as part of the repository workflow.

## 5. SDLC context architecture

The repository will expose stable context files so agents do not require a giant repeated prompt.

### 5.1 Root context

Add `AGENTS.md` as a concise project contract containing only durable information:

- product purpose and human-review boundary;
- primary entry points;
- repository map;
- backend and frontend run/test/lint/build commands;
- security invariants;
- design-system pointer;
- ADR/spec pointer;
- dependency policy;
- secret-handling policy;
- definition of done.

`AGENTS.md` must stay lean. Details that can be discovered from code do not belong there.

### 5.2 Specifications

Use small task-specific specifications and acceptance criteria rather than one giant project prompt.

Planning hierarchy:

`Requirement -> Epic -> Story -> Subtask -> Given/When/Then acceptance criteria`

Every implementation task should be small enough to finish and verify in one focused coding-agent session when practical.

### 5.3 ADRs

Create `docs/adr/` and record durable decisions rather than forcing future agents to infer them.

Initial ADR set:

1. `0001-retain-react-vite-and-fastapi.md`
2. `0002-design-system-as-a-versioned-contract.md`
3. `0003-testing-pyramid-and-browser-quality-gates.md`
4. `0004-preserve-deterministic-public-demo-boundaries.md`

Each ADR records Context, Options, Decision, and Consequences. A later reversal creates a new ADR and supersedes the old one instead of deleting history.

## 6. Coding-agent skill policy

Skills are progressive context, not permanent prompt payload.

### 6.1 Matt Pocock skills

Use the official Matt Pocock skill set as the primary implementation workflow where applicable, especially for:

- repository setup and orientation;
- specification and requirements interrogation;
- architecture improvement;
- test-driven implementation;
- code review and final verification.

Load only the skill relevant to the current task.

### 6.2 Thananon / 9arm skills

Use official `thananon/9arm-skills` selectively:

- `scrutinize` for an independent critical review;
- `debug-mantra` for evidence-first debugging;
- `post-mortem` after a verified incident/root-cause fix;
- context/session management skills only when a long-running task needs them.

### 6.3 Unverified skills

Do not install or rely on a `/graftify` skill until its canonical source, maintainer, license, and contents can be verified. A similarly named repository is not sufficient evidence of an official coding-agent skill.

## 7. Frontend target architecture

Retain Vite, React, TypeScript, Testing Library, and the existing API contract.

Target structure:

```text
frontend/src/
  app/
    App.tsx
    navigation.ts
    shell/
      AppShell.tsx
      Sidebar.tsx
      Topbar.tsx
  features/
    overview/
      OverviewView.tsx
    triage/
      TriageView.tsx
      TicketComposer.tsx
      TriageDecision.tsx
      TriageMetadata.tsx
    search/
      SearchView.tsx
    trace/
      TraceView.tsx
    evaluation/
      EvaluationView.tsx
      EvaluationChart.tsx
    dataset/
      DatasetView.tsx
    providers/
      ProviderView.tsx
  components/
    ui/
      Badge.tsx
      Button.tsx
      EmptyState.tsx
      ErrorNotice.tsx
      Field.tsx
      Panel.tsx
      StatusIndicator.tsx
    evidence/
      CaseList.tsx
      EvidenceReference.tsx
    trace/
      TraceList.tsx
  lib/
    api.ts
    format.ts
  types/
    api.ts
  styles/
    tokens.css
    base.css
    components.css
    features.css
  main.tsx
```

Exact file names may change during implementation when existing coupling is inspected, but the boundaries must remain feature-oriented rather than returning to a single application file.

### Boundary rules

- `app/` composes navigation and routing-like view selection only.
- `features/` owns workflow-specific UI and state.
- reusable visual primitives live under `components/ui`.
- evidence and trace rendering are separate domain components because they are core product concepts, not generic cards.
- API transport remains in `lib/api.ts`; components do not build endpoint URLs.
- public API response types remain centralized and mirror the backend schema.
- visual components do not contain retrieval, grounding, or escalation business rules.

No full client router is required unless the implementation demonstrates a real product need. The current view-state navigation can remain to avoid unnecessary dependency and URL-contract changes.

## 8. DESIGN.md v2

Replace the current minimal design document with a versioned, machine-readable design contract.

The file will contain YAML front matter for tokens plus prose for rationale and usage.

Required token groups:

- color: canvas, surface, elevated surface, foreground, muted foreground, border, primary, primary-hover, success, warning, danger, focus;
- typography: display, heading, body, label, code, numeric;
- spacing scale;
- radius scale;
- border/elevation rules;
- motion durations and easing;
- layout widths and breakpoints;
- component-level tokens where a component has a stable visual contract.

### Product aesthetic

**ResolveOps: Evidence-first Operational Console**

Characteristics:

- calm, precise, operational;
- light office-workspace canvas;
- dense but readable information hierarchy;
- one cobalt/blue primary action accent;
- semantic amber/red only for meaningful warning and escalation states;
- evidence and trace are highly inspectable but visually subordinate to the current decision;
- tables/open lists are preferred over decorative card grids;
- flat surfaces, hairline borders, restrained elevation;
- no gradients, glassmorphism, glowing AI decoration, or generic chatbot framing.

### Information hierarchy

For the triage workflow, priority is:

1. customer message;
2. recommended decision / human action;
3. grounding and escalation state;
4. retrieved evidence;
5. workflow trace and runtime metadata.

The UI must never make provider/model metadata more visually prominent than the decision or evidence.

### Accessibility contract

- target WCAG 2.2 AA;
- keyboard reachable actions;
- visible focus indicators;
- severity/status never encoded by color alone;
- proper labels for all form controls;
- reduced-motion support;
- meaningful empty, loading, error, unavailable, degraded, and success states;
- charts require textual summaries and must not be the sole representation of evaluation results.

### Responsive contract

Verify at minimum:

- 390px mobile;
- 768px tablet;
- 1440px desktop.

No page-level horizontal overflow is allowed. The desktop split workspace may stack on smaller viewports, but decision information must remain above detailed evidence and traces.

## 9. Storybook component system

Add Storybook for reusable components and critical domain components.

Minimum stories:

- Button: primary, secondary, disabled, loading;
- Badge/StatusIndicator: neutral, success, warning, danger;
- ErrorNotice;
- EmptyState;
- TicketComposer states;
- TriageDecision: standard, escalated, ungrounded, degraded, fallback, cached;
- CaseList: populated and empty;
- TraceList: normal, fallback, degraded;
- evaluation metric/chart display.

Storybook is the executable component catalog. Stories should expose realistic states rather than synthetic decorative examples.

Add accessibility checks for stories where supported. Interaction tests are appropriate for components with meaningful local behavior, but Storybook should not replace full browser acceptance tests.

## 10. Testing strategy

Tests start from expected behavior and acceptance criteria, not from copying current implementation details.

### 10.1 Backend

Keep the current backend lint, formatting, pytest, deterministic evaluation, and adversarial retrieval checks.

Only add backend tests where the hardening work changes a public contract or where a missing invariant becomes visible during implementation.

### 10.2 Frontend unit/component tests

Use Vitest + Testing Library for:

- feature state transitions;
- accessible controls;
- error/loading/empty states;
- decision and evidence rendering;
- regression tests for any behavior moved out of `App.tsx`.

Prefer role/label/text queries over CSS selectors.

### 10.3 Browser E2E

Add Playwright for critical user journeys.

Minimum deterministic E2E flows:

1. public demo opens and reports API status;
2. user selects `Card not arrived`, runs triage, and receives a reviewable decision;
3. decision displays intent, urgency, human action, grounding state, retrieved evidence, and trace;
4. escalated fixture communicates escalation independently of color;
5. evaluation view renders deterministic results;
6. API-unavailable/error state is understandable and does not expose sensitive details.

Selectors should use role, label, and accessible name. Arbitrary sleeps are prohibited.

### 10.4 Visual regression

Add Playwright screenshot baselines for a small set of high-signal screens:

- triage initial state;
- triage successful result;
- escalated result;
- evaluation desktop;
- representative 390px mobile view.

Freeze or mask nondeterministic data and disable animation during screenshot capture. Baselines are updated only after explicit review of image diffs.

## 11. CI quality gates

Preserve the current backend and frontend jobs, then extend CI incrementally.

Target PR checks:

### Backend job

- install deterministic CPU dependencies;
- Ruff lint;
- Ruff format check;
- pytest;
- adversarial retrieval evaluation;
- deterministic demo evaluation.

### Frontend job

- `npm ci`;
- ESLint;
- Vitest;
- TypeScript/Vite production build;
- Storybook static build.

### Browser job

- build/start the deterministic application stack required for browser tests;
- Playwright critical-flow E2E;
- visual regression;
- upload HTML report, trace, and screenshot diffs on failure.

The browser job must run with deterministic demo/mock configuration and must not require external GenAI credentials.

CI failures block merge for the affected hardening branch once the workflows are stable.

## 12. GitHub review workflow

Add repository templates that make work agent-ready.

### Feature/engineering issue template

Required fields:

- Problem / context;
- User or reviewer value;
- Scope;
- Non-goals;
- Acceptance criteria in Given/When/Then;
- Files or modules likely involved;
- Security/data considerations;
- Verification commands;
- Evidence required for completion.

### Pull request template

Required sections:

- Summary;
- Why;
- Scope / non-goals;
- Acceptance criteria status;
- Testing evidence;
- screenshots or browser evidence when UI changes;
- security/evidence-boundary impact;
- documentation/ADR impact;
- rollback notes when deployment/runtime behavior changes.

Do not generate vanity badges or process documents that are not used by the actual workflow.

## 13. Deployment and operations

Keep the existing CPU-container/Hugging Face deployment path unless implementation evidence shows it is broken.

Hardening work must:

- keep deployment reproducible from repository files;
- preserve zero-key public operation;
- document exact verification commands;
- keep secrets server-side;
- verify health/readiness and a representative triage flow after deployment;
- capture desktop/mobile screenshots only after the deployed revision is confirmed.

No CI/CD deployment automation should be introduced until the manual repository-defined deployment path is proven on the target environment.

## 14. Security invariants

The upgrade must preserve these existing boundaries:

- retrieved content is untrusted evidence, never workflow authority;
- evidence references must correspond to actually retrieved records;
- empty evidence, rejected citations, or degraded generation cannot be presented as a grounded final result;
- ungrounded output routes to human review;
- credentials, raw prompts, local paths, environment values, and stack traces are not exposed publicly;
- external inference remains optional, explicit, and server-side;
- public demo claims remain limited to deterministic structural/evidence-boundary checks, not universal semantic prompt-injection immunity;
- Banking77-derived examples remain precedent/demo evidence, not company policy.

Frontend refactoring must not weaken these messages or hide degraded/manual-review states.

## 15. Documentation deliverables

By the end of the hardening program, documentation should include:

- concise `AGENTS.md`;
- `PRODUCT.md` aligned with the final UI;
- `DESIGN.md` v2;
- ADR set;
- architecture diagram updated only if runtime boundaries change;
- testing strategy and browser-test instructions;
- deployment/runbook verification evidence;
- README recruiter path updated to current screenshots and exact verified behavior.

Documentation must be generated or updated from actual code and verification evidence, then reviewed before publication.

## 16. Implementation phases

### Phase 0 — Context and guardrails

- add `AGENTS.md`;
- add ADRs;
- upgrade `DESIGN.md` specification;
- add GitHub issue/PR templates;
- document Definition of Done and verification commands.

No runtime behavior should change in this phase.

### Phase 1 — Frontend decomposition

- establish app/feature/component boundaries;
- move existing behavior without redesigning it first;
- preserve or improve unit tests during every extraction;
- ensure production build remains unchanged from the API perspective.

### Phase 2 — Design-system implementation

- introduce design tokens as CSS custom properties/source-of-truth styles;
- convert components to use tokens instead of repeated hard-coded values;
- standardize button, status, input, panel, evidence, and trace contracts;
- implement responsive and accessibility rules from `DESIGN.md`.

### Phase 3 — Storybook and component QA

- add Storybook;
- add required component/domain stories;
- add interaction/a11y checks where valuable;
- make Storybook static build a CI check.

### Phase 4 — Browser acceptance and visual regression

- add Playwright;
- implement critical deterministic flows;
- add a small, stable screenshot baseline set;
- upload useful browser artifacts in CI.

### Phase 5 — Repository quality gates

- finalize CI jobs and failure evidence;
- remove obsolete or duplicated configuration exposed during the refactor;
- perform security review and an independent scrutinize/review pass;
- ensure no new secret or provider dependency has entered the public demo.

### Phase 6 — Deployment verification and portfolio evidence

- verify the real deployed revision;
- run health/readiness + representative browser journey;
- capture final desktop/mobile screenshots;
- update README and portfolio/recruiter evidence only with verified claims.

## 17. Acceptance criteria

### AC-1 — Existing product behavior survives decomposition

**Given** the deterministic demo configuration,
**when** a known demo ticket is triaged after the frontend refactor,
**then** the user can still inspect intent, urgency, next action, response, grounding state, evidence, and all seven trace steps without a backend contract regression.

### AC-2 — Design system is a source of truth

**Given** a reusable UI component,
**when** its visual implementation is inspected,
**then** stable color/spacing/type/radius values come from documented design tokens rather than independent arbitrary values.

### AC-3 — Human-review boundary stays obvious

**Given** ungrounded, degraded, fallback, or escalation output,
**when** the result is rendered,
**then** the UI communicates the state using explicit text/semantics and the human-review action remains visible without relying on color alone.

### AC-4 — Component behavior is independently reviewable

**Given** a core reusable or domain component,
**when** Storybook is opened,
**then** its important states/variants can be inspected without navigating the full application.

### AC-5 — Critical journeys are browser-tested

**Given** CI running the deterministic demo,
**when** the Playwright suite executes,
**then** critical triage and evaluation journeys pass using accessible selectors and produce traces/screenshots for failures.

### AC-6 — Visual regressions are intentional

**Given** a protected screenshot baseline,
**when** layout or styling changes beyond tolerance,
**then** CI fails and provides an inspectable expected/actual/diff artifact rather than silently accepting the change.

### AC-7 — Responsive behavior is verified

**Given** 390px, 768px, and 1440px viewports,
**when** the critical pages are rendered,
**then** there is no page-level horizontal overflow and decision content remains above subordinate evidence/trace content on constrained screens.

### AC-8 — Accessibility basics are enforced

**Given** keyboard-only navigation and reduced-motion preference,
**when** the core triage flow is used,
**then** all required actions are reachable, focus is visible, controls have semantic labels, statuses are not color-only, and non-essential motion is suppressed.

### AC-9 — Public demo remains zero-key

**Given** a clean public-demo environment without external model credentials,
**when** the application starts and the representative browser flow runs,
**then** deterministic triage works and no client-side or server response leaks a credential or external endpoint detail.

### AC-10 — Merge evidence is reproducible

**Given** a hardening pull request,
**when** a reviewer follows the documented commands,
**then** lint, tests, deterministic evaluation, build, and applicable browser checks can be reproduced from repository state.

## 18. Risks and mitigations

### Frontend behavior changes during extraction

Mitigation: move behavior in small slices, preserve component tests, and delay visual redesign until boundaries are stable.

### Storybook/Playwright increase dependency and CI weight

Mitigation: keep the story set and browser suite small and high-signal; do not duplicate backend evaluation logic in browser tests.

### Visual tests become flaky

Mitigation: deterministic demo data, fixed viewport/environment, disabled animation, masked dynamic regions, and explicit review before baseline updates.

### Agent context grows again

Mitigation: lean `AGENTS.md`, task-specific specs, ADRs for decisions, and skill progressive disclosure.

### Portfolio polish overstates production readiness

Mitigation: preserve current security/limitations language and require evidence for every new README claim.

## 19. Definition of done for the hardening program

The program is complete when:

- all acceptance criteria above pass;
- backend deterministic and adversarial evaluations remain reproducible;
- frontend code is feature/component structured rather than centered in one monolithic application file;
- `DESIGN.md` v2 is implemented by actual tokens/components;
- Storybook and Playwright are part of the repeatable workflow;
- CI reports actionable evidence;
- security and human-review boundaries remain intact;
- the deployed zero-key demo is verified on the final revision;
- README screenshots and claims match the verified deployed product;
- no unverified skill, secret, or unnecessary paid dependency is introduced.

## 20. Decision record

Proceed with **incremental professional hardening**. Preserve the proven RAG/backend architecture, retain React/Vite, and improve the project through explicit SDLC context, modular frontend boundaries, a machine-readable design system, executable component documentation, browser acceptance tests, visual regression, and evidence-driven GitHub quality gates.
