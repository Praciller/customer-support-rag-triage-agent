import { TraceList } from "../../components/trace/TraceList";
import type { TriageResult } from "../../types/api";

export function TraceView({ trace }: { trace: TriageResult["trace"] }) {
  return <section className="panel page-panel"><div className="section-title"><div><p>LangGraph</p><h2>Seven-node execution trace</h2></div></div><TraceList trace={trace} /></section>;
}
