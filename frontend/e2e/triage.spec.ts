import { expect, test } from "@playwright/test";

const nodes = [
  "normalize message",
  "classify intent",
  "detect urgency",
  "retrieve similar cases",
  "generate support response",
  "grounding check",
  "suggest next action",
];

test("startup reports a usable connected API", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("API connected", { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Customer message" })).toBeVisible();
});

test("Card not arrived produces a grounded seven-node decision", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Card not arrived", exact: true }).click();
  await page.getByRole("button", { name: "Run triage", exact: true }).click();

  const decision = page.getByRole("article").filter({
    has: page.getByRole("heading", { name: "Triage summary" }),
  });
  await expect(decision.getByText("Intent", { exact: true })).toBeVisible();
  await expect(decision.getByText("delivery issue", { exact: true })).toBeVisible();
  await expect(decision.getByText("Urgency", { exact: true })).toBeVisible();
  await expect(decision.getByText("medium", { exact: true })).toBeVisible();
  await expect(decision.getByText("Next action", { exact: true })).toBeVisible();
  await expect(decision.getByText("ask for order id", { exact: true })).toBeVisible();
  await expect(decision.getByText(/grounded/i)).toBeVisible();
  await expect(decision.getByText("citations checked", { exact: true })).toBeVisible();

  const evidence = page.getByRole("article").filter({
    has: page.getByRole("heading", { name: "Similar cases" }),
  });
  await expect(evidence).toContainText("found");
  const firstCase = evidence.getByRole("article").first();
  await expect(firstCase).toBeVisible();
  await expect(firstCase).toContainText("% match");
  await expect(firstCase).toContainText("mteb/banking77");
  await expect(firstCase).toContainText("demo-delivery-estimate");

  const trace = page.locator("section").filter({
    has: page.getByRole("heading", { name: "Seven-node execution trace" }),
  });
  const traceItems = trace.getByRole("listitem");
  await expect(traceItems).toHaveCount(nodes.length);
  for (const [index, node] of nodes.entries()) {
    await expect(traceItems.nth(index)).toContainText(`${index + 1}. ${node}`);
  }
});

test("a high-risk example shows an actual escalation decision", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Suspicious transaction", exact: true }).click();
  await page.getByRole("button", { name: "Run triage", exact: true }).click();

  const decision = page.getByRole("article").filter({
    has: page.getByRole("heading", { name: "Triage summary" }),
  });
  await expect(decision.getByText("Escalate", { exact: true })).toBeVisible();
  await expect(decision.getByText("high", { exact: true })).toBeVisible();
  await expect(decision).toContainText("Escalation reason");
  await expect(decision).toContainText(/human|review|protect|unauthorized|risk/i);
});
