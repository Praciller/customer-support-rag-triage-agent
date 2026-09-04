import type { Meta, StoryObj } from "@storybook/react-vite";

import { Field } from "./Field";

const meta = {
  title: "ResolveOps/UI/Field",
  component: Field,
  parameters: { layout: "centered" },
} satisfies Meta<typeof Field>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    id: "customer-email",
    label: "Customer email",
    children: <input type="email" />,
  },
};

export const WithHelperText: Story = {
  args: {
    id: "ticket-reference",
    label: "Ticket reference",
    helperText: "Use the reference supplied by the customer.",
    children: <input type="text" />,
  },
};

export const ValidationError: Story = {
  args: {
    id: "customer-email-error",
    label: "Customer email",
    error: "Enter a valid customer email.",
    children: <input type="email" />,
  },
};
