import type { Meta, StoryObj } from "@storybook/react-vite";

import { makeEvaluation } from "../../test/fixtures";
import EvaluationChart from "./EvaluationChart";

function EvaluationChartCatalog() {
  const evaluation = makeEvaluation();
  const chartData = [
    { metric: "Precision", value: (evaluation.retrieval_precision_at_k ?? 0) * 100 },
    { metric: "Intent", value: (evaluation.intent_accuracy ?? 0) * 100 },
    { metric: "Urgency", value: (evaluation.urgency_accuracy ?? 0) * 100 },
    { metric: "Grounded", value: (evaluation.groundedness_pass_rate ?? 0) * 100 },
  ];

  return (
    <div>
      <EvaluationChart data={chartData} />
      <p>
        Deterministic fixture summary: Precision@5 80%, intent 88%, urgency 100%, grounded 100%.
        Small deterministic fixture; not a production SLA.
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
