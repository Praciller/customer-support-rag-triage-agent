import { CheckCircle2, ShieldAlert } from "lucide-react";
import type { TriageResult } from "../../types/api";
import { StatusIndicator } from "../../components/ui/StatusIndicator";

export function DecisionWorkspace({ result }: { result: TriageResult | null }) {
  return (
    <section className="decision-workspace" aria-label="Recommended action">
      <div className="section-title"><div><p>Recommended action</p><h2>Triage summary</h2></div>{result && <StatusIndicator label={result.escalate ? "Escalate" : "Standard queue"} tone={result.escalate ? "danger" : "success"} />}</div>
      {result ? <>
        <div className="primary-action"><span>Next action</span><strong>{result.next_action.replaceAll("_", " ")}</strong></div>
        <div className="decision-intent"><span>Intent</span><strong>{result.intent.replaceAll("_", " ")}</strong></div>
        <div className="decision-statuses">
          <span className="decision-status"><CheckCircle2 size={16} />{result.grounded ? `${Math.round(result.grounding_score * 100)}% grounded` : `Not grounded (${Math.round(result.grounding_score * 100)}%)`}</span>
          <span className="decision-status">Urgency: <strong>{result.urgency}</strong></span>
          <span className="decision-status">{result.citation_integrity ? "Citations checked" : "Citation rejected"}</span>
          <span className="decision-status">{result.escalate ? "Manual review required" : "Human review remains required"}</span>
        </div>
        <div className="response"><span>Suggested response · draft for human review</span><p>{result.suggested_response}</p></div>
        {result.escalation_reason && <div className="escalation-reason"><span><ShieldAlert size={15} /> Escalation reason</span><p>{result.escalation_reason}</p></div>}
        {result.degraded_mode && <div className="warning" role="status">A safe fallback was used. Review retrieved evidence and respond manually.</div>}
        {!!result.unsupported_claims.length && <div className="warning">Unsupported claims: {result.unsupported_claims.join("; ")}</div>}
      </> : <div className="empty"><strong>Ready for triage</strong><p>Run triage to generate a recommended action and evidence.</p></div>}
    </section>
  );
}
