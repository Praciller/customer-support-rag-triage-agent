import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, fn } from "storybook/test";

import { Button } from "./Button";

const meta = {
  title: "ResolveOps/UI/Button",
  component: Button,
  parameters: { layout: "centered" },
  args: { children: "Run triage", onClick: fn() },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {};

export const Secondary: Story = {
  args: { variant: "secondary" },
};

export const Disabled: Story = {
  args: { disabled: true },
};

export const Loading: Story = {
  args: { loading: true },
};

export const LongLabel: Story = {
  args: { children: "Request manual review for this customer decision" },
};

export const KeyboardFocus: Story = {
  parameters: { pseudo: { focusVisible: true } },
  play: async ({ canvas, userEvent }) => {
    await userEvent.tab();
    await expect(canvas.getByRole("button", { name: /run triage/i })).toHaveFocus();
  },
};

const clickable = fn();

export const Clickable: Story = {
  args: { onClick: clickable },
  play: async ({ args, canvas, userEvent }) => {
    await userEvent.click(canvas.getByRole("button", { name: /run triage/i }));
    await expect(args.onClick).toHaveBeenCalledOnce();
  },
};
