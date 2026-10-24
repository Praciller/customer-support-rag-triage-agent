import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "../../lib/api";
import { makeEvaluation } from "../../test/fixtures";
import { EvaluationView } from "./EvaluationView";

vi.mock("../../lib/api", () => ({
  api: {
    evaluation: vi.fn(),
  },
}));

beforeEach(() => {
  vi.clearAllMocks();
});

describe("EvaluationView", () => {
  it("groups deterministic metrics by meaning without a repeated chart", async () => {
    vi.mocked(api.evaluation).mockResolvedValue(makeEvaluation());
    const { container } = render(<EvaluationView />);

    expect(await screen.findByRole("heading", { name: "Retrieval quality" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Workflow checks" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Runtime profile" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Intent metrics by class" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Methodology and limitations" })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: /precision/i })).toBeInTheDocument();
    expect(screen.getByText(/small deterministic fixture/i)).toBeInTheDocument();
    expect(screen.getByText(/no external llm calls/i)).toBeInTheDocument();
    expect(container.querySelector(".metric-grid")).toBeNull();
    expect(container.querySelector(".evaluation-chart")).toBeNull();
  });

  it("preserves explicit zeros and shows unavailable values as dashes", async () => {
    vi.mocked(api.evaluation).mockResolvedValue(makeEvaluation({
      retrieval_precision_at_k: 0,
      average_latency_ms: 0,
      urgency_macro_f1: undefined,
      fallback_count: 0,
    }));
    render(<EvaluationView />);
    await screen.findByRole("heading", { name: "Retrieval quality" });
    expect(screen.getByText("Precision@5").closest("div")).toHaveTextContent("0%");
    expect(screen.getByText("Average latency").closest("div")).toHaveTextContent("0 ms");
    expect(screen.getByText("Urgency macro F1").closest("div")).toHaveTextContent("--");
    expect(screen.getByText("Provider fallbacks").closest("div")).toHaveTextContent("0");
  });

  it("does not claim an external-provider run used no external calls", async () => {
    vi.mocked(api.evaluation).mockResolvedValue(makeEvaluation({ evaluation_mode: "real_provider" }));
    render(<EvaluationView />);
    expect(await screen.findByRole("heading", { name: "real provider" })).toBeInTheDocument();
    expect(screen.queryByText(/no external llm calls/i)).not.toBeInTheDocument();
    expect(screen.getByText(/inspect provider provenance/i)).toBeInTheDocument();
  });
});

  it("clearly hides stale metrics when no compatible report is available", async () => {
    vi.mocked(api.evaluation).mockResolvedValue({ status: "not_evaluated" });
    render(<EvaluationView />);
    expect(await screen.findByRole("heading", { name: "No compatible evaluation report" })).toBeInTheDocument();
    expect(screen.queryByText("Measured artifact")).not.toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Retrieval quality" })).not.toBeInTheDocument();
  });
