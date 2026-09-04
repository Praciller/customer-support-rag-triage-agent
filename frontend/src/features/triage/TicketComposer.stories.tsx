import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";

import { TicketComposer } from "./TicketComposer";

const meta = {
  title: "ResolveOps/Triage/TicketComposer",
  component: TicketComposer,
  parameters: { layout: "padded" },
  args: {
    message: "My card has still not arrived and I need help before I travel tomorrow.",
    setMessage: fn(),
    run: fn(),
    loading: false,
    error: "",
  },
} satisfies Meta<typeof TicketComposer>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Loading: Story = {
  args: { loading: true },
};

export const Error: Story = {
  args: { error: "The triage service is unavailable. Review the message and try again." },
};
