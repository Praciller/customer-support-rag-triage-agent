import type { Meta, StoryObj } from "@storybook/react-vite";
import { makeTriageResult } from "../../test/fixtures";
import { DecisionWorkspace } from "./DecisionWorkspace";

const meta = { title: "ResolveOps/Triage/DecisionWorkspace", component: DecisionWorkspace, parameters: { layout: "padded" } } satisfies Meta<typeof DecisionWorkspace>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Empty: Story = { args: { result: null } };
export const Grounded: Story = { args: { result: makeTriageResult() } };
export const Escalated: Story = { args: { result: makeTriageResult({ escalate: true, urgency: "high", escalation_reason: "The customer reports a potentially compromised card." }) } };
export const UngroundedManualReview: Story = { args: { result: makeTriageResult({ grounded: false, grounding_score: 0.2, next_action: "manual_review", unsupported_claims: ["Evidence is insufficient."] }) } };

