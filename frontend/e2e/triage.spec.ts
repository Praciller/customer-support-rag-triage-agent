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

test("mobile More exposes labelled secondary tools and closes with Escape", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(page.getByRole("button", { name: "Triage", exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Evaluation", exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Trace", exact: true })).toBeVisible();
  const primary = page.locator(".responsive-primary");
  const order = await primary.locator("button").evaluateAll((buttons) => buttons.map((button) => button.textContent?.trim()));
  expect(order).toEqual(["Triage", "Evaluation", "Trace", "More"]);
  const more = primary.getByRole("button", { name: "More", exact: true });
  await more.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("menu")).toBeVisible();
  await expect(page.getByRole("menuitem", { name: "Overview" })).toBeVisible();
  await expect(page.getByRole("menuitem", { name: "Semantic search" })).toBeVisible();
  await expect(page.getByRole("menuitem", { name: "Dataset explorer" })).toBeVisible();
  await expect(page.getByRole("menuitem", { name: "Provider status" })).toBeVisible();
  await page.keyboard.press("ArrowDown");
  await page.keyboard.press("ArrowUp");
  await page.keyboard.press("Enter");
  await expect(page.getByRole("heading", { name: "Overview" })).toBeVisible();
  await expect(page.getByRole("menu")).toBeHidden();
  await expect(more).toHaveAttribute("data-current-secondary", "true");
  await more.click();
  await expect(page.getByRole("menuitem", { name: "Overview" })).toHaveAttribute("data-current", "true");
  await expect(page.getByRole("menuitem", { name: "Overview" }).locator("[aria-current='page']")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("menu")).toBeHidden();
  await expect(more).toBeFocused();
});
