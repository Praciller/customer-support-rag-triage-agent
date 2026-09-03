import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { makeTriageResult } from "../../test/fixtures";
import { TraceView } from "./TraceView";

describe("TraceView", () => {
  it("preserves the empty state before a triage run", () => {
    render(<TraceView trace={[]} />);

    expect(screen.getByText(/run triage to inspect the workflow/i)).toBeInTheDocument();
  });

  it("renders the deterministic seven-node trace in order", () => {
    render(<TraceView trace={makeTriageResult().trace} />);

    const steps = screen.getAllByRole("listitem");
    expect(steps).toHaveLength(7);
    expect(steps[0]).toHaveTextContent(/1\. normalize message/i);
    expect(steps[6]).toHaveTextContent(/7\. suggest next action/i);
    expect(steps[3]).toHaveTextContent(/1 ms/i);
  });
});
