import { CheckCircle2, Clock3 } from "lucide-react";

import type { TraceStep } from "../../types/api";
import { Badge } from "../ui/Badge";
import { EmptyState } from "../ui/EmptyState";

export function TraceList({ trace }: { trace: TraceStep[] }) {
  if (!trace.length) {
    return <EmptyState icon={<Clock3 size={20} />} description="Run triage to inspect the workflow." />;
  }
  return (
    <ol className="trace">
      {trace.map((step, index) => (
        <li key={step.node}>
          <span className="trace-icon"><CheckCircle2 size={16} /></span>
          <div>
            <strong>{index + 1}. {step.node.replaceAll("_", " ")}</strong>
            <p>{step.output_summary || step.detail}</p>
            <div className="trace-meta">
              <Badge>{step.component}</Badge>
              {step.provider && <Badge>{step.provider} / {step.model}</Badge>}
              {step.cache_hit && <Badge tone="success">cache hit</Badge>}
              {step.fallback && <Badge tone="warning">fallback</Badge>}
              {step.degraded_mode && <Badge tone="danger">degraded</Badge>}
            </div>
          </div>
          <code>{step.duration_ms} ms</code>
        </li>
      ))}
    </ol>
  );
}
