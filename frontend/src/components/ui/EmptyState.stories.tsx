import type { Meta, StoryObj } from "@storybook/react-vite";

import { Button } from "./Button";
import { EmptyState } from "./EmptyState";

const meta = {
  title: "ResolveOps/UI/EmptyState",
  component: EmptyState,
  parameters: { layout: "centered" },
} satisfies Meta<typeof EmptyState>;

export default meta;
type Story = StoryObj<typeof meta>;

export const NoMatchingCases: Story = {
  args: {
    title: "No evidence found",
    description: "No matching indexed cases yet. Run triage to retrieve bounded precedent.",
    action: <Button variant="secondary">Run triage</Button>,
  },
};
