import type { Meta, StoryObj } from "@storybook/react-vite";

const meta = { title: "Foundations/Spacing", parameters: { layout: "padded" } } satisfies Meta;
export default meta;
type Story = StoryObj<typeof meta>;

export const Scale: Story = {
  render: () => (
    <div style={{ display: "grid", gap: 12, maxWidth: 560 }}>
      {[1, 2, 3, 4, 5, 6, 7].map((step) => <div key={step} style={{ display: "flex", alignItems: "center", gap: 12 }}><code className="type-technical">space-{step}</code><div style={{ width: `var(--space-${step})`, height: 16, background: "var(--color-primary)" }} /></div>)}
    </div>
  ),
};
