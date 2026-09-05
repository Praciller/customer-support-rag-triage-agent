import { expect, test, type Page } from "@playwright/test";
import { makeEvaluation, makeTriageResult } from "../src/test/fixtures";

async function installVisualRoutes(page: Page, result = makeTriageResult()) {
  await page.route("**/health", (route) => route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ status: "ok" }) }));
  await page.route("**/triage", (route) => route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(result) }));
  await page.route("**/eval/results", (route) => route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(makeEvaluation()) }));
}

async function runSuccess(page: Page) {
  await page.goto("/");
  await expect(page.getByText("API connected", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Card not arrived", exact: true }).click();
  await page.getByRole("button", { name: "Run triage", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Triage summary" })).toBeVisible();
}

test("initial triage desktop baseline", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 }); await installVisualRoutes(page); await page.goto("/");
  await expect(page.getByText("API connected", { exact: true })).toBeVisible(); await expect(page.getByRole("heading", { name: "Customer message" })).toBeVisible(); await expect(page.getByRole("heading", { name: "Triage summary" })).toBeVisible(); await page.evaluate(() => document.fonts.ready);
  await expect(page).toHaveScreenshot("triage-initial-desktop.png", { fullPage: true, animations: "disabled", caret: "hide", scale: "css" });
});

test("successful triage desktop baseline", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 }); await installVisualRoutes(page); await runSuccess(page);
  await expect(page.getByRole("main")).toContainText(/delivery issue|medium|ask for order id|grounded|citations checked|Similar cases|Seven-node execution trace/i); await page.evaluate(() => document.fonts.ready);
  await expect(page).toHaveScreenshot("triage-success-desktop.png", { fullPage: true, animations: "disabled", caret: "hide", scale: "css" });
});

test("escalated triage desktop baseline", async ({ page }) => {
  const result = makeTriageResult({ normalized_message: "A cash withdrawal was made from my account, but I did not make it. This is urgent.", intent: "billing_issue", urgency: "high", escalate: true, escalation_reason: "Customer language indicates immediate financial or service risk" });
  await page.setViewportSize({ width: 1440, height: 1000 }); await installVisualRoutes(page, result); await page.goto("/"); await expect(page.getByText("API connected", { exact: true })).toBeVisible(); await page.getByRole("button", { name: "Suspicious transaction", exact: true }).click(); await page.getByRole("button", { name: "Run triage", exact: true }).click();
  await expect(page.getByText("Escalate", { exact: true })).toBeVisible(); await expect(page.getByRole("main")).toContainText(/high|Escalation reason/i); await page.evaluate(() => document.fonts.ready);
  await expect(page).toHaveScreenshot("triage-escalated-desktop.png", { fullPage: true, animations: "disabled", caret: "hide", scale: "css" });
});

test("evaluation desktop baseline", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 }); await installVisualRoutes(page); await page.goto("/"); await page.getByRole("button", { name: "Evaluation", exact: true }).click();
  await expect(page.getByText("Measured artifact", { exact: true })).toBeVisible(); await expect(page.getByRole("heading", { name: "Offline baseline metrics" })).toBeVisible(); await expect(page.getByRole("heading", { name: "Intent metrics by class" })).toBeVisible(); await expect(page.getByRole("heading", { name: "Methodology and limitations" })).toBeVisible(); await expect(page.getByText(/deterministic|not a production SLA/i).last()).toBeVisible(); await page.evaluate(() => document.fonts.ready);
  await expect(page).toHaveScreenshot("evaluation-desktop.png", { fullPage: true, animations: "disabled", caret: "hide", scale: "css" });
});

test("successful triage mobile baseline and hierarchy", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 }); await installVisualRoutes(page); await runSuccess(page);
  const decision = page.getByRole("region", { name: "Recommended action" }); const evidence = page.getByRole("region", { name: "Retrieved evidence" }); const trace = page.getByRole("region", { name: "Workflow trace" });
  const boxes = await Promise.all([decision, evidence, trace].map((locator) => locator.boundingBox())); if (boxes.some((box) => box === null)) throw new Error("Expected mobile decision, evidence, and trace boxes");
  if (!(boxes[0]!.y < boxes[1]!.y && boxes[1]!.y < boxes[2]!.y)) throw new Error("Mobile hierarchy order is incorrect");
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(await page.evaluate(() => document.documentElement.clientWidth)); await page.evaluate(() => document.fonts.ready);
  await expect(page).toHaveScreenshot("triage-success-mobile-390.png", { fullPage: true, animations: "disabled", caret: "hide", scale: "css" });
});

for (const width of [390, 768, 1440]) test(`responsive triage has no page overflow at ${width}px`, async ({ page }) => {
  await page.setViewportSize({ width, height: width === 390 ? 844 : 1000 }); await installVisualRoutes(page); await runSuccess(page);
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(await page.evaluate(() => document.documentElement.clientWidth));
});

test("evaluation has no page overflow at 390px", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 }); await installVisualRoutes(page); await page.goto("/"); await page.getByRole("button", { name: "Evaluation", exact: true }).click(); await expect(page.getByText("Measured artifact", { exact: true })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(await page.evaluate(() => document.documentElement.clientWidth));
});
