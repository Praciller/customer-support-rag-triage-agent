import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "../../api";
import { ProviderView } from "./ProviderView";

vi.mock("../../api", () => ({
  api: {
    providers: vi.fn(),
  },
}));

beforeEach(() => {
  vi.clearAllMocks();
});

describe("ProviderView", () => {
  it("renders provider status returned by the existing API", async () => {
    vi.mocked(api.providers).mockResolvedValue({
      inference: "mock",
      storage: "memory",
    });
    render(<ProviderView />);

    expect(await screen.findByText("inference")).toBeInTheDocument();
    expect(screen.getByText("mock")).toBeInTheDocument();
    expect(screen.getByText("memory")).toBeInTheDocument();
    expect(api.providers).toHaveBeenCalledTimes(1);
  });
});
