# Final Hardening Verification Review

Date: 2026-09-05  
Candidate commit: `6ecc3d1902a47d3851a426849ec06307372c1123`  
Review branch: `docs/final-hardening-verification`  
Live Hugging Face Space commit: `a2661562ff1a2a7b7f15e4b9145cb007c98444a5`  
Live URL: https://pracill-customer-support-rag-triage-agent.hf.space/

## Passed

- Backend: `ruff check src tests`, `ruff format --check src tests`, `pytest` (39 passed), adversarial retrieval evaluation (all checks passed), deterministic mock evaluation, and `pip check`.
- Frontend: `npm ci` (0 vulnerabilities), `npm audit` (0 vulnerabilities), lint, Vitest (11 files/34 tests passed), Vite production build, and Playwright browser suite (14 tests passed with the repository virtual environment).
- Live deployment: Hugging Face metadata reported the required commit, RUNNING runtime, READY domain; `/`, `/health`, `/ready`, and `/eval/results` returned 200; ingestion remained correctly forbidden (403); triage returned the expected delivery decision, grounded evidence, seven-node trace, mock provider, and no fallback/degraded state.
- Direct live visual evidence was inspected at desktop and mobile sizes with no console errors, page errors, failed requests, loading failures, overflow, or secret/private data observed.
- Public-copy review found no unsupported production, autonomy, policy-correctness, SLA, or semantic prompt-injection claims; matched language was explicitly bounded or negative.

## Failed

None.

## Flaky

None observed. The first local Storybook attempt was blocked by a stale ignored `storybook-static` output directory; after removing that generated directory, a fresh `npm run build-storybook` completed successfully without source or configuration changes.

## Limitations

- The fixture is small and deterministic; results are not a production SLA or production support-quality evidence.
- Banking77-derived labels are demo precedent, not company policy; deterministic grounding is not semantic entailment proof.
- The adversarial evaluation proves typed-field and workflow guard behavior, not universal semantic prompt-injection immunity.
- Free CPU deployment may cold-start; observed live latency is not an availability or performance guarantee.
- Main branch protection is disabled (GitHub returned `Branch not protected`).

## Acceptance criteria

- [x] AC1 — Review is based on the exact candidate SHA and isolated branch; no source, dependency, CI, deployment, or screenshot changes were made.
- [x] AC2 — Fresh backend, frontend, security, and browser verification is recorded with results and limitations.
- [x] AC3 — Live evidence was rechecked against the required Hugging Face SHA and public routes.
- [x] AC4 — Public recruiter-facing copy was scanned for unsupported claims; no unsupported matches were found.
- [x] AC5 — This report is the only new tracked artifact for Issue #29; no issues were merged or closed.

## Owner-gated follow-up

Optional repository-governance follow-up: enable branch protection/ruleset and require the stable backend, frontend, and browser checks if desired and if repository settings permit.

Issue state at review: #28 CLOSED; #29 OPEN; #14 OPEN; #10 OPEN.
