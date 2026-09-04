import type { Meta, StoryObj } from "@storybook/react-vite";

import { makeTriageResult } from "../../test/fixtures";
import { TraceList } from "./TraceList";

const meta = {
  title: "ResolveOps/Trace/TraceList",
  component: TraceList,
  parameters: { layout: "padded" },
} satisfies Meta<typeof TraceList>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Normal: Story = {
  args: { trace: makeTriageResult().trace },
};

export const Fallback: Story = {
  args: {
    trace: makeTriageResult().trace.map((step, index) =>
      index === 4
        ? { ...step, fallback: true, output_summary: "Provider fallback selected; review evidence before responding." }
        : step,
    ),
  },
};

export const Degraded: Story = {
  args: {
    trace: makeTriageResult().trace.map((step, index) =>
      index === 5
        ? { ...step, degraded_mode: true, output_summary: "Grounding check degraded; manual review is required." }
        : step,
    ),
  },
};

export const Empty: Story = {
  args: { trace: [] },
};
