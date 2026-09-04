import { expect, test } from "@playwright/test";

const nodes = ["normalize message", "classify intent", "detect urgency", "retrieve similar cases", "generate support response", "grounding check", "suggest next action"];

test("startup reports a usable connected API", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("API connected", { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Customer message" })).toBeVisible();
});

test("Card not arrived produces a grounded seven-node decision", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Card not arrived", exact: true }).click();
  await page.getByRole("button", { name: "Run triage", exact: true }).click();
  const decision = page.getByRole("article").filter({ has: page.getByRole("heading", { name: "Triage summary" }) });
  await expect(decision).toContainText(/Intent|Urgency|Next action/);
  await expect(decision).toContainText(/Grounded|citation/i);
  const evidence = page.getByRole("article").filter({ has: page.getByRole("heading", { name: "Similar cases" }) });
  await expect(evidence).toContainText("found");
  await expect(evidence.getByRole("article").first()).toBeVisible();
  const trace = page.locator("section").filter({ has: page.getByRole("heading", { name: "Seven-node execution trace" }) });
  for (const node of nodes) await expect(trace).toContainText(node);
});

test("a high-risk example shows an actual escalation decision", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Suspicious transaction", exact: true }).click();
  await page.getByRole("button", { name: "Run triage", exact: true }).click();
  const decision = page.getByRole("article").filter({ has: page.getByRole("heading", { name: "Triage summary" }) });
  await expect(decision.getByText("Escalate", { exact: true })).toBeVisible();
  await expect(decision).toContainText(/high|critical/i);
  await expect(decision).toContainText("Escalation reason");
  await expect(decision).toContainText(/human|review|protect|unauthorized|risk/i);
});
