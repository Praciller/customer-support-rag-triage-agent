import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";
import { makeTriageResult } from "../src/test/fixtures";
import { installReviewedOnnxEvaluation } from "./support/reviewed-evaluation";

// Axe checks are a repeatable, scoped WCAG A/AA regression gate, not a
// replacement for manual screen-reader, focus, or browser-zoom review.
const wcagTags = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];

async function expectNoWcagViolations(page: Page, screen: string): Promise<void> {
  const results = await new AxeBuilder({ page }).withTags(wcagTags).analyze();
  const failures = results.violations.map((violation) => ({
    rule: violation.id,
    impact: violation.impact,
    elements: violation.nodes.map((node) => node.target.join(" ")),
  }));
  expect(failures, `WCAG A/AA violations in ${screen}`).toEqual([]);
}

for (const width of [390, 1440]) {
  test(`axe WCAG smoke: triage and evaluation at ${width}px`, async ({ page }) => {
    await installReviewedOnnxEvaluation(page);
    await page.setViewportSize({ width, height: width === 390 ? 844 : 900 });
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Customer message" })).toBeVisible();
    await expectNoWcagViolations(page, `triage ${width}px`);

    await page.getByRole("button", { name: "Evaluation", exact: true }).click();
    await expect(page.getByRole("heading", { name: "Methodology and limitations" })).toBeVisible();
    await expectNoWcagViolations(page, `evaluation ${width}px`);
  });
}

for (const width of [390, 1440]) {
  test(`axe WCAG state smoke: degraded triage and failed evaluation at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 390 ? 844 : 900 });
    const base = makeTriageResult();
    const degraded = makeTriageResult({
      grounded: false,
      grounding_score: 0,
      citation_integrity: false,
      fallback_used: true,
      degraded_mode: true,
      next_action: "manual_review",
      trace: base.trace.map((step, index) =>
        index === 4 ? { ...step, fallback: true, degraded_mode: true } : step),
    });
    await page.route("**/triage", (route) => route.fulfill({
      status: 200, contentType: "application/json", body: JSON.stringify(degraded),
    }));
    await page.route("**/eval/results", (route) => route.abort());

    await page.goto("/");
    await page.getByRole("button", { name: "Run triage", exact: true }).click();
    const decision = page.getByRole("region", { name: "Recommended action" });
    await expect(decision).toContainText("manual review");
    await expect(decision.getByRole("status").filter({ hasText: "A safe fallback was used." }))
      .toBeVisible();
    await expectNoWcagViolations(page, `degraded triage ${width}px`);

    await page.getByRole("button", { name: "Evaluation", exact: true }).click();
    await expect(page.getByRole("alert")).toContainText("Evaluation artifacts are unavailable");
    await expectNoWcagViolations(page, `evaluation unavailable ${width}px`);
  });
}
