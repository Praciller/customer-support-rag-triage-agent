# Design System

## Theme

Light operational workspace for support agents working in normal office lighting. Restrained color strategy: cool tinted neutrals, one cobalt action color, semantic amber and red only for urgency.

## Color

- Canvas: `oklch(0.975 0.006 245)`
- Surface: `oklch(0.995 0.004 245)`
- Surface muted: `oklch(0.948 0.010 245)`
- Text: `oklch(0.245 0.025 250)`
- Text muted: `oklch(0.510 0.025 250)`
- Border: `oklch(0.875 0.018 245)`
- Accent: `oklch(0.555 0.180 258)`
- Success: `oklch(0.565 0.125 154)`
- Warning: `oklch(0.700 0.145 76)`
- Danger: `oklch(0.560 0.190 28)`

## Typography

Use `Inter`, falling back to `Segoe UI` and system sans. UI scale is compact and fixed: 12, 14, 16, 20, 26, and 34 pixels. Body copy stays below 72 characters per line.

## Layout

Desktop uses a 232-pixel side navigation and open content canvas. Primary workflows use a two-column split: input and decision on the left, evidence and trace on the right. Mobile collapses navigation into a top bar and stacks evidence below the decision.

## Components

- Buttons: 10-pixel radius, clear primary/secondary hierarchy, visible focus ring.
- Inputs: full border, 10-pixel radius, labels always visible.
- Status: text plus icon or shape; never color alone.
- Data: tables and open lists preferred over repeated cards.
- Trace: numbered vertical sequence with duration and outcome.
- Charts: flat fills, direct labels where practical, restrained grid lines.

## Motion

Use 180-millisecond ease-out transitions for hover, selection, and result reveal. Disable non-essential motion under `prefers-reduced-motion`.
