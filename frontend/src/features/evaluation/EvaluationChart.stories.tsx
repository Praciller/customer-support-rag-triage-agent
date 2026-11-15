import type { Meta, StoryObj } from "@storybook/react-vite";

import { makeEvaluation } from "../../test/fixtures";
import EvaluationChart from "./EvaluationChart";

function EvaluationChartCatalog() {
  const evaluation = makeEvaluation();
  const chartData = [
    { metric: "Precision", value: (evaluation.retrieval_precision_at_k ?? 0) * 100 },
    { metric: "Intent", value: (evaluation.intent_accuracy ?? 0) * 100 },
    { metric: "Urgency", value: (evaluation.urgency_accuracy ?? 0) * 100 },
    { metric: "Workflow trace", value: (evaluation.workflow_success_rate ?? 0) * 100 },
  ];

  return (
    <div>
      <EvaluationChart data={chartData} />
      <p>
        Deterministic fixture summary: retrieval and classification regressions are reported separately.
        The policy gate is a structural abstention check, not semantic policy validation.
      </p>
    </div>
  );
}

const meta = {
  title: "ResolveOps/Evaluation/EvaluationChart",
  component: EvaluationChartCatalog,
  parameters: { layout: "padded" },
} satisfies Meta<typeof EvaluationChartCatalog>;

export default meta;
type Story = StoryObj<typeof meta>;

export const DeterministicBaseline: Story = {};
