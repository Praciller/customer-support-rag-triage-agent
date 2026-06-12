import { CheckCircle2, Clock3, Database, ShieldAlert } from "lucide-react";
import type { SimilarCase, TraceStep } from "./types";

export function Badge({ children, tone = "neutral" }: { children: React.ReactNode; tone?: string }) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}

export function MetricCard({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <article className="panel metric">
      <p>{label}</p>
      <strong>{value}</strong>
      <span>{detail}</span>
    </article>
  );
}

export function CaseList({ cases }: { cases: SimilarCase[] }) {
  if (!cases.length) {
    return <div className="empty"><Database size={20} />No matching indexed cases yet.</div>;
  }
  return (
    <div className="case-list">
      {cases.map((item) => (
        <article className="case" key={item.ticket_id}>
          <div className="case-head">
            <Badge>{item.intent.replaceAll("_", " ")}</Badge>
            <span className="score">{Math.round(item.score * 100)}% match</span>
          </div>
          <p>{item.message}</p>
          <small>{item.source} · {item.ticket_id}</small>
        </article>
      ))}
    </div>
  );
}

export function TraceList({ trace }: { trace: TraceStep[] }) {
  if (!trace.length) {
    return <div className="empty"><Clock3 size={20} />Run triage to inspect the workflow.</div>;
  }
  return (
    <ol className="trace">
      {trace.map((step, index) => (
        <li key={step.node}>
          <span className="trace-icon"><CheckCircle2 size={16} /></span>
          <div>
            <strong>{index + 1}. {step.node.replaceAll("_", " ")}</strong>
            <p>{step.detail}</p>
          </div>
          <code>{step.duration_ms} ms</code>
        </li>
      ))}
    </ol>
  );
}

export function ErrorNotice({ message }: { message: string }) {
  return <div className="error"><ShieldAlert size={18} />{message}</div>;
}
