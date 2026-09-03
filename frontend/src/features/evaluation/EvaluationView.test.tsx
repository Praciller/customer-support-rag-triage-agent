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
  it("preserves deterministic methodology, precision, and limitations", async () => {
    vi.mocked(api.evaluation).mockResolvedValue(makeEvaluation());
    render(<EvaluationView />);

    expect(await screen.findByText(/deterministic mock/i)).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: /precision/i })).toBeInTheDocument();
    expect(screen.getByText(/small deterministic fixture/i)).toBeInTheDocument();
  });
});
