# ResolveOps Design System v3

Date: 2026-09-05  
Status: Approved for implementation planning  
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

A fresh Playwright capture of the current live Hugging Face deployment at 1440, 768, and 390 pixels confirmed that the application is responsive and operationally correct, but also exposed five design-system problems that v3 must address:

1. the human decision does not dominate the triage page strongly enough;
2. runtime metadata competes visually with decision content;
3. Evaluation overuses equal-weight metric cards and therefore flattens meaning;
4. the seven-node trace is correct but too vertically expensive and repetitive;
5. tablet/mobile navigation becomes icon-heavy and loses product-language clarity.

This phase therefore changes the frontend foundation and information presentation, not the application product model.

## 3. Source guidance

The attached AI Coding Agent for SDLC material defines the frontend path as `UI Design -> Design System -> Component -> Page`, with the design system covering style guide, color palette, typography, spacing/layout, design tokens, and grid. It also treats `DESIGN.md` as machine-readable design context for coding agents and recommends Storybook as the live component catalog.

Current upstream shadcn/ui documentation confirms:

- Vite is supported for existing projects;
- React Aria is a first-class shadcn component base;
- React Aria can be selected with `--base aria`;
- the available visual styles include Mira, Nova, Lyra, Maia, Vega, Luma, Rhea, and Sera;
- shadcn recommends progressive component-by-component adoption rather than unsafe wholesale rewrites.

Typography research selected Geist for ResolveOps. The official Vercel Geist project describes Geist Sans as designed for legibility and simplicity, provides Geist Mono for text-based/code interfaces, and publishes both under SIL Open Font License 1.1. The Fontsource variable package supports self-hosting in Vite with no runtime CDN dependency.

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
        +-- Geist Sans / Geist Mono typography foundation
        |
        +-- shadcn/ui source components
        |       |
        |       +-- React Aria base
        |
        +-- ResolveOps domain components
        |
        +-- Triage / Evidence / Trace / Evaluation pages
```

The architecture has three product layers plus a shared typography foundation.

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
- Disclosure / expandable details;
- Skeleton;
- Dialog / Sheet only if a real flow requires them;
- ScrollArea only if existing page behavior benefits.

Do not add components solely because the registry offers them.

Do not make a generic `Card` abstraction the dominant layout primitive. The current UI already suffers from too many visually equivalent bordered boxes; v3 must express stronger surface hierarchy.

### 5.3 ResolveOps domain components

Keep domain meaning outside generic primitives. Target domain components include:

- WorkspaceHeader;
- SystemHealth;
- CustomerMessage / RequestComposer;
- DecisionWorkspace;
- RecommendedAction;
- SuggestedResponse;
- GroundingStatus;
- UrgencyStatus;
- EvidenceItem / EvidenceList;
- WorkflowTrace / CompactTraceStep;
- TechnicalDetails;
- EvaluationSummary;
- RetrievalQuality;
- WorkflowChecks;
- RuntimeProfile;
- ClassificationTable.

Domain components may use shadcn primitives internally, but their public API must express ResolveOps concepts rather than registry implementation details.

## 6. Typography — selected font system

### 6.1 Decision

Replace the current Inter-first UI stack with:

```text
UI / headings / labels / body:
Geist Sans / Geist Variable

Technical identifiers / metrics / trace metadata:
Geist Mono

Fallbacks:
Geist Variable, Geist, ui-sans-serif, system-ui, -apple-system,
BlinkMacSystemFont, "Segoe UI", sans-serif

Mono fallbacks:
Geist Mono, ui-monospace, SFMono-Regular, Consolas, monospace
```

Use the variable package where practical and self-host it through the application bundle. Preferred implementation path:

```text
@fontsource-variable/geist
```

For Geist Mono, use an official/self-hosted package path verified at implementation time; do not load fonts from a runtime third-party CDN.

### 6.2 Why Geist

Geist is selected because it better matches the intended product character than the current Inter stack:

- contemporary technical/SaaS character without becoming decorative;
- strong readability for compact product UI;
- clean numerals and labels for evidence-heavy screens;
- a matching mono family for trace/runtime data;
- variable weights allow hierarchy without shipping many unrelated font files;
- open-source OFL 1.1 licensing supports repository and deployed-app use;
- high current ecosystem adoption makes it a lower-risk portfolio choice than a niche display face.

This is a deliberate product choice, not a temporary experiment.

### 6.3 Type roles

Use these roles as the starting contract for `DESIGN.md` v3:

```text
page-title:          26px / 32px, 600
section-title:       18px / 24px, 600
primary-decision:    22px / 28px, 600
body:                15px / 22px, 400
body-strong:         15px / 22px, 550-600
control:             14px / 20px, 500
metadata:            13px / 18px, 400-500
technical:           12-13px / 18px, 450-500, Geist Mono
eyebrow:             11px / 16px, 600, limited uppercase use
```

Consequential decision/action text must not be smaller than 14px.

Avoid excessive uppercase labels and excessive letter spacing. Uppercase eyebrows are reserved for a small number of structural labels, not every panel.

Use `font-variant-numeric: tabular-nums` for metrics, latency, scores, and aligned technical values where it improves scanning.

## 7. Visual direction

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
- Do not use a tiny uppercase eyebrow as a substitute for meaningful hierarchy.

## 8. Surface hierarchy

The current app makes too many unrelated blocks look like the same white bordered panel. v3 must define distinct surface roles:

1. **Canvas** — global application background.
2. **Workspace** — page-level working area; usually not boxed.
3. **Primary decision surface** — strongest visual surface on Triage.
4. **Standard section surface** — groups evidence or evaluation content.
5. **Subtle item surface** — individual evidence/trace rows; lower contrast than primary surfaces.
6. **Technical metadata surface** — weakest surface, visually subordinate.

Do not wrap every metric, label, or metadata group in an equal-weight card.

## 9. Layout system

### Desktop

Adopt a stable application shell with compact navigation and one main workspace.

Suggested structure:

```text
+----------------------------------------------------------------+
| ResolveOps                         API Ready         Utilities   |
+---------------+------------------------------------------------+
| Triage        | WorkspaceHeader                                |
| Evaluation    |                                                |
| Trace         | Customer request                               |
|               |                                                |
| Overview      | Recommended action / human decision            |
| Search        | Grounding / escalation                         |
| Dataset       |                                                |
| Providers     | Evidence                                       |
|               |                                                |
|               | Workflow trace / technical details             |
+---------------+------------------------------------------------+
```

Navigation must not overpower the work surface.

Separate navigation into two conceptual groups:

**Primary work:**

- Triage;
- Evaluation;
- Trace.

**Secondary tools:**

- Overview;
- Semantic search;
- Dataset;
- Provider status.

The exact visual group labels may be subtle, but the hierarchy must be perceivable.

### Tablet and mobile

At 390px, maintain the mandatory content order:

`decision -> grounding/escalation -> evidence -> trace`.

Do not collapse all navigation to unlabeled icons.

Preferred mobile navigation pattern:

```text
ResolveOps                  API Ready
Triage | Eval | Trace | More
```

`More` may open an accessible sheet/menu containing secondary tools. If a sheet is used, React Aria focus management and keyboard behavior are required.

At 768px, labels may be shortened but primary destinations must remain understandable without guessing icon meaning.

No page-level horizontal overflow at 390, 768, or 1440.

## 10. Triage information architecture

The current Decision panel contains correct information but mixes human decision content with provider/cache/runtime detail. v3 must separate these concerns.

Required order:

```text
Customer request

Recommended action
Suggested response
Grounding / urgency / escalation

Evidence

Workflow trace
Technical details
```

The `DecisionWorkspace` is the strongest visual area after the customer request.

Keep immediately visible:

- next human action;
- suggested response;
- grounding status/score;
- urgency;
- escalation/manual-review state when applicable.

Move to `TechnicalDetails` or trace context:

- normalized message;
- provider/model;
- cache hit;
- raw latency details;
- other implementation metadata that is not required for the support decision.

The goal is not to hide engineering evidence; it is to place it at the correct level of hierarchy.

## 11. Evidence presentation

Evidence remains a first-class product differentiator.

Each evidence item must make these easy to scan:

- reference/case identity;
- relevance/similarity;
- provenance/source;
- useful excerpt/content;
- any bounded caveat needed to avoid treating evidence as policy.

Evidence items should be visually lighter than the primary decision surface and should not all look like independent dashboard cards.

Retrieved evidence remains untrusted evidence, never workflow authority or support policy.

## 12. Workflow trace presentation

The current seven-node trace is semantically correct but too tall and repeats runtime badges.

Desktop/tablet target: compact technical timeline/table hybrid capable of showing most or all seven stages in one viewport.

Conceptual form:

```text
✓ 1 Normalize message       Local                       0.03 ms
│
✓ 2 Classify intent         delivery_issue · 0.91       0.67 ms
│                           Mock · cache
│
✓ 3 Detect urgency          medium                      0.48 ms
│
✓ 4 Retrieve cases          3 cases · Qdrant          152.08 ms
│
✓ 5 Generate response       220 chars                   2.26 ms
│
✓ 6 Grounding check         0.86 grounded               0.58 ms
│
✓ 7 Suggest next action     ask_for_order_id            0.01 ms
```

The exact values remain runtime-driven; the example above is layout guidance only.

Repeated provider/cache metadata should use a disclosure or shared technical context rather than seven identical badges.

Mobile may remain stacked, but must reduce badge repetition and preserve readability.

## 13. Evaluation redesign

Evaluation is the strongest candidate for structural redesign.

Do not render every metric as an equal-weight card. Replace the current metric-card grid with semantic groups:

### Retrieval quality

- Precision@K;
- Recall@K;
- MRR;
- nDCG@K.

### Workflow checks

- intent accuracy/F1;
- urgency accuracy/F1;
- grounding fixture result;
- workflow completion/success.

### Runtime profile

- median/P95 latency where available;
- provider mode;
- external-call/fallback context;
- cache context where useful.

### Classification detail

Use a compact table/list for per-class metrics instead of promoting each row to a card.

### Methodology and limitations

Keep the deterministic-fixture limitation visible and easy to discover.

Charts must add information rather than repeat adjacent metrics. Prefer direct labels and compact horizontal profiles over decorative bars. If a chart is redundant, remove it.

Every chart still requires a textual summary.

## 14. Token strategy

`DESIGN.md` v3 will retain semantic token names rather than expose registry-specific color names.

Expected roles include:

- canvas;
- surface;
- surface-muted;
- surface-strong;
- technical-surface;
- foreground;
- foreground-muted;
- foreground-subtle;
- border;
- border-strong;
- primary;
- primary-foreground;
- success;
- warning;
- danger;
- focus;
- selected;
- disabled.

Typography token roles must reference Geist Sans/Variable and Geist Mono rather than Inter.

Spacing should remain on a small deliberate scale. Add density roles for compact controls and technical rows rather than creating arbitrary one-off padding values.

Registry-generated CSS variables must be mapped to ResolveOps semantic roles. Generated theme values are not accepted as product decisions by default.

## 15. Tailwind migration policy

The project currently has Tailwind 3.x in devDependencies. Current shadcn examples use the modern toolchain, but the redesign must not mix a broad dependency upgrade with visual migration without evidence.

Implementation must begin with a compatibility spike on an isolated branch/worktree to determine the least risky path:

1. verify whether the selected React Aria shadcn components can be introduced cleanly in the existing Vite project;
2. determine whether Tailwind 3 can be retained temporarily or whether a controlled Tailwind 4 migration is necessary;
3. verify the self-hosted Geist package path with the current Vite build;
4. if Tailwind 4 is required, perform it as its own reviewable slice with app behavior unchanged;
5. do not combine unrelated package upgrades.

No `npm audit fix --force` and no dependency churn unrelated to design-system adoption.

## 16. Component migration strategy

Migrate progressively and keep the app runnable after every slice.

Suggested sequence:

1. compatibility spike;
2. Geist typography + foundation/tokens and utility setup;
3. Button and Field/Input;
4. Badge/Status/Alert states;
5. surface composition;
6. app shell/navigation;
7. Triage decision and message hierarchy;
8. Evidence components;
9. Workflow trace;
10. Evaluation grouped layout;
11. final responsive/a11y polish.

Existing component APIs should be preserved where cheap. If an API change is necessary, update consumers in the same bounded slice and keep tests green.

## 17. Storybook contract

Storybook becomes the design-system catalog, not merely a component preview.

Required Storybook groups:

- Foundations / Typography;
- Foundations / Color and surfaces;
- Foundations / Spacing and density;
- Primitives;
- Status and feedback;
- Domain / Triage;
- Domain / Evidence;
- Domain / Trace;
- Domain / Evaluation.

Typography stories must visibly demonstrate:

- page title;
- section title;
- primary decision;
- body;
- control;
- metadata;
- Geist Mono technical text;
- numeric/tabular styles.

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

## 18. Testing and QA

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

### Screenshot identity contract

The baseline audit found a capture defect: files named as Overview screenshots were actually captured from Ticket triage. Future capture scripts must assert page identity before saving a screenshot.

At minimum, each named capture must verify:

- expected current navigation item;
- expected page heading;
- expected route/state identifier where available.

A mismatched page name is a capture failure, not an acceptable screenshot.

### Visual review

Every major migration slice must be inspected at 1440 desktop and 390 mobile. The goal is visual improvement plus semantic preservation, not merely snapshot acceptance.

## 19. Accessibility

Target WCAG 2.2 AA remains unchanged.

Required:

- keyboard operability;
- visible focus;
- semantic labels and landmarks;
- status meaning not carried by color alone;
- reduced-motion handling;
- chart text summary;
- correct focus management for any dialog/sheet/navigation overlay;
- sufficient contrast after token changes;
- navigation remains understandable when labels are shortened;
- technical mono text never becomes the sole carrier of critical user action.

React Aria primitives are an implementation aid, not proof of accessibility by themselves.

## 20. Impeccable usage

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

## 21. Non-goals

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
- analytics/product feature expansion;
- runtime web-font CDN dependency;
- changing the product to a generic shadcn visual identity.

## 22. Rollout plan

Implementation should be decomposed into small PRs rather than one large redesign PR.

### Slice A — Foundation compatibility spike

- verify shadcn + React Aria integration on current Vite app;
- resolve Tailwind compatibility decision;
- verify self-hosted Geist package path/build behavior;
- no user-visible redesign required.

### Slice B — Design foundation

- `DESIGN.md` v3;
- Geist Sans/Variable + Geist Mono typography foundation;
- semantic CSS variables/tokens;
- surface/density roles;
- base primitive setup;
- Storybook foundation stories.

### Slice C — Shell + navigation

- application shell;
- primary/secondary navigation hierarchy;
- mobile labeled navigation + accessible More surface;
- current page routing behavior preserved.

### Slice D — Triage workspace

- customer request;
- primary DecisionWorkspace;
- grounding/escalation;
- evidence composition;
- technical metadata moved to subordinate context.

### Slice E — Trace + Evaluation

- compact seven-node trace;
- runtime metadata disclosure/subordination;
- grouped Evaluation layout;
- redundant chart/card reduction.

### Slice F — QA and evidence refresh

- full unit/Storybook/Playwright matrix;
- accessibility review;
- visual baseline review;
- live deployment verification;
- corrected page-identity screenshot capture;
- refreshed screenshots only after verified deployment.

## 23. Acceptance criteria

The redesign is complete only when all of the following are true:

1. `DESIGN.md` v3 is the documented source of truth and its semantic tokens map to implementation variables.
2. Geist Sans/Variable is the default UI typeface and Geist Mono is used for technical/runtime roles through self-hosted bundled assets, not a runtime external CDN.
3. The selected accessible primitive layer is introduced without unrelated dependency churn.
4. ResolveOps domain components remain distinct from generic UI primitives.
5. DecisionWorkspace is visually stronger than runtime metadata and evidence detail.
6. Runtime/provider/cache/latency information is subordinate to the support decision rather than competing with it.
7. Evaluation is organized into semantic groups instead of an equal-weight metric-card wall.
8. The seven-node trace is compact enough to scan efficiently while preserving all seven ordered stages and runtime evidence.
9. Primary/secondary navigation is understandable at desktop, tablet, and mobile sizes; mobile does not rely on unlabeled icons alone.
10. The app shell, Triage, Evidence, Trace, and Evaluation views share one coherent visual rhythm.
11. Storybook functions as a categorized design-system catalog with meaningful states and typography/foundation stories.
12. Unit tests, Storybook build, and the full Playwright suite pass.
13. Existing business semantics and seven-node workflow behavior remain unchanged.
14. WCAG 2.2 AA target rules remain satisfied for changed flows.
15. 390/768/1440 layouts have no page-level horizontal overflow.
16. Mobile decision/evidence/trace hierarchy remains correct.
17. Visual baselines change only after human review of intentional differences.
18. Public screenshots are refreshed only from a verified deployed revision and the capture script asserts page identity before naming each screenshot.
19. No unsupported production-quality, policy-correctness, or semantic prompt-injection-immunity claims are introduced.
20. No new runtime external font/CDN dependency is introduced.

## 24. Success criterion from a portfolio perspective

A reviewer should be able to open the live demo and immediately read it as a deliberate operations product rather than a generic AI dashboard, while still seeing the engineering evidence that makes the project credible: a clear human decision, grounding, retrieved cases, explicit escalation boundaries, seven-step trace, deterministic evaluation, Storybook-backed components, responsive QA, and bounded limitations.

Typography should contribute to that impression rather than look like a default starter stack: Geist Sans provides the product voice, and Geist Mono visually separates technical evidence without making the interface feel like a terminal.
