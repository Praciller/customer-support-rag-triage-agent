import { defineConfig, devices } from "@playwright/test";
import { existsSync } from "node:fs";
import { resolve } from "node:path";

const inheritedEnv = Object.fromEntries(Object.entries(process.env).filter((entry): entry is [string, string] => entry[1] !== undefined));
const windowsPython = ".venv\\Scripts\\python.exe";
const python = process.platform === "win32" && existsSync(resolve("..", windowsPython)) ? windowsPython : "python";

export default defineConfig({
  testDir: "./e2e", timeout: 30_000, expect: { timeout: 5_000 }, fullyParallel: false,
  workers: 1, retries: process.env.CI ? 1 : 0,
  reporter: [["list"], ["html", { outputFolder: "playwright-report", open: "never" }]],
  use: { baseURL: "http://127.0.0.1:5173", trace: "retain-on-failure", screenshot: "only-on-failure", video: "retain-on-failure" },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"], browserName: "chromium" } }],
  webServer: [
    { command: `${python} -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000`, cwd: "..", env: { ...inheritedEnv, DEMO_MODE: "true", MOCK_LLM_MODE: "true", QDRANT_MODE: "memory", EMBEDDING_PROVIDER: "hashing", RETRIEVAL_MIN_SCORE: "0", LLM_CACHE_ENABLED: "false" }, url: "http://127.0.0.1:8000/health", timeout: 120_000, reuseExistingServer: !process.env.CI },
    { command: "npm run dev -- --host 127.0.0.1", url: "http://127.0.0.1:5173", timeout: 120_000, reuseExistingServer: !process.env.CI },
  ],
});
