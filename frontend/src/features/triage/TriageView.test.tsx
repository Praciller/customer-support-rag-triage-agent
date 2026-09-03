import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { makeTriageResult } from "../../test/fixtures";
import { TriageView } from "./TriageView";

function renderTriage(result = makeTriageResult()) {
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

  it("preserves the original triage metadata badge order", () => {
    const { container } = renderTriage();

    const metadata = Array.from(container.querySelectorAll(".metadata .badge")).map((node) =>
      node.textContent?.trim(),
    );

    expect(metadata).toEqual([
      "mock / mock-small",
      "86% grounded",
      "fresh",
      "18.4 ms total",
      "citations checked",
    ]);
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
});
