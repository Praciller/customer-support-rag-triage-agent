import { expect, test } from "@playwright/test";
import { makeTriageResult } from "../src/test/fixtures";

const nodes = [
  "normalize message",
  "classify intent",
  "detect urgency",
  "retrieve similar cases",
  "generate support response",
  "policy gate",
  "suggest next action",
];

for (const backend of ["v1", "upgrade-required"]) {
  test(`shows controlled version mismatch for ${backend} without rendering a decision`, async ({ page }) => {
    let requests = 0;
    await page.route("**/triage", (route) => {
      requests += 1;
      expect(route.request().headers()["x-resolveops-api-version"]).toBe("2");
      return route.fulfill({
        status: backend === "v1" ? 200 : 426,
        contentType: "application/json",
        body: JSON.stringify(backend === "v1"
          ? { grounded: true, grounding_score: 0.86, suggested_response: "Legacy fixture" }
          : { detail: "API v2 required" }),
      });
    });
    await page.goto("/");
    await page.getByRole("button", { name: "Run triage", exact: true }).click();
    await expect(page.getByRole("alert")).toContainText("console and API versions do not match");
    await expect(page.getByText("Legacy fixture")).toHaveCount(0);
    await expect(page.getByRole("button", { name: "Retry triage", exact: true })).toHaveCount(0);
    expect(requests).toBe(1);
  });
}

test("startup reports a usable connected API", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("API connected", { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Customer message" })).toBeVisible();
});

test("shows a cold-start wait, times out, and retries only after a manual action", async ({ page }) => {
  let triageRequests = 0;
  let releaseFirstResponse!: () => void;
  const firstResponseHeld = new Promise<void>((resolve) => {
    releaseFirstResponse = resolve;
  });
  await page.clock.install();
  await page.route("**/health", (route) => route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify({ status: "ok" }),
  }));
  await page.route("**/triage", async (route) => {
    triageRequests += 1;
    if (triageRequests === 1) {
      await firstResponseHeld;
      await route.fulfill({
        status: 504,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Request timed out" }),
      });
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(makeTriageResult()),
    });
  });

  await page.goto("/");
  await page.getByRole("button", { name: "Run triage", exact: true }).click();
  await expect(page.getByText(/backend may be starting after an idle period/i)).toBeVisible();
  releaseFirstResponse();
  await expect(page.getByRole("alert")).toContainText(/backend timed out while processing triage/i);
  await expect(page.getByRole("button", { name: "Retry triage", exact: true })).toBeVisible();
  await page.clock.fastForward(65_000);
  expect(triageRequests).toBe(1);

  await page.getByRole("button", { name: "Retry triage", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Seven-node execution trace" })).toBeVisible();
  expect(triageRequests).toBe(2);
});

test("Card not arrived without approved policy routes to human review", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Card not arrived", exact: true }).click();
  await page.getByRole("button", { name: "Run triage", exact: true }).click();

  const decision = page.getByRole("region", { name: "Recommended action" });
  await expect(decision.getByText("Intent", { exact: true })).toBeVisible();
  await expect(decision.getByText("delivery issue", { exact: true })).toBeVisible();
  await expect(decision).toContainText("Urgency:");
  await expect(decision.getByText("medium", { exact: true })).toBeVisible();
  await expect(decision.getByText("Next action", { exact: true })).toBeVisible();
  await expect(decision.getByText("manual review", { exact: true })).toBeVisible();
  await expect(decision.getByLabel("Policy review status: No approved policy")).toBeVisible();
  await expect(decision).toContainText("Similar past cases are context only");
  await expect(decision).toContainText("A support specialist needs to review this before we can advise on next steps.");
  await expect(decision).not.toContainText(/refund options|order id/i);
  await expect(decision).toContainText("proposal 1: no approved policy");

  const evidence = page.getByRole("region", { name: "Similar past cases" });
  await expect(evidence).toContainText("found");
  const firstCase = evidence.getByRole("listitem").first();
  await expect(firstCase).toBeVisible();
  await expect(firstCase).toContainText("similarity");
  await expect(firstCase).toContainText("Not approved policy");
  await expect(firstCase).toContainText("mteb/banking77");
  await expect(firstCase).toContainText("demo-delivery-estimate");

  const trace = page.getByRole("region", { name: "Workflow trace" });
  const details = page.getByRole("group", { name: "Technical details" });
  await expect(details).toBeVisible();
  await expect(decision).toHaveAttribute("aria-label", "Recommended action");
  const decisionBox = await decision.boundingBox();
  const evidenceBox = await evidence.boundingBox();
  const traceBox = await trace.boundingBox();
  expect(decisionBox && evidenceBox && traceBox && decisionBox.y < evidenceBox.y && evidenceBox.y < traceBox.y).toBeTruthy();
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

  const decision = page.getByRole("region", { name: "Recommended action" });
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
