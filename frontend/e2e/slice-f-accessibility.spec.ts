import { expect, test } from "@playwright/test";
import { makeTriageResult } from "../src/test/fixtures";
import { installReviewedOnnxEvaluation } from "./support/reviewed-evaluation";

for (const width of [390, 768, 1440]) {
  test(`keyboard skip link reaches main at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 390 ? 844 : 1000 });
    await page.goto("/");
    const skip = page.getByRole("link", { name: "Skip to main content" });
    const main = page.getByRole("main");

    await page.keyboard.press("Tab");
    await expect(skip).toBeFocused();
    await expect(skip).toBeVisible();
    await page.keyboard.press("Enter");
    await expect(main).toBeFocused();
    await expect(main).toHaveAttribute("id", "main-content");
  });
}

test("mobile classification table exposes all column labels and values", async ({ page }) => {
  await installReviewedOnnxEvaluation(page);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.getByRole("button", { name: "Evaluation", exact: true }).click();

  const table = page.getByRole("table");
  await expect(table).toBeVisible();
  for (const heading of ["Intent", "Precision", "Recall", "F1", "Support"]) {
    await expect(table.getByRole("columnheader", { name: heading })).toHaveCount(1);
  }
  await expect(table.locator('td[data-label="Support"]').first()).toBeVisible();
  await expect(page.getByRole("heading", { name: "Methodology and limitations" })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
});

test("degraded ungrounded triage retains explicit manual-review semantics and keyboard details", async ({ page }) => {
  const base = makeTriageResult();
  const result = makeTriageResult({
    grounded: false,
    grounding_score: 0,
    citation_integrity: false,
    fallback_used: true,
    degraded_mode: true,
    next_action: "manual_review",
    trace: base.trace.map((step, index) => index === 4 ? { ...step, fallback: true, degraded_mode: true } : step),
  });
  await page.route("**/triage", (route) => route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify(result),
  }));
  await page.goto("/");
  await page.getByRole("button", { name: "Run triage", exact: true }).click();

  const decision = page.getByRole("region", { name: "Recommended action" });
  await expect(decision).toContainText("manual review");
  await expect(decision.getByLabel("Grounding status: not grounded")).toBeVisible();
  await expect(decision).toContainText("Citation rejected");
  await expect(decision.getByRole("status").filter({ hasText: "A safe fallback was used." }))
    .toContainText("Review retrieved evidence and respond manually.");

  const trace = page.getByRole("region", { name: "Workflow trace" });
  await expect(trace.getByRole("listitem")).toHaveCount(7);
  await expect(trace).toContainText("degraded");
  const details = trace.locator("details").first();
  await details.locator("summary").focus();
  await page.keyboard.press("Enter");
  await expect(details).toHaveAttribute("open", "");
  await expect(details.getByText("Evidence references")).toBeVisible();
});

test("evaluation failure is announced without a misleading zero-score success state", async ({ page }) => {
  await page.route("**/eval/results", (route) => route.abort());
  await page.goto("/");
  await page.getByRole("button", { name: "Evaluation", exact: true }).click();

  await expect(page.getByRole("alert")).toContainText("Evaluation artifacts are unavailable");
  await expect(page.getByRole("heading", { name: "Retrieval quality" })).toHaveCount(0);
});

test("reduced-motion preference suppresses nonessential transitions", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  const durations = await page.getByRole("button", { name: "Card not arrived", exact: true })
    .evaluate((button) => getComputedStyle(button).transitionDuration.split(",").map((duration) => {
      const value = duration.trim();
      return value.endsWith("ms") ? Number.parseFloat(value) : Number.parseFloat(value) * 1000;
    }));
  expect(durations.every((duration) => Number.isFinite(duration) && duration <= 1)).toBe(true);
});
