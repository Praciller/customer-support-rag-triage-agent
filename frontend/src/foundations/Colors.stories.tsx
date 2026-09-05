import type { Meta, StoryObj } from "@storybook/react-vite";

const meta = { title: "Foundations/Colors", parameters: { layout: "padded" } } satisfies Meta;
export default meta;
type Story = StoryObj<typeof meta>;

export const SemanticPalette: Story = {
  render: () => (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 12 }}>
      {(["canvas", "surface", "surface-muted", "primary", "success", "warning", "danger", "technical-surface", "selected"] as const).map((name) => (
        <div key={name} style={{ background: `var(--color-${name})`, border: "1px solid var(--color-border)", padding: 16, borderRadius: "var(--radius-sm)" }}>{name}</div>
      ))}
    </div>
  ),
};
