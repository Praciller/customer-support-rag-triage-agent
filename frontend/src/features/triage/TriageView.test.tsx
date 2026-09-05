import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { makeTriageResult } from "../../test/fixtures";
import { TriageView } from "./TriageView";

function renderTriage(result: ReturnType<typeof makeTriageResult> | null = makeTriageResult()) {
  return render(
    <TriageView
      message="My card has still not arrived and I need help."
      setMessage={vi.fn()}
      run={vi.fn()}
      loading={false}
      result={result}
      error=""
    />,
  );
}

describe("TriageView", () => {
  it("renders the triage decision, evidence, and complete trace", () => {
    renderTriage();

    expect(screen.getByRole("textbox", { name: /customer message/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /run triage/i })).toBeEnabled();
    expect(screen.getByText("My card has not arrived.")).toBeInTheDocument();
    expect(screen.getByText("delivery issue", { selector: "strong" })).toBeInTheDocument();
    expect(screen.getByText(/medium/i)).toBeInTheDocument();
    expect(screen.getByText(/ask for order id/i)).toBeInTheDocument();
    expect(screen.getByText(/86% grounded/i)).toBeInTheDocument();
    expect(screen.getByText(/citations checked/i)).toBeInTheDocument();
    expect(screen.getByText("Where is the card I ordered?")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /seven-node execution trace/i })).toBeInTheDocument();
    expect(screen.getByText(/7\. suggest next action/i)).toBeInTheDocument();
  });

  it("makes the human decision the primary workspace and subordinates technical metadata", () => {
    const { container } = renderTriage();

    const decision = screen.getByRole("region", { name: /recommended action/i });
    expect(decision).toHaveTextContent(/ask for order id/i);
    expect(decision).toHaveTextContent(/suggested response/i);
    expect(decision).toHaveTextContent(/86% grounded/i);
    expect(decision).toHaveTextContent(/medium/i);
    expect(screen.getByRole("group", { name: /technical details/i })).toBeInTheDocument();
    expect(container.querySelector(".technical-details")).toBeInTheDocument();
    expect(container.querySelector(".inline-trace")?.compareDocumentPosition(container.querySelector(".technical-details")!)).toBe(Node.DOCUMENT_POSITION_FOLLOWING);
  });

  it("keeps the empty state purposeful without inventing a decision", () => {
    renderTriage(null);

    expect(screen.getByText(/run triage to generate a recommended action and evidence/i)).toBeInTheDocument();
    expect(screen.queryByText(/ask for order id/i)).not.toBeInTheDocument();
  });

  it("provides a keyboard-operable technical details disclosure", () => {
    const { container } = renderTriage();
    const details = container.querySelector(".technical-details")!;
    expect(details).not.toHaveAttribute("open");
    fireEvent.click(screen.getByText("Technical details", { selector: "summary" }));
    expect(details).toHaveAttribute("open");
    expect(details.querySelector("code")).toHaveTextContent("mock / mock-small");
  });

  it("does not duplicate technical metadata as badges", () => {
    const { container } = renderTriage();

    expect(container.querySelectorAll(".technical-details .metadata .badge")).toHaveLength(0);
  });

  it("shows semantic escalation text and the escalation reason", () => {
    renderTriage({
      ...makeTriageResult(),
      escalate: true,
      escalation_reason: "The customer reports a potentially compromised card.",
    });

    expect(screen.getByText("Escalate")).toBeInTheDocument();
    expect(screen.getByText("The customer reports a potentially compromised card.")).toBeInTheDocument();
  });

  it("makes an ungrounded result and manual review action explicit", () => {
    renderTriage({
      ...makeTriageResult(),
      grounded: false,
      grounding_score: 0.2,
      next_action: "manual_review",
    });

    expect(screen.getByText(/not grounded/i)).toBeInTheDocument();
    expect(screen.getByText("manual review", { selector: "strong" })).toBeInTheDocument();
    const groundingStatus = screen.getByLabelText("Grounding status: not grounded");
    expect(groundingStatus).toBeInTheDocument();
    expect(groundingStatus.querySelector("svg")?.getAttribute("data-lucide")).not.toBe("circle-check");
    expect(screen.getByText("Manual review")).toBeInTheDocument();
  });

  it("shows each technical detail once and only conditional runtime flags", () => {
    const { container } = renderTriage({ ...makeTriageResult(), fallback_used: true, degraded_mode: true });
    fireEvent.click(screen.getByText("Technical details", { selector: "summary" }));
    const details = container.querySelector(".technical-details")!;
    expect(details.querySelectorAll("code")).toHaveLength(4);
    expect(Array.from(details.querySelectorAll("code")).filter((node) => node.textContent === "mock / mock-small")).toHaveLength(1);
    expect(Array.from(details.querySelectorAll("code")).filter((node) => node.textContent === "fresh")).toHaveLength(1);
    expect(Array.from(details.querySelectorAll("code")).filter((node) => node.textContent === "18.4 ms total")).toHaveLength(1);
    expect(Array.from(details.querySelectorAll("code")).filter((node) => node.textContent === "My card has not arrived.")).toHaveLength(1);
    expect(screen.getByText("provider fallback")).toBeInTheDocument();
    expect(screen.getByText("degraded")).toBeInTheDocument();
  });

  it("keeps degraded fallback review instructions visible", () => {
    renderTriage({
      ...makeTriageResult(),
      degraded_mode: true,
      grounded: false,
      next_action: "manual_review",
    });

    expect(screen.getByText(/degraded/i)).toBeInTheDocument();
    expect(screen.getByText(/review retrieved evidence and respond manually/i)).toBeInTheDocument();
  });
});
