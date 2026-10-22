import { AlertCircle, CheckCircle2, Clock3 } from "lucide-react";

import type { TraceStep } from "../../types/api";
import { EmptyState } from "../ui/EmptyState";

export function TraceList({ trace }: { trace: TraceStep[] }) {
  if (!trace.length) {
    return <EmptyState icon={<Clock3 size={20} />} description="Run triage to inspect the workflow." />;
  }

  return (
    <ol className="trace trace-compact" aria-label="Workflow execution steps">
      {trace.map((step, index) => {
        const completed = step.status === "completed";
        const title = step.node.replaceAll("_", " ");
        return (
          <li key={step.node} className="trace-row">
            <span className={`trace-icon ${completed ? "trace-icon-complete" : "trace-icon-attention"}`} aria-hidden="true">
              {completed ? <CheckCircle2 size={15} /> : <AlertCircle size={15} />}
            </span>
            <div className="trace-content">
              <div className="trace-row-head">
                <strong>{index + 1}. {title}</strong>
                <span className="trace-duration">{step.duration_ms} ms</span>
              </div>
              <p className="trace-outcome">{step.output_summary || step.detail}</p>
              <div className="trace-runtime-summary">
                <span>{step.component}</span>
                {step.provider && <span>{step.provider}{step.model ? ` / ${step.model}` : ""}</span>}
                {!completed && <span className="trace-flag">{step.status}</span>}
                {step.cache_hit && <span>cache hit</span>}
                {step.fallback && <span className="trace-flag">fallback</span>}
                {step.degraded_mode && <span className="trace-flag">degraded</span>}
              </div>
              <details className="trace-details">
                <summary>Technical details for {title}</summary>
                <dl>
                  <div><dt>Status</dt><dd>{step.status}</dd></div>
                  <div><dt>Component</dt><dd>{step.component}</dd></div>
                  <div><dt>Provider / model</dt><dd>{step.provider ? `${step.provider} / ${step.model ?? "unknown"}` : "Not applicable"}</dd></div>
                  <div><dt>Input summary</dt><dd>{step.input_summary}</dd></div>
                  <div><dt>Output summary</dt><dd>{step.output_summary}</dd></div>
                  <div><dt>Cache</dt><dd>{step.cache_hit ? "hit" : "miss"}</dd></div>
                  <div><dt>Fallback</dt><dd>{step.fallback ? "yes" : "no"}</dd></div>
                  <div><dt>Degraded</dt><dd>{step.degraded_mode ? "yes" : "no"}</dd></div>
                  <div><dt>Retrieved cases</dt><dd>{step.retrieved_document_count}</dd></div>
                  <div><dt>Grounding</dt><dd>{step.grounding_result === null ? "Not checked" : String(step.grounding_result)}</dd></div>
                  <div><dt>Evidence references</dt><dd>{step.evidence_references.join(", ") || "None"}</dd></div>
                  {step.error_category && <div><dt>Error category</dt><dd>{step.error_category}</dd></div>}
                </dl>
              </details>
            </div>
          </li>
        );
      })}
    </ol>
  );
}
