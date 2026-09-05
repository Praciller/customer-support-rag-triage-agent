import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { Badge } from "./Badge";
import { Button } from "./Button";
import { EmptyState } from "./EmptyState";
import { ErrorNotice } from "./ErrorNotice";
import { Field } from "./Field";
import { Panel } from "./Panel";
import { StatusIndicator } from "./StatusIndicator";

describe("semantic UI components", () => {
  it("renders primary and secondary buttons with disabled loading semantics", () => {
    render(
      <>
        <Button>Run triage</Button>
        <Button variant="secondary">Cancel</Button>
        <Button disabled>Disabled</Button>
        <Button loading>Save changes</Button>
      </>,
    );

    expect(screen.getByRole("button", { name: "Run triage" })).toHaveClass("button-primary");
    expect(screen.getByRole("button", { name: "Cancel" })).toHaveClass("button-secondary");
    expect(screen.getByRole("button", { name: "Disabled" })).toBeDisabled();
    expect(screen.getByRole("button", { name: /save changes/i })).toBeDisabled();
    expect(screen.getByRole("button", { name: /save changes/i })).toHaveTextContent("Save changes");
  });

  it("preserves button press, keyboard, and class composition semantics", async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();
    render(<Button className="custom-action" onClick={onClick}>Review decision</Button>);
    const button = screen.getByRole("button", { name: "Review decision" });
    expect(button).toHaveClass("button-primary", "custom-action");
    await user.click(button);
    expect(onClick).toHaveBeenCalledTimes(1);
    button.focus();
    await user.keyboard("[Enter]");
    expect(onClick).toHaveBeenCalledTimes(2);
  });

  it.each(["neutral", "success", "warning", "danger"] as const)(
    "renders %s status with visible meaning",
    (tone) => {
      render(<StatusIndicator label={`${tone} state`} tone={tone} />);

      const status = screen.getByRole("status");
      expect(status).toHaveTextContent(`${tone} state`);
      expect(status).toHaveAttribute("data-tone", tone);
    },
  );

  it("renders a badge with visible children and semantic tone", () => {
    render(<Badge tone="warning">Needs review</Badge>);

    expect(screen.getByText("Needs review")).toHaveClass("badge-warning");
  });

  it("associates field labels and descriptions with the control", () => {
    render(
      <Field id="customer-message" label="Customer message" helperText="Keep the message under 2,000 characters." error="Message needs review.">
        <textarea />
      </Field>,
    );

    const control = screen.getByRole("textbox", { name: "Customer message" });
    expect(control).toHaveAttribute("id", "customer-message");
    expect(control).toHaveAttribute("aria-describedby", "customer-message-help customer-message-error");
    expect(control).toHaveAttribute("aria-invalid", "true");
    expect(screen.getByText("Message needs review.")).toHaveAttribute("id", "customer-message-error");
  });

  it("provides a coherent panel wrapper without inventing a heading", () => {
    render(<Panel aria-label="Decision panel"><p>Decision content</p></Panel>);

    expect(screen.getByRole("region", { name: "Decision panel" })).toHaveClass("panel");
    expect(screen.queryByRole("heading")).not.toBeInTheDocument();
  });

  it("explains an empty state", () => {
    render(<EmptyState description="Run triage to inspect the workflow." />);

    expect(screen.getByText("Run triage to inspect the workflow.")).toBeInTheDocument();
  });

  it("renders controlled errors as alerts", () => {
    render(<ErrorNotice message="Evaluation artifacts are unavailable." />);

    expect(screen.getByRole("alert")).toHaveTextContent("Evaluation artifacts are unavailable.");
  });
});
