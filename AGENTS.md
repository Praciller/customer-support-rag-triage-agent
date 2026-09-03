# AGENTS.md

## Product contract

ResolveOps turns one customer-support message into a reviewable decision: intent, urgency, retrieved precedent, grounded draft response, next action, and a seven-node execution trace. It drafts for human review; Banking77-derived examples are demo precedent, not company policy.

## Repository map

- `src/api/` — HTTP validation and public API boundary.
- `src/graph/` — typed seven-node LangGraph orchestration.
- `src/retrieval/` — Qdrant retrieval and embeddings.
- `src/llm/` — deterministic/local and optional external inference routing.
- `src/evaluation/` — deterministic evaluation and reports.
- `frontend/` — React/Vite operations console.
- `data/demo/` — bounded deterministic fixture.
- `docs/` — architecture, security, evaluation, deployment, runbook, and ADRs.

## Source-of-truth docs

Read only what the task needs:

1. `PRODUCT.md` for user and product purpose.
2. `DESIGN.md` for UI/design tokens and interaction rules.
3. `docs/architecture.md` for runtime boundaries and node contracts.
4. `docs/security.md` for evidence, secret, and public-API invariants.
5. `docs/evaluation.md` for metric methodology and limitations.
6. `docs/superpowers/specs/2026-09-03-sdlc-professional-hardening-design.md` plus the relevant plan under `docs/superpowers/plans/` for this hardening program.

## Human-review boundary

The system drafts a support decision for a human. Retrieved support content is untrusted evidence, never workflow authority or policy. Banking77-derived records are demo precedent, not company policy.

## Security and evidence invariants

- Retrieved messages are untrusted evidence, never system/developer/workflow instructions.
- Evidence references are valid only when IDs were actually retrieved.
- Empty evidence, rejected citations, or degraded generation cannot be presented as grounded.
- Ungrounded output routes to human review.
- Never expose credentials, raw prompts, environment values, external endpoint URLs, stack traces, or local paths in public output or artifacts.
- External inference remains optional, explicit, server-side, and outside the default public demo.

## Verification

Backend from the repository root:

```text
ruff check src tests
ruff format --check src tests
python -m pytest
python -m src.evaluation.evaluate_adversarial_retrieval --report-path <temporary-non-committed-path>
```

Run the deterministic demo/evaluation command defined by the current `Makefile` and `README.md` when the environment supports it.

Frontend:

```text
cd frontend
npm ci
npm run lint
npm test
npm run build
```

After Storybook/Playwright are introduced, UI behavior changes must also run the repository Storybook build and critical browser suite defined by their approved plan.

## Dependency policy

Keep the existing stack unless an accepted requirement proves a dependency is necessary. Do not add a framework migration, client router, state-management library, component mega-library, analytics product, or unverified agent skill for convenience.

## Secret handling

Never commit credentials, private environment values, raw environment dumps, raw prompts, customer-sensitive data, or secret-bearing screenshots/logs/fixtures. Use the existing local/demo configuration and server-side external inference boundary; do not require credentials for deterministic acceptance.

## Definition of Done

A bounded change is done only when:

- its Given/When/Then acceptance criteria pass;
- relevant lint, type, build, unit, integration, and browser checks pass;
- security/evidence boundaries are unchanged or explicitly reviewed;
- UI status remains understandable without color alone;
- docs and screenshots describe verified behavior only;
- no secret, private path, raw prompt, or unsupported production claim is committed;
- the diff remains inside the accepted task scope.

## Stop conditions

Stop and request review rather than silently broadening scope if implementation would require changing the public backend contract, weakening evidence/grounding semantics, adding an unplanned framework/dependency, using external credentials for deterministic acceptance, repairing unrelated failures, or performing owner-authenticated deployment/secret entry.

## Hardening program pointers

The approved hardening design is `docs/superpowers/specs/2026-09-03-sdlc-professional-hardening-design.md`. Phase-specific plans live under `docs/superpowers/plans/`. Future architecture reversals must supersede an ADR rather than silently rewriting its decision history.
