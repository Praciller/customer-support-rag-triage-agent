import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { makeTriageResult } from "../../test/fixtures";
import { TraceList } from "./TraceList";

describe("TraceList", () => {
  it("renders a compact, ordered seven-node workflow with outcome and latency", () => {
    render(<TraceList trace={makeTriageResult().trace} />);

    const steps = within(screen.getByRole("list", { name: "Workflow execution steps" })).getAllByRole("listitem");
    expect(steps).toHaveLength(7);
    expect(steps[0]).toHaveTextContent(/1\. normalize message/i);
    expect(steps[6]).toHaveTextContent(/7\. suggest next action/i);
    expect(steps[3]).toHaveTextContent("bounded output");
    expect(steps[3]).toHaveTextContent("1 ms");
    expect(steps[0]).toHaveTextContent("local");
  });

  it("explains when no workflow trace is available", () => {
    render(<TraceList trace={[]} />);
    expect(screen.getByText("Run triage to inspect the workflow.")).toBeInTheDocument();
  });

  it("keeps runtime state available without repeating multiple badges", () => {
    const trace = makeTriageResult().trace.map((step, index) =>
      index === 0
        ? { ...step, provider: "mock", model: "mock-small", cache_hit: true, fallback: true, degraded_mode: true }
        : step,
    );
    render(<TraceList trace={trace} />);

    const first = screen.getAllByRole("listitem")[0];
    expect(first).toHaveTextContent("mock / mock-small");
    expect(first).toHaveTextContent("cache hit");
    expect(first).toHaveTextContent("fallback");
    expect(first).toHaveTextContent("degraded");
    expect(first.querySelectorAll(".badge")).toHaveLength(0);
    fireEvent.click(within(first).getByText(/technical details for normalize message/i));
    expect(within(first).getByText("Input summary")).toBeInTheDocument();
    expect(within(first).getByText("Evidence references")).toBeInTheDocument();
    expect(within(first).getByText("Degraded")).toBeInTheDocument();
  });

  it("shows non-completed status as text, not color alone", () => {
    const trace = makeTriageResult().trace.map((step, index) =>
      index === 4 ? { ...step, status: "failed", error_category: "ProviderError" } : step,
    );
    render(<TraceList trace={trace} />);
    const row = screen.getAllByRole("listitem")[4];
    expect(row).toHaveTextContent("failed");
    fireEvent.click(within(row).getByText(/technical details for generate support response/i));
    expect(within(row).getByText("ProviderError")).toBeInTheDocument();
  });
});
