# Frontend dependency security: compatible lockfile patch (2026-10-23)

This change updates only `frontend/package-lock.json`, within the project's existing
`frontend/package.json` dependency ranges. It does not migrate Tailwind, alter
customer-support runtime behavior, or modify deployment configuration.

## Reproduced audit evidence

| Category | Before (Slice E audit) | After compatible patch |
| --- | ---: | ---: |
| Critical | 1 | 0 |
| High | 8 | 5 |
| Moderate | 4 | 2 |
| Total | 13 | 7 |

- Baseline: GitHub Actions `39825503566` on the pre-patch lockfile.
- Rebuilt candidate and validation: GitHub Actions `39828401266` and `39828869873`.
- The candidate was generated with `npm update storybook @storybook/react-vite
  @storybook/addon-a11y vite vitest` followed by **non-forced**
  `npm audit fix --package-lock-only`, then `npm ci`.
- Verified lockfile versions: `storybook@10.6.3`,
  `@storybook/react-vite@10.6.3`, `@storybook/addon-a11y@10.6.3`,
  `vite@8.3.5`, `vitest@4.1.12`. **`tailwindcss@3.4.19` is unchanged.**
- The candidate passed frontend lint, unit tests, production build,
  `verify:button-css`, and Storybook build on GitHub Actions.
- No change to top-level `package.json` was needed.

## Seven unresolved advisories

The remaining npm audit graph contains `tailwindcss`, `braces`,
`chokidar`, `micromatch`, `fast-glob`, `postcss-nested`, and
`postcss-selector-parser` (five high and two moderate findings). npm suggests
a major Tailwind 4 upgrade to resolve these paths. That upgrade is **not**
approved as part of Slice E and is **not** included here.

These are primarily frontend build/watch-time transitive dependencies; this
is a *reachability consideration*, not a blanket assertion of safety.
Do not run the dev/build toolchain on untrusted source, inputs, or content
globs. Do not expose local development servers to untrusted networks.

Track next steps in [Issue #86](https://github.com/Praciller/customer-support-rag-triage-agent/issues/86):
investigate supportable Tailwind 3-compatible transitive patches or
explicitly scope a separate Tailwind migration. Do not suppress or relabel
the findings as resolved. No zero-vulnerability, production-quality, or
runtime-exploitability guarantee is made.

## Audit policy

The Slice E draft PR currently reports `npm audit` with
`continue-on-error: true` to retain UI test evidence. This does **not**
count as successful security remediation. Before approving the Slice E
release gate, require either a clean audit or a time-bounded exception
explicitly accepted by the repository owner, with this outstanding
advisory set and compensating controls documented.
