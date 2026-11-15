import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./app/App";
import { ApiResponseError, api } from "./lib/api";
import { makeEvaluation, makeTriageResult } from "./test/fixtures";

vi.mock("./lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("./lib/api")>();
  return {
    ...actual,
    api: {
      health: vi.fn(),
      triage: vi.fn(),
      search: vi.fn(),
      evaluation: vi.fn(),
      providers: vi.fn(),
      dataset: vi.fn(),
    },
  };
});

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(api.health).mockResolvedValue({ status: "ok" });
});

describe("App", () => {
  it("renders the support triage workspace", async () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: /ticket triage/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /run triage/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /overview/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /dataset explorer/i })).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: /main navigation/i })).toBeInTheDocument();
    expect(screen.getByText(/deterministic demo/i)).toBeInTheDocument();
    expect(await screen.findByText(/api connected/i)).toBeInTheDocument();
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

    expect((await screen.findAllByText(/api unavailable/i)).length).toBeGreaterThan(0);
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
    expect(screen.getByText(/18\.4 ms total/i, { selector: "code" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /seven-node execution trace/i })).toBeInTheDocument();
    expect(screen.getByText(/7\. suggest next action/i)).toBeInTheDocument();
  });

  it("explains cold start, times out, and waits for a manual retry", async () => {
    vi.useFakeTimers();
    try {
      vi.mocked(api.triage)
        .mockImplementationOnce((_message, _topK, signal) => new Promise((_, reject) => {
          signal?.addEventListener("abort", () => reject(new DOMException("Aborted", "AbortError")), { once: true });
        }))
        .mockRejectedValueOnce(new ApiResponseError("Request timed out", 504))
        .mockResolvedValueOnce(makeTriageResult());
      render(<App />);

      await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: "Run triage" }));
        await Promise.resolve();
      });
      expect(screen.getByText(/backend may be starting after an idle period/i)).toBeInTheDocument();
      expect(api.triage).toHaveBeenCalledTimes(1);

      await act(async () => {
        await vi.advanceTimersByTimeAsync(60_000);
      });
      expect(screen.getByRole("alert")).toHaveTextContent(/timed out after 60 seconds/i);
      expect(screen.getByRole("button", { name: "Retry triage" })).toBeInTheDocument();
      expect(api.triage).toHaveBeenCalledTimes(1);

      await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: "Retry triage" }));
        await Promise.resolve();
      });
      expect(screen.getByRole("alert")).toHaveTextContent(/backend timed out while processing triage/i);
      expect(api.triage).toHaveBeenCalledTimes(2);
      await act(async () => {
        await vi.advanceTimersByTimeAsync(5_000);
      });
      expect(api.triage).toHaveBeenCalledTimes(2);

      await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: "Retry triage" }));
        await Promise.resolve();
      });
      expect(api.triage).toHaveBeenCalledTimes(3);
      expect(screen.getByRole("heading", { name: /seven-node execution trace/i })).toBeInTheDocument();
    } finally {
      vi.useRealTimers();
    }
  });

  it("renders measured evaluation methodology and per-class results", async () => {
    vi.mocked(api.evaluation).mockResolvedValue(makeEvaluation());
    render(<App />);

    fireEvent.click(screen.getAllByRole("button", { name: /^evaluation$/i })[0]);

    expect(await screen.findByRole("heading", { name: /deterministic mock/i })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: /precision/i })).toBeInTheDocument();
    expect(screen.getByText(/small deterministic fixture/i)).toBeInTheDocument();
    expect(screen.getByText("No-approved-policy cases")).toBeInTheDocument();
    expect(screen.getByText("Proposals withheld")).toBeInTheDocument();
    expect(screen.queryByText(/grounding score|confidence score|grounded percentage/i)).not.toBeInTheDocument();
  });

  it("opens labelled secondary tools from the responsive More control", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /^more$/i }));
    expect(screen.getByRole("menu")).toBeInTheDocument();
    expect(screen.getByRole("menuitem", { name: /provider status/i })).toBeInTheDocument();
    expect(document.querySelector(".more-trigger")).toHaveAttribute("aria-expanded", "true");
  });

  it("keeps workflow navigation in the approved order", () => {
    render(<App />);
    const desktop = screen.getByRole("navigation", { name: "Main navigation" });
    expect(Array.from(desktop.querySelectorAll("button")).slice(0, 3).map((button) => button.textContent)).toEqual(["Ticket triage", "Evaluation", "Agent trace"]);
    const responsive = document.querySelector(".responsive-primary")!;
    expect(Array.from(responsive.querySelectorAll("button")).slice(0, 4).map((button) => button.textContent?.trim())).toEqual(["Triage", "Evaluation", "Trace", "More"]);
  });

  it("marks More when the current view is a secondary tool", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "More" }));
    fireEvent.click(screen.getByRole("menuitem", { name: "Overview" }));
    expect(screen.getByRole("heading", { name: "Overview" })).toBeInTheDocument();
    expect(document.querySelector(".more-trigger")).toHaveAttribute("data-current-secondary", "true");
    fireEvent.click(screen.getByRole("button", { name: "More" }));
    expect(screen.getByRole("menuitem", { name: "Overview" })).toHaveAttribute("data-current", "true");
    expect(screen.getByRole("menuitem", { name: "Overview" }).querySelector("[aria-current='page']")).toBeInTheDocument();
  });
});
