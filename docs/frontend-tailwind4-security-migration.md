# Frontend toolchain security remediation — Tailwind 4 migration

A scoped security migration is needed because the Tailwind 3 toolchain's
`braces@3.0.3` has a high-severity advisory without any published patched release.
There were **seven unresolved advisory entries** after the compatible
Storybook/Vite/Vitest lockfile fixes in PR #87.

## Scope of this migration

- Replace Tailwind 3.4.19 with Tailwind 4.3.3 and `@tailwindcss/postcss@4.3.3`.
- Move PostCSS integration to the first-party plugin, switch the stylesheet to
  `@import "tailwindcss";`, and use `@config "../../tailwind.config.js";`
  to preserve the v3 semantic token configuration.
- Update the CSS utility verification to recognize valid Tailwind 4 selectors;
  continue to require all buttons' CSS selectors and focus-visible styles.
- Keep React components, LangGraph/RAG, API, retrieval, tickets, and fixtures unchanged.
- Lock the exact dependency versions and enforce `npm audit --audit-level=low`
  in the normal CI frontend job.

## Verification

- Isolated build/audit spike: [GitHub Actions #39832518326](https://github.com/Praciller/customer-support-rag-triage-agent/actions/runs/39832518326),
  `npm ci`, `npm audit --audit-level=low`, lint, Vitest, production build,
  button CSS verification and Storybook all passed.
- At merge, require exact-head normal CI with Windows Playwright screenshots,
  backend Pytest, frontend and Docker image smoke. The **Windows screenshot
  baseline** is the visual compatibility test; no baseline updates or
  automatic screenshot re-approval are part of this security migration.
- This PR is a build-time tooling upgrade, not a Tailwind 4 UI redesign.

## Limitations

A clean npm audit is a point-in-time scan and does not prove the entire application
is vulnerability-free. Verify production artifacts and lockfile provenance before
release. Run the full tests again on the resulting merged `main` revision.
Do not deploy to Hugging Face automatically.
