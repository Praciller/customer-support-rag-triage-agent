import { TraceList } from "../../components/trace/TraceList";
import { Panel } from "../../components/ui/Panel";
import type { TriageResult } from "../../types/api";

export function TraceView({ trace }: { trace: TriageResult["trace"] }) {
  return <Panel className="page-panel"><div className="section-title"><div><p>LangGraph</p><h2>Seven-node execution trace</h2></div></div><TraceList trace={trace} /></Panel>;
}
