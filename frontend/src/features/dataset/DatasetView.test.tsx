import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "../../api";
import { DatasetView } from "./DatasetView";

vi.mock("../../api", () => ({
  api: {
    dataset: vi.fn(),
  },
}));

beforeEach(() => {
  vi.clearAllMocks();
});

describe("DatasetView", () => {
  it("renders dataset metadata returned by the existing API", async () => {
    vi.mocked(api.dataset).mockResolvedValue({
      name: "Banking77",
      license: "CC BY 4.0",
      split: "train",
      upstream_dataset: "banking77",
      records: 27,
      intents: { delivery_issue: 3 },
    });
    render(<DatasetView />);

    expect(await screen.findByText("Banking77")).toBeInTheDocument();
    expect(screen.getByText("27 records")).toBeInTheDocument();
    expect(api.dataset).toHaveBeenCalledTimes(1);
  });
});
