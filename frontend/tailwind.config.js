/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "var(--color-canvas)",
        foreground: "var(--color-foreground)",
        primary: {
          DEFAULT: "var(--color-primary)",
          foreground: "var(--color-primary-foreground)",
        },
        secondary: {
          DEFAULT: "var(--color-surface-muted)",
          foreground: "var(--color-foreground)",
        },
        muted: {
          DEFAULT: "var(--color-surface-muted)",
          foreground: "var(--color-foreground-muted)",
        },
        border: "var(--color-border)",
        input: "var(--color-border)",
        ring: "var(--color-focus)",
        destructive: {
          DEFAULT: "var(--color-danger)",
          foreground: "var(--color-surface)",
        },
      },
      fontFamily: {
        sans: ["Geist Variable", "Geist", "Segoe UI", "sans-serif"],
        mono: ["Geist Mono Variable", "Geist Mono", "Consolas", "monospace"],
      },
    },
  },
  plugins: [],
};
