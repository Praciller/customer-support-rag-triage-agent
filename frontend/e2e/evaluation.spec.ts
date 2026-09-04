import { expect, test } from "@playwright/test";

test("Evaluation shows measured deterministic artifacts and limitations", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Evaluation", exact: true }).click();
  await expect(page.getByText("Measured artifact", { exact: true })).toBeVisible();
  await expect(page.getByText(/deterministic/i).first()).toBeVisible();
  await expect(page.getByText(/Precision@|Recall@|Intent accuracy/).first()).toBeVisible();
  await expect(page.getByRole("heading", { name: "Intent metrics by class" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Methodology and limitations" })).toBeVisible();
  await expect(page.getByText(/small|fixture|not a production SLA/i).last()).toBeVisible();
});
