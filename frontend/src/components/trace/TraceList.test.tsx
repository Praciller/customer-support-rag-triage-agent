import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { makeTriageResult } from "../../test/fixtures";
import { TraceList } from "./TraceList";

describe("TraceList", () => {
  it("renders the ordered seven-node trace and bounded runtime metadata", () => {
    render(<TraceList trace={makeTriageResult().trace} />);

    expect(screen.getAllByRole("listitem")).toHaveLength(7);
    expect(screen.getByText(/1\. normalize message/i)).toBeInTheDocument();
    expect(screen.getByText(/7\. suggest next action/i)).toBeInTheDocument();
    expect(screen.getAllByText("local")).toHaveLength(7);
    expect(screen.getAllByText("1 ms")).toHaveLength(7);
  });

  it("explains when no workflow trace is available", () => {
    render(<TraceList trace={[]} />);

    expect(screen.getByText("Run triage to inspect the workflow.")).toBeInTheDocument();
  });

  it("keeps provider, cache, fallback, and degraded trace metadata visible", () => {
    const trace = makeTriageResult().trace.map((step, index) =>
      index === 0
        ? { ...step, provider: "mock", model: "mock-small", cache_hit: true, fallback: true, degraded_mode: true }
        : step,
    );
    render(<TraceList trace={trace} />);

    expect(screen.getAllByText("mock / mock-small")).toHaveLength(2);
    expect(screen.getByText("cache hit")).toBeInTheDocument();
    expect(screen.getByText("fallback")).toBeInTheDocument();
    expect(screen.getByText("degraded")).toBeInTheDocument();
  });
});
