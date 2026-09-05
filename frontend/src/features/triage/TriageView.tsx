import { CaseList } from "../../components/evidence/CaseList";
import { TraceList } from "../../components/trace/TraceList";
import type { TriageResult } from "../../types/api";
import { TicketComposer } from "./TicketComposer";
import { DecisionWorkspace } from "./DecisionWorkspace";
import { TechnicalDetails } from "./TechnicalDetails";

export function TriageView({
  message,
  setMessage,
  run,
  loading,
  result,
  error,
}: {
  message: string;
  setMessage: (value: string) => void;
  run: () => void;
  loading: boolean;
  result: TriageResult | null;
  error: string;
}) {
  return (
    <div className="workspace">
      <TicketComposer
        message={message}
        setMessage={setMessage}
        run={run}
        loading={loading}
        error={error}
      />
      <DecisionWorkspace result={result} />
      <section className="evidence panel" aria-label="Retrieved evidence">
          <div className="section-title"><div><p>Retrieved evidence</p><h2>Similar cases</h2></div><span className="evidence-count">{result?.retrieved_cases.length ?? 0} found</span></div>
          <p className="evidence-caveat">Retrieved cases are evidence/context, not support policy.</p>
          <CaseList cases={result?.retrieved_cases ?? []} />
      </section>
      <section className="panel inline-trace" aria-label="Workflow trace">
        <div className="section-title">
          <div><p>Workflow trace</p><h2>Seven-node execution trace</h2></div>
          <span className="evidence-count">{result?.trace.length ?? 0} / 7 complete</span>
        </div>
        <TraceList trace={result?.trace ?? []} />
      </section>
      {result && <TechnicalDetails result={result} />}
    </div>
  );
}
