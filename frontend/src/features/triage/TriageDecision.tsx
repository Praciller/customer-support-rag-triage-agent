import { StatusIndicator } from "../../components/ui/StatusIndicator";
import type { TriageResult } from "../../types/api";
import { TriageMetadata } from "./TriageMetadata";

export function TriageDecision({ result }: { result: TriageResult | null }) {
  const verified = result?.policy_status === "verified";
  return (
    <article className="panel decision">
      <div className="section-title">
        <div><p>Decision</p><h2>Triage summary</h2></div>
        {result && <StatusIndicator label={result.escalate ? "Escalate" : verified ? "Checks passed" : "Manual review"} tone={result.escalate || !verified ? "danger" : "success"} />}
      </div>
      {result ? (
        <>
          <div className="facts">
            <div><span>Intent</span><strong>{result.intent.replaceAll("_", " ")}</strong></div>
            <div><span>Urgency</span><strong>{result.urgency}</strong></div>
            <div><span>Policy status</span><strong>{result.policy_status.replaceAll("_", " ")}</strong></div>
            <div><span>Next action</span><strong>{result.next_action.replaceAll("_", " ")}</strong></div>
          </div>
          <div className="normalized-output">
            <span>Normalized message</span>
            <p>{result.normalized_message}</p>
          </div>
          <div className="response"><span>Customer response · human review required</span><p>{result.suggested_response}</p></div>
          {result.proposal_checks.length > 0 && (
            <ul aria-label="Per-proposal policy checks">
              {result.proposal_checks.map((check) => (
                <li key={check.proposal_id}>
                  {check.proposal_id}: {check.status}; verification {check.verification_result};
                  policy {check.policy_references.join(", ") || "none"}
                </li>
              ))}
            </ul>
          )}
          {result.verified_proposals.map((proposal) => (
            <p key={proposal.proposal_id}>
              {proposal.text} (policy {proposal.policy_references.join(", ")}; verification {proposal.verification_result})
            </p>
          ))}
          {result.policy_status === "no_approved_policy" && (
            <p className="evidence-caveat">Similar past cases are not approved policy.</p>
          )}
          {result.escalation_reason && <div className="escalation-reason"><span>Escalation reason</span><p>{result.escalation_reason}</p></div>}
          <div className="metadata"><TriageMetadata result={result} /></div>
          {result.degraded_mode && (
            <div className="warning" role="status">A safe fallback was used. Review the triage and decide manually.</div>
          )}
        </>
      ) : <div className="empty">Run triage to classify the message and find similar past cases.</div>}
    </article>
  );
}
