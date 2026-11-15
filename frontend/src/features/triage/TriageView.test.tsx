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
    expect(screen.getByRole("group", { name: "Example tickets" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /run triage/i })).toBeEnabled();
    expect(screen.getByText("My card has not arrived.")).toBeInTheDocument();
    expect(screen.getByText("delivery issue", { selector: "strong" })).toBeInTheDocument();
    expect(screen.getByText(/medium/i)).toBeInTheDocument();
    expect(screen.getByText("manual review", { selector: "strong" })).toBeInTheDocument();
    expect(screen.getByLabelText("Policy review status: No approved policy")).toBeInTheDocument();
    expect(screen.getByText(/proposal 1: no approved policy/i)).toBeInTheDocument();
    expect(screen.getAllByText(/not approved policy/i).length).toBeGreaterThan(0);
    expect(screen.getByText("Where is the card I ordered?")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /seven-node execution trace/i })).toBeInTheDocument();
    expect(screen.getByText(/7\. suggest next action/i)).toBeInTheDocument();
  });

  it("makes the human decision the primary workspace and subordinates technical metadata", () => {
    const { container } = renderTriage();

    const decision = screen.getByRole("region", { name: /recommended action/i });
    expect(decision).toHaveTextContent(/manual review/i);
    expect(decision).toHaveTextContent(/customer response · human review required/i);
    expect(decision).toHaveTextContent(/no approved policy/i);
    expect(decision).toHaveTextContent(/medium/i);
    expect(screen.getByRole("group", { name: /technical details/i })).toBeInTheDocument();
    expect(container.querySelector(".technical-details")).toBeInTheDocument();
    expect(container.querySelector(".inline-trace")?.compareDocumentPosition(container.querySelector(".technical-details")!)).toBe(Node.DOCUMENT_POSITION_FOLLOWING);
  });

  it("keeps the empty state purposeful without inventing a decision", () => {
    renderTriage(null);

    expect(screen.getByText(/run triage to classify the message and find similar past cases/i)).toBeInTheDocument();
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

  it("makes missing policy and manual review explicit", () => {
    renderTriage({
      ...makeTriageResult(),
      next_action: "manual_review",
      policy_status: "no_approved_policy",
    });

    expect(screen.getByLabelText("Policy review status: No approved policy")).toBeInTheDocument();
    expect(screen.getByText("manual review", { selector: "strong" })).toBeInTheDocument();
    const policyStatus = screen.getByLabelText("Policy review status: No approved policy");
    expect(policyStatus).toBeInTheDocument();
    expect(policyStatus.querySelector("svg")?.getAttribute("data-lucide")).not.toBe("circle-check");
    expect(screen.getByText("Manual review")).toBeInTheDocument();
  });

  it("shows the policy and check result for each allowed proposal", () => {
    renderTriage({
      ...makeTriageResult(),
      policy_status: "verified",
      next_action: "reply_to_customer",
      policy_references: ["synthetic-test-policy-card-17"],
      proposal_checks: [{
        proposal_id: "proposal-1",
        status: "supported",
        policy_references: ["synthetic-test-policy-card-17"],
        verification_result: "passed",
        verification_method: "synthetic_test_verifier",
      }],
      verified_proposals: [{
        proposal_id: "proposal-1",
        text: "Synthetic test proposal: check the delivery tracking page.",
        policy_references: ["synthetic-test-policy-card-17"],
        verification_result: "passed",
        verification_method: "synthetic_test_verifier",
      }],
      suggested_response: "Synthetic test proposal: check the delivery tracking page.",
    });

    expect(screen.getByRole("heading", { name: "Proposals with passing policy checks" })).toBeInTheDocument();
    expect(screen.getByText(/synthetic-test-policy-card-17.*verification: passed/i)).toBeInTheDocument();
    expect(screen.getAllByText("Synthetic test proposal: check the delivery tracking page.")).toHaveLength(2);
    expect(screen.queryByText(/grounded|confidence/i)).not.toBeInTheDocument();
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
      next_action: "manual_review",
    });

    expect(screen.getByText("degraded", { selector: ".badge" })).toBeInTheDocument();
    expect(screen.getByText(/review the triage and decide manually/i)).toBeInTheDocument();
  });
});
