import type { ReactNode } from "react";

import type { StatusTone } from "./types";

export function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: StatusTone }) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}
