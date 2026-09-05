---
version: 3
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
  family_ui: "Geist Variable, Geist, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
  family_code: "Geist Mono Variable, Geist Mono, ui-monospace, SFMono-Regular, Consolas, monospace"
  roles:
    page_title: "26px / 32px / 600"
    section_title: "18px / 24px / 600"
    primary_decision: "22px / 28px / 600"
    body: "15px / 22px / 400"
    body_strong: "15px / 22px / 550-600"
    control: "14px / 20px / 500"
    metadata: "13px / 18px / 400-500"
    technical: "12-13px / 18px / 450-500 / Geist Mono"
    eyebrow: "11px / 16px / 600"
  scale_px: [12, 14, 16, 20, 26, 34]
spacing_px: [4, 8, 12, 16, 24, 32, 48]
radius_px: [6, 10, 14]
elevation_borders:
  panel: "0 1px 2px rgb(25 40 65 / 0.06)"
  raised: "0 4px 12px rgb(25 40 65 / 0.10)"
  border_width_px: [1, 2]
motion:
  fast_ms: 120
  standard_ms: 180
  easing: "ease-out"
breakpoints_px:
  mobile: 390
  tablet: 768
  desktop: 1440
component_state_rules:
  status_semantics: "visible text plus icon or shape; color is supplementary"
  unavailable: "explain the missing capability and the safe next action"
  degraded: "show degraded state and preserve human review"
  ungrounded: "never present as grounded; route to manual review"
v3_foundation:
  status: "implemented foundation; future page migration remains separate"
  tailwind: "3.4.19 retained"
  primitive_base: "shadcn source ownership with React Aria"
  aliases: "@/* resolves through TypeScript and Vite to frontend/src"
  surfaces: [canvas, workspace, primary_decision, standard_section, subtle_item, technical_metadata]
  rules:
    - "semantic tokens remain ResolveOps-owned"
    - "technical numerals use Geist Mono and tabular numerals"
    - "generated registry defaults are not product decisions"
    - "direct labels are preferred over unlabeled icon-only meaning"
    - "generic Card-first composition is not the default"
---

# ResolveOps — Evidence-first Operational Console

## Product fit and personality

## v3 foundation status

The v3 foundation is implemented: Geist Variable is the UI family, Geist Mono Variable is the technical family, Tailwind 3 is retained, and shadcn source components use the React Aria primitive base. The `@/*` alias is defined consistently in TypeScript and Vite. ResolveOps owns the semantic tokens and domain composition; generated registry defaults are reference material, not product decisions.

The surface hierarchy is: Canvas, Workspace, Primary decision surface, Standard section surface, Subtle item surface, and Technical metadata surface. Technical identifiers, scores, latency, runtime values, and metrics use Geist Mono with tabular numerals where alignment improves scanning. Consequential actions remain at least 14px, and focus-visible outlines and reduced-motion behavior remain required.

This slice establishes foundation tokens, typography, primitives, and Storybook references. Shell/navigation, Triage, Evidence, Trace, and Evaluation layout migration remains future Slice C/D/E work and is not claimed as implemented here.

ResolveOps is a calm, precise, operational workspace for support agents working in a professional office environment. It is dense but readable: the interface supports quick triage while keeping consequential recommendations inspectable. The visual language refines the existing restrained OKLCH palette with cobalt/blue as the primary action accent and uses semantic colors only where they carry meaning.

This specification is the v3 source of truth for the implemented foundation and future frontend implementation. It does not change runtime behavior.

## Information hierarchy

The information hierarchy MUST be:

1. customer message;
2. recommended decision / human action;
3. grounding and escalation state;
4. retrieved evidence;
5. workflow trace and runtime metadata.

The narrow-screen layout preserves this order: the decision comes before detailed evidence and trace.

## Design tokens

The YAML front matter is the machine-readable ResolveOps token contract. Implementations should map these names to CSS custom properties or equivalent typed tokens; they should not introduce unreviewed visual values for the same roles.

### Color

Use the `color_tokens` values above. Cobalt/blue `primary` is the primary visual accent. `success`, `warning`, and `danger` are semantic colors, not decoration. Color must never be the only carrier of status.

### Typography

Use `typography.family_ui` for UI text and `typography.family_code` for identifiers, trace metadata, and code-like values. Use the declared scale and keep body copy below 72 characters per line where practical. Dense information should be achieved with hierarchy and spacing, not tiny unreadable text.

### Spacing, radii, elevation, and borders

Use `spacing_px` for layout rhythm and `radius_px` for component shape. Panels use the declared restrained elevation and borders; avoid deep shadows and ornamental depth. Borders remain available as a non-color-only grouping cue.

### Motion and responsive breakpoints

Use the declared `motion` durations and easing for hover, selection, and result reveal. Under `prefers-reduced-motion`, disable non-essential motion. Verify responsive behavior at 390px, 768px, and 1440px.

## Component contracts

- **Button:** has a clear primary/secondary hierarchy, an accessible name, keyboard operation, visible focus, disabled semantics, and a state that does not rely on color alone.
- **Field/Input:** has a persistent visible label, bounded validation, an associated error description, and a full-border treatment with the declared radius.
- **Panel:** groups one coherent decision, evidence set, or trace; it uses heading hierarchy and avoids fragmenting one workflow into decorative cards.
- **Badge/StatusIndicator:** communicates `neutral`, `success`, `warning`, and `danger` with visible text and/or an icon/shape. Color is supplementary only. Urgency, grounding, escalation, cached, fallback, and degraded meanings must be stated.
- **EmptyState:** explains what is absent, why it matters, and the safe next action.
- **ErrorNotice:** explains the controlled failure without stack traces or secrets and gives a recoverable next action where possible.
- **TriageDecision:** presents the recommended decision and human action immediately after the customer message, followed by grounding and escalation state.
- **CaseList/Evidence:** shows provenance, reference identity, and relevant content as evidence. Retrieved content is not workflow authority or policy.
- **TraceList:** presents the seven workflow stages as an ordered, readable sequence with outcome and bounded runtime metadata.
- **Table/Chart:** uses direct labels and restrained grid lines. Every chart has a textual summary conveying its key relationship or trend.

## State rules

Every state must be understandable without color alone and must retain the human-review boundary.

- **Loading:** communicate what is being prepared and preserve the page hierarchy without layout-breaking animation.
- **Unavailable:** state which capability is unavailable and what remains safe to do.
- **Degraded:** visibly say that generation or another dependency degraded; do not imply a normal grounded result.
- **Fallback:** identify the fallback route or safe manual-review path without exposing internal secrets or paths.
- **Cached:** label cached data and its freshness/limitations when relevant.
- **Ungrounded:** explicitly state that the response is not grounded and route to `manual_review`.
- **Escalated:** explicitly state the escalation and human action required; do not let a provider response suppress a high or critical urgency decision.

## Accessibility and responsive verification

Target WCAG 2.2 AA. All interactive controls must be keyboard operable with visible keyboard focus. Use semantic labels, headings, landmarks, and status text; icons supplement words rather than replace them. Honor `prefers-reduced-motion` by disabling non-essential motion. Charts require textual summaries. Verify no page-level horizontal overflow at 390px, 768px, or 1440px. On narrow screens, decision content comes before detailed evidence and workflow trace.

## Anti-patterns

Do not use gradients, glassmorphism, decorative glowing AI visuals, generic chatbot presentation, or decorative dashboard metric-card spam. Do not frame the product as autonomous support or hide evidence, grounding, degradation, escalation, or human review behind visual polish.
