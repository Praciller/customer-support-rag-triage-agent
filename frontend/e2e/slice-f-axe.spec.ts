import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

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
    await page.setViewportSize({ width, height: width === 390 ? 844 : 900 });
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Customer message" })).toBeVisible();
    await expectNoWcagViolations(page, `triage ${width}px`);

    await page.getByRole("button", { name: "Evaluation", exact: true }).click();
    await expect(page.getByRole("heading", { name: "Methodology and limitations" })).toBeVisible();
    await expectNoWcagViolations(page, `evaluation ${width}px`);
  });
}
