import type { ReactNode } from "react";

import type { StatusTone } from "./types";

export function StatusIndicator({
  label,
  tone,
  icon,
}: {
  label: string;
  tone: StatusTone;
  icon?: ReactNode;
}) {
  return (
    <span className={`status-indicator status-${tone}`} data-tone={tone} role="status">
      {icon && <span aria-hidden="true">{icon}</span>}
      <span>{label}</span>
    </span>
  );
}
