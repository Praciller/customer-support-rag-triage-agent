import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./storybook-e2e",
  timeout: 30_000,
  expect: { timeout: 10_000 },
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:6006",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    colorScheme: "light",
    reducedMotion: "reduce",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: "npx storybook dev -p 6006 --ci --no-open --host 127.0.0.1 --disable-telemetry",
    env: { STORYBOOK_COMPONENT_A11Y_E2E: "1" },
    url: "http://127.0.0.1:6006/iframe.html",
    timeout: 120_000,
    reuseExistingServer: !process.env.CI,
  },
});
