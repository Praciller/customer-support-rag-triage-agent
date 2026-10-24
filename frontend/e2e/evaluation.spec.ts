import { expect, test } from "@playwright/test";

import { installReviewedOnnxEvaluation } from "./support/reviewed-evaluation";

test("Evaluation renders reviewed ONNX mock metrics and limitations", async ({ page }) => {
  await installReviewedOnnxEvaluation(page);
  await page.goto("/");
  await page.getByRole("button", { name: "Evaluation", exact: true }).click();
  await expect(page.getByText("Measured artifact", { exact: true })).toBeVisible();
  await expect(page.getByText(/deterministic/i).first()).toBeVisible();
  await expect(page.getByText(/Precision@|Recall@|Intent accuracy/).first()).toBeVisible();
  await expect(page.getByRole("heading", { name: "Intent metrics by class" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Methodology and limitations" })).toBeVisible();
  await expect(page.getByText(/small|fixture|not a production SLA/i).last()).toBeVisible();
});

test("Evaluation groups reviewed ONNX metrics at tablet width", async ({ page }) => {
  await installReviewedOnnxEvaluation(page);
  await page.setViewportSize({ width: 768, height: 1024 });
  await page.goto("/");
  await page.getByRole("button", { name: "Evaluation", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Retrieval quality" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Workflow checks" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Runtime profile" })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(
    await page.evaluate(() => document.documentElement.clientWidth),
  );
});

test("Evaluation never shows incompatible ONNX metrics as hashing measurements", async ({ page }) => {
  // CI's live test backend deliberately uses the hashing embedder, not ONNX.
  await page.goto("/");
  await page.getByRole("button", { name: "Evaluation", exact: true }).click();
  await expect(page.getByRole("heading", { name: "No compatible evaluation report" })).toBeVisible();
  await expect(page.getByText("Measured artifact", { exact: true })).not.toBeVisible();
});
