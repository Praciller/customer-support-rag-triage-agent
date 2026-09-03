import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import { api } from "./api";
import { makeEvaluation, makeTriageResult } from "./test/fixtures";

vi.mock("./api", () => ({
  api: {
    health: vi.fn(),
    triage: vi.fn(),
    search: vi.fn(),
    evaluation: vi.fn(),
    providers: vi.fn(),
    dataset: vi.fn(),
  },
}));

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(api.health).mockResolvedValue({ status: "ok" });
});

describe("App", () => {
  it("renders the support triage workspace", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: /ticket triage/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /run triage/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /overview/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /dataset explorer/i })).toBeInTheDocument();
  });

  it("labels deterministic demo mode and loads a fraud example", () => {
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: /suspicious transaction/i }));

    expect(screen.getByText(/deterministic demo/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/customer message/i)).toHaveValue(
      "A cash withdrawal was made from my account, but I did not make it. This is urgent.",
    );
  });

  it("shows an unavailable API state when the health check fails", async () => {
    vi.mocked(api.health).mockRejectedValue(new Error("offline"));

    render(<App />);

    expect(await screen.findByText(/api unavailable/i)).toBeInTheDocument();
  });

  it("gives semantic search controls accessible names", () => {
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: /semantic search/i }));

    expect(screen.getByRole("textbox", { name: /search support tickets/i })).toBeInTheDocument();
    expect(screen.getByRole("combobox", { name: /intent filter/i })).toBeInTheDocument();
  });

  it("renders a complete triage decision and seven-node trace", async () => {
    vi.mocked(api.triage).mockResolvedValue(makeTriageResult());
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: /run triage/i }));

    expect(await screen.findByText("My card has not arrived.")).toBeInTheDocument();
    expect(screen.getByText(/18\.4 ms total/i)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /seven-node execution trace/i })).toBeInTheDocument();
    expect(screen.getByText(/7\. suggest next action/i)).toBeInTheDocument();
  });

  it("renders measured evaluation methodology and per-class results", async () => {
    vi.mocked(api.evaluation).mockResolvedValue(makeEvaluation());
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: /^evaluation$/i }));

    expect(await screen.findByText(/deterministic mock/i)).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: /precision/i })).toBeInTheDocument();
    expect(screen.getByText(/small deterministic fixture/i)).toBeInTheDocument();
  });
});
