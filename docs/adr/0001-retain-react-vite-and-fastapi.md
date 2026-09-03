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
