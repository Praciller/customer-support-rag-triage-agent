import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

// Storybook renders reusable components in isolation, separately from the
// app-wide route checks in e2e/slice-f-axe.spec.ts.
const stories = [
  { id: "resolveops-trace-tracelist--normal", visibleText: "normalize message" },
  { id: "resolveops-trace-tracelist--fallback", visibleText: "normalize message" },
  { id: "resolveops-trace-tracelist--degraded", visibleText: "normalize message" },
  { id: "resolveops-trace-tracelist--incomplete", visibleText: "normalize message" },
  { id: "resolveops-trace-tracelist--empty", visibleText: "Run triage to inspect the workflow." },
  { id: "resolveops-evaluation-evaluationchart--deterministic-baseline", visibleText: "Offline baseline metrics" },
  { id: "resolveops-triage-triagedecision--ungrounded", visibleText: "manual review" },
  { id: "resolveops-triage-decisionworkspace--ungrounded-manual-review", visibleText: "Human review remains required" },
] as const;

const wcagTags = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];

for (const width of [390, 1440]) {
  for (const { id, visibleText } of stories) {
    test(`Storybook WCAG A/AA: ${id} at ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: width === 390 ? 844 : 900 });
      await page.goto(`/iframe.html?id=${encodeURIComponent(id)}&viewMode=story`);
      const root = page.locator("#storybook-root");
      // Fail closed if the intended story is missing, errored or blank.
      await expect(root).toContainText(new RegExp(visibleText, "i"));
      const results = await new AxeBuilder({ page })
        .include("#storybook-root")
        .withTags(wcagTags)
        .analyze();
      expect(
        results.violations.map((violation) => ({
          rule: violation.id,
          impact: violation.impact,
          elements: violation.nodes.map((node) => node.target.join(" ")),
        })),
        `Storybook axe failures in ${id} at ${width}px`,
      ).toEqual([]);
    });
  }
}
