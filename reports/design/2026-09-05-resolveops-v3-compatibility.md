# ResolveOps v3 compatibility decision

## Baseline

- GitHub `main`: `8577bcf81a97bd2f4c6360170bc07cc83a9adeb0`
- Node: `v22.23.2`
- npm: `10.9.8`
- React / React DOM: `19.2.7 / 19.2.7`
- Vite: `8.0.16`
- Tailwind CSS: `3.4.19`
- TypeScript: `5.7.3`
- PostCSS / Autoprefixer: `8.5.28 / 10.5.0`
- shadcn CLI: `4.21.0`
- Baseline gates: `npm ci` PASS, `npm audit` PASS with 0 vulnerabilities, lint PASS, 34/34 unit tests PASS, build PASS.

## Geist self-hosting

- `@fontsource-variable/geist`: `5.3.0`
- `@fontsource-variable/geist-mono`: `5.3.0`
- Vite build: PASS.
- Local font assets: YES; multiple `.woff2` assets were emitted.
- Runtime external font CDN: NO; no `fonts.googleapis.com` or `fonts.gstatic.com` references were found in `dist`.
- Build note: the probe added 12 local font assets and increased transformed modules from 2,155 to 2,157. The emitted application JS remained 216.63 kB before gzip; the font assets were emitted separately.

## Tailwind 3 + shadcn React Aria

- Classification: `SUPPORTED_WITH_CHURN`
- `--base aria` recognized: YES.
- Tailwind 3 validation: PASS.
- React Aria init: PARTIAL. The CLI validated Vite, Tailwind CSS, and an added probe alias, then wrote `components.json` with `style: aria-nova` and React Aria-oriented aliases.
- Button primitive generated: NO. `add button` could not load the disposable workspace config, and the existing Button remained a native HTML wrapper; React Aria Button integration is therefore not verified.
- Tailwind 3 probe lint: PASS.
- Tailwind 3 probe unit: 34/34 PASS.
- Tailwind 3 probe build: PASS.
- Forced/config changes observed: `components.json` was added; the probe needed an explicit `@/*` TypeScript/Vite alias for CLI validation. No Tailwind 4 plugin, PostCSS rewrite, CSS `@import "tailwindcss"`, or production dependency change was accepted.
- The CLI did not overwrite ResolveOps semantic tokens in the successful init attempt.

## Tailwind 4 probe

- Required: NO.
- Result: `NOT_REQUIRED`.
- Tailwind 3 was accepted by the current CLI, so a Tailwind 4 migration would add scope without evidence that it is required for this compatibility question.

## Decision

- Tailwind path: `KEEP_3`
- React Aria base: `BLOCKED`
- Geist typography: `ADOPT`

The current Vite/Tailwind 3 stack builds cleanly, and the CLI recognizes the React Aria base without forcing a Tailwind 4 migration. However, the current CLI could not complete the representative Button add in the disposable workspace, so React Aria adoption is not yet proven. Geist self-hosting is directly proven through local WOFF2 emission and absence of runtime font CDN references. Slice B should resolve the CLI workspace-config/alias issue in a disposable reproduction before any permanent primitive changes.

## Guardrails for Slice B

- Keep production Tailwind 3 until a separate migration is justified by a reproducible requirement.
- Resolve and independently verify the shadcn workspace-config and alias behavior before adopting React Aria components.
- Use `--base aria` explicitly; do not substitute Radix or Base UI.
- Add Geist Sans and Geist Mono only through self-hosted `@fontsource-variable` imports; do not add Google Fonts or another runtime CDN.
- Preserve ResolveOps-owned semantic tokens and domain components; do not copy generated `aria-nova` theme defaults wholesale.
- Introduce one primitive at a time, beginning with Button, and run lint, unit, build, Storybook, and browser gates before broader migration.
- Keep the compatibility work separate from production UI redesign and document any resolved CLI workaround before committing it.

## Limitations

- The probe used a disposable copy and did not prove a permanent production integration.
- React Aria Button generation remains unverified because the CLI could not load the disposable workspace config during `add button`.
- The font bundle observation is a compatibility result, not a final performance budget.
- Deterministic local gates do not establish cross-platform browser or production deployment behavior.
