import type { Meta, StoryObj } from "@storybook/react-vite";
import { useState } from "react";
import { ResponsiveNavigation } from "./ResponsiveNavigation";
import type { View } from "../navigation";

function Catalog({ initial = "triage" as View }: { initial?: View }) {
  const [view, setView] = useState(initial);
  return <ResponsiveNavigation view={view} setView={setView} apiStatus="connected" />;
}

const meta = { title: "ResolveOps/Shell/ResponsiveNavigation", component: Catalog, parameters: { layout: "fullscreen" } } satisfies Meta<typeof Catalog>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Mobile: Story = { args: {} };
export const MobileEvaluation: Story = { args: { initial: "evaluation" } };
export const ResponsiveMobile: Story = { args: {} };
export const ResponsiveMobileSecondaryCurrent: Story = { args: { initial: "overview" } };
export const ResponsiveMobileMoreOpen: Story = { args: {}, play: async ({ canvas, userEvent }) => { await userEvent.click(canvas.getByRole("button", { name: "More" })); await canvas.getByRole("menuitem", { name: "Overview" }); } };
export const DesktopNavigation: Story = { args: { initial: "triage" } };
