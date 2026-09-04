import type { Meta, StoryObj } from "@storybook/react-vite";

import { makeTriageResult } from "../../test/fixtures";
import { CaseList } from "./CaseList";

const meta = {
  title: "ResolveOps/Evidence/CaseList",
  component: CaseList,
  parameters: { layout: "padded" },
} satisfies Meta<typeof CaseList>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Populated: Story = {
  args: { cases: makeTriageResult().retrieved_cases },
};

export const Empty: Story = {
  args: { cases: [] },
};
