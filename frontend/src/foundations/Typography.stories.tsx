import type { Meta, StoryObj } from "@storybook/react-vite";

const meta = { title: "Foundations/Typography", parameters: { layout: "padded" } } satisfies Meta;
export default meta;
type Story = StoryObj<typeof meta>;

export const Roles: Story = {
  render: () => (
    <div style={{ display: "grid", gap: 16, maxWidth: 720 }}>
      <div><div className="type-eyebrow">Page title</div><h1 className="type-page-title">ResolveOps workspace</h1></div>
      <div><div className="type-eyebrow">Section title</div><h2 className="type-section-title">Recommended action</h2></div>
      <p className="type-primary-decision">Ask for the order ID before offering a refund.</p>
      <p className="type-body">A readable body role keeps the customer request and the human decision easy to scan under pressure.</p>
      <button className="button button-primary type-control">Run triage</button>
      <p className="type-metadata">Mock provider · deterministic-small · cached result</p>
      <p className="type-technical">trace-06 · 152.08 ms · score 0.86 · 1,024 records</p>
    </div>
  ),
};
