# ResolveOps Design System v3

Date: 2026-09-05  
Status: Proposed for implementation after owner review  
Base commit: `992b07d6aee9e533d2c31a711b19dc719940c74c`

## 1. Goal

Raise the frontend from a custom but relatively shallow component layer into a coherent, reusable, accessible product design system without changing backend, LangGraph, RAG, evaluation semantics, deployment behavior, or human-review boundaries.

The target experience is a professional AI operations workspace: calm, dense, precise, evidence-first, and clearly distinct from a generic chatbot or decorative dashboard.

The implementation must preserve the current information hierarchy:

1. customer message;
2. recommended decision / human action;
3. grounding and escalation state;
4. retrieved evidence;
5. workflow trace and runtime metadata.

## 2. Why a v3 system is needed

`DESIGN.md` v2 already defines useful machine-readable tokens, accessibility rules, semantic states, responsive breakpoints, and domain component contracts. The gap is implementation depth: the current UI foundation consists mainly of project-local components such as Button, Field, Badge, StatusIndicator, Panel, EmptyState, and ErrorNotice, with no mature accessible primitive layer underneath them.

The result is functionally correct and testable, but visual density, state consistency, navigation, interaction polish, and reusable composition are still weaker than the written design contract.

This phase therefore changes the frontend foundation, not the application product model.

## 3. Source guidance

The attached AI Coding Agent for SDLC material defines the frontend path as `UI Design -> Design System -> Component -> Page`, with the design system covering style guide, color palette, typography, spacing/layout, design tokens, and grid. It also treats `DESIGN.md` as machine-readable design context for coding agents and recommends Storybook as the live component catalog.

Current upstream shadcn/ui documentation confirms:

- Vite is supported for existing projects;
- React Aria is a first-class shadcn component base;
- React Aria can be selected with `--base aria`;
- the available visual styles include Mira, Nova, Lyra, Maia, Vega, Luma, Rhea, and Sera;
- shadcn recommends progressive component-by-component adoption rather than unsafe wholesale rewrites.

Impeccable is optional design-review tooling only; it must not become the product's runtime UI dependency or source of truth.

## 4. Options considered

### Option A — shadcn/ui + React Aria + ResolveOps theme — selected

Use shadcn-owned source components with React Aria as the accessible primitive base, then theme them through ResolveOps semantic tokens and domain composition.

Benefits:

- accessible interaction foundation;
- source ownership and full customization;
- compatible with Vite;
- avoids adopting another company's visual identity;
- works well with Storybook and current test strategy;
- allows progressive migration.

Costs:

- requires deliberate token mapping and component ownership;
- some migration work is needed around Tailwind and generated component styles;
- generated defaults must be reviewed to avoid generic shadcn appearance.

### Option B — Carbon Design System

Strong enterprise accessibility and data-heavy component coverage, but carries recognizable IBM visual language and would constrain ResolveOps brand ownership more than desired.

### Option C — PatternFly

Strong for operations/admin software, but the Red Hat/cloud-console visual language is too dominant for this portfolio product.

Decision: Option A.

## 5. Selected architecture

```text
ResolveOps Design System v3
        |
        +-- DESIGN.md v3: semantic tokens + product rules
        |
        +-- shadcn/ui source components
        |       |
        |       +-- React Aria base
        |
        +-- ResolveOps domain components
        |
        +-- Triage / Evaluation / Trace pages
```

The architecture has three layers.

### 5.1 Foundation

`DESIGN.md` remains the source of truth for product semantics and visual decisions.

Foundation tokens cover:

- semantic colors;
- typography;
- spacing;
- radius;
- borders/elevation;
- motion;
- responsive breakpoints;
- density;
- focus and interaction states.

The existing restrained OKLCH identity remains the starting palette. Cobalt remains the primary action accent; success/warning/danger remain semantic only.

### 5.2 Accessible UI primitives

Adopt a bounded set of shadcn/ui components generated from the React Aria base. Initial primitive candidates:

- Button;
- IconButton-equivalent composition;
- Input;
- Textarea;
- Label / Field composition;
- Badge;
- Alert;
- Tooltip;
- Separator;
- Tabs;
- Table primitives where useful;
- Skeleton;
- Dialog / Sheet only if a real flow requires them;
- ScrollArea only if existing page behavior benefits.

Do not add components solely because the registry offers them.

### 5.3 ResolveOps domain components

Keep domain meaning outside generic primitives. Target domain components include:

- CustomerMessage;
- DecisionPanel;
- GroundingStatus;
- UrgencyStatus;
- EvidenceCard / EvidenceList;
- WorkflowTrace / TraceStep;
- RuntimeMetadata;
- EvaluationMetric;
- EvaluationChart.

Domain components may use shadcn primitives internally, but their public API must express ResolveOps concepts rather than registry implementation details.

## 6. Visual direction

Use Mira as inspiration for compact application density, not as a copied theme.

ResolveOps v3 should feel:

- calm rather than flashy;
- compact rather than spacious marketing UI;
- operational rather than decorative;
- evidence-first rather than metric-card-first;
- clear under pressure;
- visually differentiated by hierarchy, not by excessive color.

### Required visual rules

- No gradients.
- No glassmorphism.
- No glowing AI effects.
- No generic chat bubbles as the primary product frame.
- No card spam for every metric or metadata field.
- Keep borders and shallow elevation restrained.
- Use one dominant primary accent.
- Use semantic colors only for semantic state.
- Avoid excessive rounding; use the declared radius scale.
- Body content remains readable at dense information levels.
- Direct labels are preferred to icon-only meaning.

## 7. Layout system

### Desktop

Adopt a stable application shell with compact navigation and one main workspace.

Suggested structure:

```text
+---------------------------------------------------------------+
| ResolveOps                         API Ready        Utilities   |
+---------------+-----------------------------------------------+
| Triage        | Customer message                              |
| Evaluation    |                                               |
| Trace         | Recommended action / human decision           |
|               | Grounding / escalation                        |
|               |                                               |
|               | Evidence                                      |
|               |                                               |
|               | Workflow trace / metadata                     |
+---------------+-----------------------------------------------+
```

Navigation must not overpower the work surface. A sidebar may collapse on narrower desktop/tablet widths if implemented accessibly.

### Mobile

At 390px, maintain the current mandatory content order:

`decision -> grounding/escalation -> evidence -> trace`.

Navigation may become a compact top-level control or sheet only if keyboard and focus behavior remain correct.

No page-level horizontal overflow at 390, 768, or 1440.

## 8. Token strategy

`DESIGN.md` v3 will retain semantic token names rather than expose registry-specific color names.

Expected roles include:

- canvas;
- surface;
- surface-muted;
- foreground;
- foreground-muted;
- border;
- primary;
- primary-foreground;
- success;
- warning;
- danger;
- focus;
- selected;
- disabled.

Spacing should remain on a small deliberate scale. A density token should distinguish compact control height from normal content spacing.

Registry-generated CSS variables must be mapped to ResolveOps semantic roles. Generated theme values are not accepted as product decisions by default.

## 9. Tailwind migration policy

The project currently has Tailwind 3.x in devDependencies. Current shadcn examples use the modern toolchain, but the redesign must not mix a broad dependency upgrade with visual migration without evidence.

Implementation must begin with a compatibility spike on an isolated branch/worktree to determine the least risky path:

1. verify whether the selected React Aria shadcn components can be introduced cleanly in the existing Vite project;
2. determine whether Tailwind 3 can be retained temporarily or whether a controlled Tailwind 4 migration is necessary;
3. if Tailwind 4 is required, perform it as its own reviewable slice with app behavior unchanged;
4. do not combine unrelated package upgrades.

No `npm audit fix --force` and no dependency churn unrelated to design-system adoption.

## 10. Component migration strategy

Migrate progressively and keep the app runnable after every slice.

Suggested sequence:

1. foundation/tokens and utility setup;
2. Button and Field/Input;
3. Badge/Status/Alert states;
4. Panel/surface composition;
5. app shell/navigation;
6. Triage decision and message hierarchy;
7. Evidence components;
8. Workflow trace;
9. Evaluation metrics/chart shell;
10. final responsive/a11y polish.

Existing component APIs should be preserved where cheap. If an API change is necessary, update consumers in the same bounded slice and keep tests green.

## 11. Storybook contract

Storybook becomes the design-system catalog, not merely a component preview.

Required Storybook groups:

- Foundations;
- Primitives;
- Status and feedback;
- Domain / Triage;
- Domain / Evidence;
- Domain / Trace;
- Domain / Evaluation.

For meaningful components, stories should cover:

- default;
- hover/focus where practical;
- disabled;
- loading;
- error/unavailable;
- degraded/fallback;
- ungrounded/escalated where applicable;
- narrow viewport for layout-sensitive components.

Accessibility addon remains required.

## 12. Testing and QA

The existing test stack remains mandatory.

### Unit/component

- preserve existing Vitest coverage;
- add focused tests when component behavior or accessibility contracts change;
- avoid snapshot-only assertions for interactive semantics.

### Storybook

- static build must pass;
- stories must use real component APIs and semantic states;
- a11y violations in new/changed stories are blockers unless documented false positives.

### Playwright

Keep the real-backend deterministic flow and visual regression strategy.

Critical invariants:

- API state remains visible;
- `Card not arrived` still produces the same business result;
- seven workflow stages remain ordered and visible;
- ungrounded/degraded states preserve manual review;
- decision precedes evidence and trace on 390px;
- no page-level overflow at 390/768/1440;
- no baseline update is accepted without human visual review.

### Visual review

Every major migration slice must be inspected at 1440 desktop and 390 mobile. The goal is visual improvement plus semantic preservation, not merely snapshot acceptance.

## 13. Accessibility

Target WCAG 2.2 AA remains unchanged.

Required:

- keyboard operability;
- visible focus;
- semantic labels and landmarks;
- status meaning not carried by color alone;
- reduced-motion handling;
- chart text summary;
- correct focus management for any dialog/sheet/navigation overlay;
- sufficient contrast after token changes.

React Aria primitives are an implementation aid, not proof of accessibility by themselves.

## 14. Impeccable usage

Impeccable may be installed project-locally as an optional coding-agent design-review skill if its source/license remain verified at implementation time.

Allowed uses:

- critique;
- audit;
- polish;
- deterministic design-quality detection.

It must not:

- modify product semantics without explicit review;
- replace `DESIGN.md`;
- introduce runtime dependencies;
- override accessibility/test evidence;
- be trusted as the sole visual reviewer.

## 15. Non-goals

This phase does not include:

- backend changes;
- LangGraph changes;
- RAG/retrieval changes;
- model/provider changes;
- evaluation fixture changes;
- Next.js migration;
- new paid infrastructure;
- autonomous-support framing;
- dark mode unless separately approved;
- a full routing rewrite;
- analytics/product feature expansion.

## 16. Rollout plan

Implementation should be decomposed into small PRs rather than one large redesign PR.

Recommended slices:

### Slice A — Foundation compatibility spike

- verify shadcn + React Aria integration on current Vite app;
- resolve Tailwind compatibility decision;
- no user-visible redesign required.

### Slice B — Design foundation

- `DESIGN.md` v3;
- semantic CSS variables/tokens;
- base primitive setup;
- Storybook foundation stories.

### Slice C — Shell + navigation

- application shell;
- responsive navigation;
- current page routing behavior preserved.

### Slice D — Triage workspace

- customer message;
- decision panel;
- grounding/escalation;
- evidence composition.

### Slice E — Trace + evaluation

- seven-node trace;
- runtime metadata;
- evaluation metrics/chart presentation.

### Slice F — QA and evidence refresh

- full unit/Storybook/Playwright matrix;
- accessibility review;
- visual baseline review;
- live deployment verification;
- refreshed screenshots only after verified deployment.

## 17. Acceptance criteria

The redesign is complete only when all of the following are true:

1. `DESIGN.md` v3 is the documented source of truth and its semantic tokens map to implementation variables.
2. The selected accessible primitive layer is introduced without unrelated dependency churn.
3. ResolveOps domain components remain distinct from generic UI primitives.
4. The app shell, Triage, Evidence, Trace, and Evaluation views share one coherent visual rhythm.
5. Storybook functions as a categorized design-system catalog with meaningful states.
6. Unit tests, Storybook build, and the full Playwright suite pass.
7. Existing business semantics and seven-node workflow behavior remain unchanged.
8. WCAG 2.2 AA target rules remain satisfied for changed flows.
9. 390/768/1440 layouts have no page-level horizontal overflow.
10. Mobile decision/evidence/trace hierarchy remains correct.
11. Visual baselines change only after human review of intentional differences.
12. Public screenshots are refreshed only from a verified deployed revision.
13. No unsupported production-quality, policy-correctness, or semantic prompt-injection-immunity claims are introduced.

## 18. Success criterion from a portfolio perspective

A reviewer should be able to open the live demo and immediately read it as a deliberate operations product rather than a generic AI dashboard, while still seeing the engineering evidence that makes the project credible: grounding, retrieved cases, explicit human action, seven-step trace, deterministic evaluation, Storybook-backed components, responsive QA, and bounded limitations.
