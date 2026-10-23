import type { StorybookConfig } from "@storybook/react-vite";

const config: StorybookConfig = {
  stories: ["../src/**/*.stories.@(ts|tsx)"],
  // CI uses axe-core through Playwright; avoid running two axe scans at once.
  // Keep the accessibility addon available in the normal developer Storybook.
  addons: process.env.STORYBOOK_COMPONENT_A11Y_E2E === "1" ? [] : ["@storybook/addon-a11y"],
  framework: "@storybook/react-vite",
};

export default config;
