import { expect, test, type Page } from "@playwright/test";
import { makeEvaluation, makeTriageResult } from "../src/test/fixtures";

async function installSyntheticRoutes(page: Page) {
  await page.route("**/health", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ status: "ok" }),
    }),
  );
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
}

for (const width of [390, 768, 1440]) {
  test(`Slice E owner-review images at ${width}px (synthetic fixtures)`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 390 ? 844 : 1000 });
    await installSyntheticRoutes(page);
    await page.goto("/");
    await expect(page.getByText("API connected", { exact: true })).toBeVisible();

    await page.getByRole("button", { name: "Card not arrived", exact: true }).click();
    await page.getByRole("button", { name: "Run triage", exact: true }).click();
    await expect(page.getByRole("heading", { name: "Seven-node execution trace" })).toBeVisible();
    await expect(page.getByRole("list", { name: "Workflow execution steps" }).getByRole("listitem")).toHaveCount(7);
    await page.evaluate(() => document.fonts.ready);
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(
      await page.evaluate(() => document.documentElement.clientWidth),
    );
    await page.screenshot({
      path: `review-evidence/slice-e-trace-${width}.png`,
      fullPage: true,
      animations: "disabled",
      caret: "hide",
      scale: "css",
    });

    await page.getByRole("button", { name: "Evaluation", exact: true }).click();
    await expect(page.getByRole("heading", { name: "Retrieval quality" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Workflow checks" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Runtime profile" })).toBeVisible();
    await page.evaluate(() => document.fonts.ready);
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(
      await page.evaluate(() => document.documentElement.clientWidth),
    );
    await page.screenshot({
      path: `review-evidence/slice-e-evaluation-${width}.png`,
      fullPage: true,
      animations: "disabled",
      caret: "hide",
      scale: "css",
    });
  });
}
