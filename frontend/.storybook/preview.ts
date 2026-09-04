import type { Preview } from "@storybook/react-vite";

import "../src/styles/tokens.css";
import "../src/styles/base.css";
import "../src/styles/components.css";
import "../src/styles/features.css";

const preview: Preview = {
  parameters: {
    backgrounds: {
      default: "light",
      values: [{ name: "light", value: "var(--color-canvas)" }],
    },
  },
};

export default preview;
