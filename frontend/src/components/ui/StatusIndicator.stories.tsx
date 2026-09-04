import type { Meta, StoryObj } from "@storybook/react-vite";

import { StatusIndicator } from "./StatusIndicator";

const meta = {
  title: "ResolveOps/UI/StatusIndicator",
  component: StatusIndicator,
  parameters: { layout: "centered" },
} satisfies Meta<typeof StatusIndicator>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Neutral: Story = { args: { label: "Pending review", tone: "neutral" } };
export const Success: Story = { args: { label: "Standard queue", tone: "success" } };
export const Warning: Story = { args: { label: "Review fallback", tone: "warning" } };
export const Danger: Story = { args: { label: "Escalate", tone: "danger" } };
