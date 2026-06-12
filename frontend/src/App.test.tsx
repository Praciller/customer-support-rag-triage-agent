import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import App from "./App";

describe("App", () => {
  it("renders the support triage workspace", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: /ticket triage/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /run triage/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /overview/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /dataset explorer/i })).toBeInTheDocument();
  });
});
