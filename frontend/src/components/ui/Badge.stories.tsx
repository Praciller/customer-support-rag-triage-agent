import type { Meta, StoryObj } from "@storybook/react-vite";

import { Badge } from "./Badge";

const meta = {
  title: "ResolveOps/UI/Badge",
  component: Badge,
  parameters: { layout: "centered" },
} satisfies Meta<typeof Badge>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Neutral: Story = { args: { children: "Fresh" } };
export const Success: Story = { args: { children: "86% grounded", tone: "success" } };
export const Warning: Story = { args: { children: "Provider fallback", tone: "warning" } };
export const Danger: Story = { args: { children: "Not grounded", tone: "danger" } };
