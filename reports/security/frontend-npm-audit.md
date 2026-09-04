# Frontend npm audit triage

Baseline captured after `npm ci` on the frontend. The five high findings were development/build-tool dependencies; `npm audit --omit=dev` reported zero vulnerabilities, so they are not in the production Vite dependency graph.

| Package | Severity | Advisory IDs | Dependency path | Exposure | Disposition |
| --- | --- | --- | --- | --- | --- |
| brace-expansion | high | 1123897, 1123898, 1130588, 1130591, 1130734, 1130737 | ESLint/minimatch; TypeScript-ESLint/minimatch; Storybook/glob/minimatch | dev/build | Lockfile-only compatible refresh to 1.1.18 / 5.0.9 |
| browserslist | high | 1153171, 1153172 | Autoprefixer and Storybook/Babel tooling | build/dev | Lockfile-only compatible refresh to 4.28.9 |
| js-yaml | high | 1123911, 1138115 | ESLint configuration tooling | dev/build | Lockfile-only compatible refresh to 4.3.2 |
| nanoid | high | 1138811, 1139427 | PostCSS | build/dev | Lockfile-only compatible refresh to 3.3.18 |
| postcss | high | 1130709, 1139510 | Direct PostCSS dependency and Vite/Tailwind tooling | build/dev | Lockfile-only compatible refresh to 8.5.28 |

`npm audit fix --package-lock-only` was used without `--force`; it changed only compatible transitive lockfile resolutions and left `package.json`, framework versions, Playwright, Storybook, and scripts unchanged. No overrides were added. Post-remediation audit is zero, including production audit.

Verification covered lint, unit tests, application build, Storybook build, and the existing 14-test Playwright suite without snapshot updates. Backend and CI behavior are outside this remediation and unchanged.
