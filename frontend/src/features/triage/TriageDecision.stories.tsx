import type { Meta, StoryObj } from "@storybook/react-vite";

import { makeTriageResult } from "../../test/fixtures";
import { TriageDecision } from "./TriageDecision";

const meta = {
  title: "ResolveOps/Triage/TriageDecision",
  component: TriageDecision,
  parameters: { layout: "padded" },
} satisfies Meta<typeof TriageDecision>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Standard: Story = {
  args: { result: makeTriageResult() },
};

export const Escalated: Story = {
  args: {
    result: makeTriageResult({
      escalate: true,
      urgency: "high",
      escalation_reason: "Urgent account-protection review required.",
    }),
  },
};

export const Ungrounded: Story = {
  args: {
    result: makeTriageResult({
      grounded: false,
      grounding_score: 0.2,
      next_action: "manual_review",
      unsupported_claims: ["Evidence is insufficient."],
    }),
  },
};

export const Degraded: Story = {
  args: {
    result: makeTriageResult({ degraded_mode: true, grounded: false, next_action: "manual_review" }),
  },
};

export const Fallback: Story = {
  args: { result: makeTriageResult({ fallback_used: true }) },
};

export const Cached: Story = {
  args: { result: makeTriageResult({ cached: true }) },
};
