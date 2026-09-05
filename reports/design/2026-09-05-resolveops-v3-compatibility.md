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
- React Aria init: PASS after the expected alias contract was added in the disposable probe. The CLI validated Vite, Tailwind CSS, and import aliases, then wrote `components.json` with `style: aria-nova`.
- Button primitive generated: YES at the disposable-only `src/components/aria-ui/button.tsx` target. The initial attempt exposed the Windows case-insensitive collision between the existing `src/components/ui/Button.tsx` and generated `button.tsx`; the probe restored the existing wrapper and used the separate `aria-ui` target before retrying.
- React Aria source: VERIFIED. The generated Button imports `Button`/`Link` primitives and prop types from `react-aria-components`.
- React Aria dependency evidence: `react-aria-components@1.21.1`, `class-variance-authority@0.7.1`, and `cn@0.2.5` were installed in the disposable probe.
- Tailwind 3 probe lint: PASS.
- Tailwind 3 probe unit: 35/35 PASS, including a focused React Aria Button test covering accessible rendering, activation, disabled behavior, and the `outline` variant.
- Tailwind 3 probe build: PASS against the preserved ResolveOps CSS entry. The unmodified shadcn-generated CSS entry failed because it added `@apply border-border` without corresponding existing Tailwind 3 theme tokens; this is generated-theme churn, not a Tailwind 4 requirement.
- Forced/config changes observed: `components.json`, root and app `@/*` TypeScript paths, and Vite `resolve.alias` were required in the disposable probe. The init command also added `src/lib/utils.ts` and attempted to rewrite the CSS entry. No Tailwind 4 plugin or production dependency/config change was accepted.

## Tailwind 4 probe

- Required: NO.
- Result: `NOT_REQUIRED`.
- Tailwind 3 was accepted by the current CLI, so a Tailwind 4 migration would add scope without evidence that it is required for this compatibility question.

## Decision

- Tailwind path: `KEEP_3`
- React Aria base: `ADOPT`
- Geist typography: `ADOPT`

The current Vite/Tailwind 3 stack builds cleanly, and the CLI recognizes `--base aria`. With the explicit TypeScript/Vite alias contract and a separate disposable `aria-ui` target, the CLI generated a React Aria Button, the focused test passed, and the preserved ResolveOps CSS entry built successfully. Tailwind 3 remains the least-change path; the generated CSS theme requires deliberate token mapping in Slice B. Geist self-hosting is directly proven through local WOFF2 emission and absence of runtime font CDN references.

## Guardrails for Slice B

- Keep production Tailwind 3 until a separate migration is justified by a reproducible requirement.
- Add matching `@/*` paths to root/app TypeScript configuration and `@` runtime resolution in Vite before running shadcn in the production project.
- Use `--base aria` explicitly; do not substitute Radix or Base UI.
- Treat generated shadcn theme utilities and CSS as inputs to map onto ResolveOps tokens, not as an automatic replacement for the existing token system.
- Add Geist Sans and Geist Mono only through self-hosted `@fontsource-variable` imports; do not add Google Fonts or another runtime CDN.
- Preserve ResolveOps-owned semantic tokens and domain components; do not copy generated `aria-nova` theme defaults wholesale.
- Introduce one primitive at a time, beginning with Button, and run lint, unit, build, Storybook, and browser gates before broader migration.
- Resolve the existing `src/components/ui/Button.tsx` versus generated lowercase `button.tsx` naming collision deliberately on Windows; never overwrite it accidentally.
- Keep the compatibility work separate from production UI redesign and document any resolved CLI workaround before committing it.

## Limitations

- The probe used a disposable copy and did not prove a permanent production integration.
- The React Aria Button was verified only in a disposable probe; permanent production adoption remains Slice B work.
- The generated CSS entry requires token/config mapping for this existing Tailwind 3 project; blindly retaining it fails on `border-border`.
- The font bundle observation is a compatibility result, not a final performance budget.
- Deterministic local gates do not establish cross-platform browser or production deployment behavior.
