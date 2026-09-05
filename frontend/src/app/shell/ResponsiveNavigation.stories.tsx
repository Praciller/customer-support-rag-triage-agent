import type { Meta, StoryObj } from "@storybook/react-vite";
import { within } from "@testing-library/react";
import { useState } from "react";
import { ResponsiveNavigation } from "./ResponsiveNavigation";
import { Sidebar } from "./Sidebar";
import type { View } from "../navigation";

function ResponsiveCatalog({ initial = "triage" as View }: { initial?: View }) {
  const [view, setView] = useState(initial);
  return <ResponsiveNavigation view={view} setView={setView} apiStatus="connected" />;
}

function DesktopCatalog({ initial = "triage" as View }: { initial?: View }) {
  const [view, setView] = useState(initial);
  return <div style={{ minHeight: "100vh", width: 232 }}><Sidebar view={view} setView={setView} /></div>;
}

const mobile = { viewport: { options: { mobile: { name: "Mobile 390", styles: { width: "390px", height: "844px" } } }, defaultViewport: "mobile" } };
const meta = { title: "ResolveOps/Shell/Navigation", component: ResponsiveCatalog, parameters: { layout: "fullscreen" } } satisfies Meta<typeof ResponsiveCatalog>;
export default meta;
type Story = StoryObj<typeof meta>;

export const DesktopNavigation: Story = { render: (args) => <DesktopCatalog {...args} />, args: { initial: "triage" } };
export const DesktopSecondaryCurrent: Story = { render: (args) => <DesktopCatalog {...args} />, args: { initial: "overview" } };
export const ResponsiveMobile: Story = { args: {}, parameters: mobile };
export const ResponsiveMobileEvaluation: Story = { args: { initial: "evaluation" }, parameters: mobile };
export const ResponsiveMobileSecondaryCurrent: Story = { args: { initial: "overview" }, parameters: mobile };
export const ResponsiveMobileMoreOpen: Story = {
  args: {}, parameters: mobile,
  play: async ({ canvas, userEvent, expect }) => {
    const body = within(canvas.getByRole("navigation", { name: "Primary workflow navigation" }).ownerDocument.body);
    const more = canvas.getByRole("button", { name: "More" });
    await userEvent.click(more);
    await expect(body.getByRole("menu")).toBeVisible();
    for (const label of ["Overview", "Semantic search", "Dataset explorer", "Provider status"]) await expect(body.getByRole("menuitem", { name: label })).toBeVisible();
    await userEvent.click(body.getByRole("menuitem", { name: "Overview" }));
    await expect(more).toHaveAttribute("data-current-secondary", "true");
    await userEvent.click(more);
    await expect(body.getByRole("menuitem", { name: "Overview" })).toHaveAttribute("data-current", "true");
    await expect(body.getByRole("menuitem", { name: "Overview" }).querySelector("[aria-current='page']")).toBeTruthy();
    await more.focus();
    await userEvent.keyboard("{Enter}{ArrowDown}{ArrowUp}{Escape}");
    await expect(body.getByRole("menu")).toBeHidden();
    await expect(more).toBeFocused();
  },
};
