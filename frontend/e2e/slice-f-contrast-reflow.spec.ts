import { expect, test, type Page } from "@playwright/test";
import { installReviewedOnnxEvaluation } from "./support/reviewed-evaluation";

async function assertNoDocumentOverflow(page: Page) {
  const dimensions = await page.evaluate(() => ({
    content: document.documentElement.scrollWidth,
    viewport: document.documentElement.clientWidth,
  }));
  expect(dimensions.content, "No page-level horizontal overflow; locally scrollable tables are allowed")
    .toBeLessThanOrEqual(dimensions.viewport);
}

test("320px reflow keeps triage and evaluation usable", async ({ page }) => {
  await installReviewedOnnxEvaluation(page);
  await page.setViewportSize({ width: 320, height: 780 });
  await page.goto("/");
  await expect(page.getByRole("link", { name: "Skip to main content" })).toBeAttached();
  await expect(page.getByRole("heading", { name: "Customer message" })).toBeVisible();
  await assertNoDocumentOverflow(page);

  await page.getByRole("button", { name: "Card not arrived", exact: true }).click();
  await page.getByRole("button", { name: "Run triage", exact: true }).click();
  await expect(page.getByRole("region", { name: "Recommended action" })).toContainText("ask for order id");
  await expect(page.getByRole("region", { name: "Workflow trace" }).getByRole("listitem")).toHaveCount(7);
  await assertNoDocumentOverflow(page);

  await page.getByRole("button", { name: "Evaluation", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Retrieval quality" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Methodology and limitations" })).toBeVisible();
  await expect(page.locator('.evaluation-table td[data-label="Support"]').first()).toBeVisible();
  await assertNoDocumentOverflow(page);
});

test("status labels meet a sampled 4.5:1 browser-computed text contrast gate", async ({ page }) => {
  await page.goto("/");
  const results = await page.evaluate(() => {
    // Sample source-owned state-token classes against their actual computed backgrounds.
    // Canvas converts OKLCH and CSS color-mix output to sRGB before ratio calculation.
    const canvas = document.createElement("canvas");
    canvas.width = 1;
    canvas.height = 1;
    const context = canvas.getContext("2d", { willReadFrequently: true });
    if (!context) throw new Error("Unable to measure contrast: canvas unavailable");

    const srgb = (color: string): number[] => {
      context.clearRect(0, 0, 1, 1);
      context.fillStyle = color;
      context.fillRect(0, 0, 1, 1);
      const rgba = Array.from(context.getImageData(0, 0, 1, 1).data);
      if (rgba[3] !== 255) throw new Error(`Opaque text/background expected: ${color}`);
      return rgba.slice(0, 3).map((channel) => channel / 255);
    };
    const luminance = (rgb: number[]) =>
      rgb.map((c) => c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)
        .reduce((total, c, index) => total + c * [0.2126, 0.7152, 0.0722][index], 0);

    return ["badge", "badge-success", "badge-warning", "badge-danger"].map((modifier) => {
      const sample = document.createElement("span");
      sample.className = modifier === "badge" ? "badge" : `badge ${modifier}`;
      sample.textContent = "State label";
      document.body.appendChild(sample);
      const style = getComputedStyle(sample);
      const fg = luminance(srgb(style.color));
      const bg = luminance(srgb(style.backgroundColor));
      sample.remove();
      return { state: modifier, ratio: (Math.max(fg, bg) + 0.05) / (Math.min(fg, bg) + 0.05) };
    });
  });
  for (const result of results) {
    expect(result.ratio, `Contrast of ${result.state} is ${result.ratio.toFixed(2)}:1`)
      .toBeGreaterThanOrEqual(4.5);
  }
});
