# ADR 0002: Treat the Design System as a Versioned Contract

- Status: Accepted
- Date: 2026-09-03

## Context

The product needs a consistent, accessible operational console while its frontend is decomposed into smaller feature and component boundaries. The existing `DESIGN.md` captures useful visual intent and values but is not yet a complete contract for implementation.

## Options considered

1. Keep design guidance informal and let each component choose its own values.
2. Make `DESIGN.md` a versioned source of truth for tokens, hierarchy, responsive behavior, accessibility, motion, and component states.
3. Adopt a component library as the primary design authority.

## Decision

Use option 2. `DESIGN.md` is the versioned source-of-truth design contract consumed by implementation. CSS and components consume its token and state rules rather than inventing new hard-coded visual values. A materially different design direction must update the versioned contract through review.

## Consequences

- Design decisions are discoverable by agents and reviewers before implementation.
- Token and state changes are reviewable independently from CSS changes.
- The existing restrained ResolveOps aesthetic remains coherent across future features.
- The contract requires implementation and accessibility checks to stay synchronized with its version.
