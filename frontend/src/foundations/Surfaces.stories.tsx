import type { Meta, StoryObj } from "@storybook/react-vite";

const meta = { title: "Foundations/Surfaces", parameters: { layout: "padded" } } satisfies Meta;
export default meta;
type Story = StoryObj<typeof meta>;

export const Hierarchy: Story = {
  render: () => (
    <div style={{ background: "var(--color-canvas)", padding: 24, display: "grid", gap: 12 }}>
      <div style={{ padding: 16 }}>Canvas / Workspace</div>
      <div style={{ background: "var(--color-surface)", border: "2px solid var(--color-primary)", padding: 20, borderRadius: "var(--radius-md)" }}><strong>Primary decision surface</strong></div>
      <div style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)", padding: 16, borderRadius: "var(--radius-md)" }}>Standard section surface</div>
      <div style={{ background: "var(--color-surface-muted)", padding: 12, borderRadius: "var(--radius-sm)" }}>Subtle item surface</div>
      <div style={{ background: "var(--color-technical-surface)", padding: 12, fontFamily: "var(--font-code)" }}>Technical metadata surface · 152.08 ms</div>
    </div>
  ),
};
