import type { Meta, StoryObj } from "@storybook/react-vite";

import { ErrorNotice } from "./ErrorNotice";

const meta = {
  title: "ResolveOps/UI/ErrorNotice",
  component: ErrorNotice,
  parameters: { layout: "centered" },
} satisfies Meta<typeof ErrorNotice>;

export default meta;
type Story = StoryObj<typeof meta>;

export const ApiUnavailable: Story = {
  args: { message: "The API is unavailable. Review the request and try again." },
};
