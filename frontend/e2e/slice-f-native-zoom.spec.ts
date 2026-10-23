import AxeBuilder from "@axe-core/playwright";
import { expect, test, chromium } from "@playwright/test";
import { mkdtemp, mkdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { makeEvaluation, makeTriageResult } from "../src/test/fixtures";

// This uses Chrome's native tab zoom API, NOT page-scale emulation, pinch zoom,
// device scaling, or a narrower viewport presented as 200% browser zoom.
test("native Chromium 200% zoom preserves Triage and Evaluation reflow", async () => {
  const workDir = await mkdtemp(path.join(tmpdir(), "csrta-native-zoom-"));
  const extension = path.join(workDir, "zoom-extension");
  const profile = path.join(workDir, "profile");
  let context: Awaited<ReturnType<typeof chromium.launchPersistentContext>> | undefined;

  try {
    await mkdir(extension);
    await writeFile(
      path.join(extension, "manifest.json"),
      JSON.stringify({
        manifest_version: 3,
        name: "Isolated native zoom smoke",
        version: "0.0.1",
        permissions: ["tabs"],
        background: { service_worker: "worker.js" },
      }),
    );
    await writeFile(
      path.join(extension, "worker.js"),
      "chrome.runtime.onInstalled.addListener(() => {});",
    );
    context = await chromium.launchPersistentContext(profile, {
      channel: "chromium",
      headless: true,
      viewport: { width: 1280, height: 900 },
      args: [
        `--disable-extensions-except=${extension}`,
        `--load-extension=${extension}`,
      ],
    });
    const worker =
      context.serviceWorkers()[0] ??
      (await context.waitForEvent("serviceworker", { timeout: 15_000 }));
    const page = await context.newPage();
    await page.route("**/triage", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(makeTriageResult()),
      }),
    );
    await page.route("**/eval/results", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(makeEvaluation()),
      }),
    );
    await page.goto("http://127.0.0.1:5173/");
    const initial = await page.evaluate(() => window.innerWidth);
    expect(initial).toBe(1280);

    const zoom = await worker.evaluate(async () => {
      const tabs = await chrome.tabs.query({ url: "http://127.0.0.1:5173/*" });
      const tabId = tabs[0]?.id;
      if (tabId === undefined) throw new Error("Local UI tab not found");
      const before = await chrome.tabs.getZoom(tabId);
      await chrome.tabs.setZoom(tabId, 2);
      const after = await chrome.tabs.getZoom(tabId);
      return { before, after };
    });
    expect(zoom).toEqual({ before: 1, after: 2 });

    for (const width of [1280, 768, 640]) {
      await page.setViewportSize({ width, height: 900 });
      await page.goto("http://127.0.0.1:5173/");
      await expect(page.getByRole("heading", { name: "Customer message" })).toBeVisible();
      if (width === 640) {
        await page.keyboard.press("Tab");
        await expect(page.getByRole("link", { name: "Skip to main content" })).toBeFocused();
      }
      const dimensions = await page.evaluate(() => ({
        cssWidth: window.innerWidth,
        dpr: window.devicePixelRatio,
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      }));
      expect(dimensions.cssWidth, `Native 200% zoom should halve ${width}px`)
        .toBe(width / 2);
      expect(dimensions.dpr).toBe(2);
      expect(
        dimensions.scrollWidth,
        `No document horizontal overflow at native 200% zoom, CSS ${width / 2}px`,
      ).toBeLessThanOrEqual(dimensions.clientWidth);

      await page.getByRole("button", { name: "Card not arrived", exact: true }).click();
      await page.getByRole("button", { name: "Run triage", exact: true }).click();
      await expect(page.getByRole("region", { name: "Recommended action" }))
        .toContainText("ask for order id");
      await expect(page.getByRole("region", { name: "Workflow trace" }).getByRole("listitem"))
        .toHaveCount(7);
      const triageWidth = await page.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      }));
      expect(triageWidth.scrollWidth).toBeLessThanOrEqual(triageWidth.clientWidth);
      if (width === 640) {
        const scan = await new AxeBuilder({ page }).withTags([
          "wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa",
        ]).analyze();
        expect(scan.violations.map((violation) => violation.id)).toEqual([]);
      }

      await page.getByRole("button", { name: "Evaluation", exact: true }).click();
      await expect(page.getByRole("heading", { name: "Retrieval quality" })).toBeVisible();
      await expect(page.getByRole("heading", { name: "Methodology and limitations" }))
        .toBeVisible();
      const evalWidth = await page.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      }));
      expect(evalWidth.scrollWidth).toBeLessThanOrEqual(evalWidth.clientWidth);
      if (width === 640) {
        const scan = await new AxeBuilder({ page }).withTags([
          "wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa",
        ]).analyze();
        expect(scan.violations.map((violation) => violation.id)).toEqual([]);
      }
    }
  } finally {
    await context?.close();
    await rm(workDir, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 });
  }
});
