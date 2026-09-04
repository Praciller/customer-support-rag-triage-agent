import { expect, test } from "@playwright/test";

test("health failure shows a safe unavailable state without leaking internals", async ({ page }) => {
  await page.route("**/health", (route) => route.abort());
  await page.goto("/");
  await expect(page.getByText("API unavailable", { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Customer message" })).toBeVisible();
  await expect(page.getByText(/traceback|api[_-]?key|secret|password|C:\\Users|\/home\/runner/i)).toHaveCount(0);
});
