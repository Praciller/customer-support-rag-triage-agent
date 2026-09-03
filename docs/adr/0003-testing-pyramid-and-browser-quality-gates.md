# ADR 0003: Use a Testing Pyramid with Browser Quality Gates

- Status: Accepted
- Date: 2026-09-03

## Context

The product combines a typed backend workflow with a responsive evidence-and-trace console. Backend regressions, component state regressions, accessibility failures, and browser-flow failures require different levels of feedback and evidence.

## Options considered

1. Rely on backend tests and manual browser review.
2. Use layered backend, component, component-catalog, browser, and selected visual checks.
3. Use only broad end-to-end coverage.

## Decision

Use option 2 as the testing pyramid:

- Vitest and Testing Library verify component and feature behavior.
- Storybook verifies isolated states, documentation, and accessibility.
- Playwright verifies deterministic end-to-end acceptance and selected visual regression.
- Browser selectors use semantic roles and labels; tests do not use arbitrary sleeps.
- CI reports tests, traces, and screenshots as review evidence when produced.
- Existing backend deterministic and adversarial evidence-boundary checks remain mandatory.

## Consequences

- Fast lower-level feedback catches most regressions before browser execution.
- Critical workflows receive real-browser and responsive evidence.
- CI artifacts become actionable review material rather than an opaque pass/fail signal.
- Browser and visual checks add maintenance cost and must remain deterministic and scoped to critical flows.
