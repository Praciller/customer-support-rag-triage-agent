import { Badge, CaseList, TraceList } from "../../components";
import type { TriageResult } from "../../types";
import { TicketComposer } from "./TicketComposer";
import { TriageDecision } from "./TriageDecision";

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
      <section className="result-grid">
        <TriageDecision result={result} />
        <article className="panel evidence">
          <div className="section-title"><div><p>Retrieval</p><h2>Similar cases</h2></div><Badge>{result?.retrieved_cases.length ?? 0} found</Badge></div>
          <CaseList cases={result?.retrieved_cases ?? []} />
        </article>
      </section>
      <section className="panel inline-trace">
        <div className="section-title">
          <div><p>Execution evidence</p><h2>Seven-node execution trace</h2></div>
          <Badge>{result?.trace.length ?? 0} / 7 complete</Badge>
        </div>
        <TraceList trace={result?.trace ?? []} />
      </section>
    </div>
  );
}
