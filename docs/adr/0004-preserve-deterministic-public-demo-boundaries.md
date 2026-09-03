# ADR 0004: Preserve Deterministic Public Demo Boundaries

- Status: Accepted
- Date: 2026-09-03

## Context

The public demo is intended to be reviewable and reproducible without requiring an external AI credential. Its retrieved support cases are bounded Banking77-derived precedent, and its workflow already exposes grounding, degraded generation, citation integrity, and human-review states.

## Options considered

1. Make the public path depend on an external GenAI provider for a more realistic demo.
2. Preserve a zero-key deterministic public/demo path and keep external GenAI optional behind the server-side boundary.
3. Present retrieved examples as policy authority and hide degraded or invalid-citation states for a simpler user experience.

## Decision

Use option 2. The default public/demo path requires no external credential. Retrieved examples remain precedent/evidence, not policy authority. Degraded generation or invalid citation paths cannot look grounded. Semantic LLM prompt-injection immunity is not established by deterministic tests. External GenAI remains optional and server-side.

## Consequences

- Reviewers can reproduce the public workflow without keys or paid infrastructure.
- Evidence, grounding, escalation, and human-review limits remain visible.
- Deterministic results are appropriate for regression evidence, not claims of universal model safety or policy correctness.
- A future provider or policy change must preserve these boundaries or supersede this ADR with explicit review.
