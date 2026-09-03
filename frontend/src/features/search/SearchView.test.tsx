import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "../../api";
import { SearchView } from "./SearchView";

vi.mock("../../api", () => ({
  api: {
    search: vi.fn(),
  },
}));

beforeEach(() => {
  vi.clearAllMocks();
});

describe("SearchView", () => {
  it("keeps accessible search controls and the existing request contract", async () => {
    vi.mocked(api.search).mockResolvedValue([
      {
        ticket_id: "demo-delivery",
        message: "Where is the card I ordered?",
        intent: "delivery_issue",
        response: "",
        source: "mteb/banking77",
        score: 0.91,
        metadata: {},
      },
    ]);
    render(<SearchView />);

    expect(screen.getByRole("textbox", { name: "Search support tickets" })).toBeInTheDocument();
    expect(screen.getByRole("combobox", { name: "Intent filter" })).toBeInTheDocument();

    fireEvent.change(screen.getByRole("textbox", { name: "Search support tickets" }), {
      target: { value: "late card" },
    });
    fireEvent.change(screen.getByRole("combobox", { name: "Intent filter" }), {
      target: { value: "delivery_issue" },
    });
    fireEvent.click(screen.getByRole("button", { name: /^search$/i }));

    expect(api.search).toHaveBeenCalledWith("late card", 5, "delivery_issue");
    expect(await screen.findByText("Where is the card I ordered?")).toBeInTheDocument();
  });
});
