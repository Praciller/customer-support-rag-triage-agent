import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { SimilarCase } from "../../types/api";
import { CaseList } from "./CaseList";

const exampleCase: SimilarCase = {
  ticket_id: "demo-delivery",
  message: "Where is the card I ordered?",
  intent: "delivery_issue",
  response: "",
  source: "mteb/banking77",
  score: 0.91,
  metadata: {},
};

describe("CaseList", () => {
  it("renders evidence identity, intent, score, and message", () => {
    render(<CaseList cases={[exampleCase]} />);

    expect(screen.getByText("delivery issue")).toBeInTheDocument();
    expect(screen.getByText("0.91 similarity")).toBeInTheDocument();
    expect(screen.getByText("Where is the card I ordered?")).toBeInTheDocument();
    expect(screen.getByText("Source: mteb/banking77")).toBeInTheDocument();
    expect(screen.queryByText(/bounded demo evidence/i)).not.toBeInTheDocument();
    expect(screen.getByText("demo-delivery")).toBeInTheDocument();
  });

  it("explains when no indexed evidence matches", () => {
    render(<CaseList cases={[]} />);

    expect(screen.getByText("No matching indexed cases yet.")).toBeInTheDocument();
  });
});
