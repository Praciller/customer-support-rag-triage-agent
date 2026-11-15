import { CheckCircle2, ShieldAlert } from "lucide-react";

import type { TriageResult } from "../../types/api";
import { StatusIndicator } from "../../components/ui/StatusIndicator";

function policyStatusLabel(status: TriageResult["policy_status"]): string {
  const labels: Record<TriageResult["policy_status"], string> = {
    verified: "Policy checks passed",
    unsupported: "No supporting policy",
    conflicting: "Conflicting policy results",
    uncertain: "Policy check uncertain",
    no_approved_policy: "No approved policy",
    verification_failed: "Policy verification failed",
    no_proposals: "No proposals to check",
  };
  return labels[status];
}

export function DecisionWorkspace({ result }: { result: TriageResult | null }) {
  const policyVerified = result?.policy_status === "verified";
  const requiresReview = result !== null && !policyVerified;
  return (
    <section className="decision-workspace" aria-label="Recommended action">
      <div className="section-title">
        <div><p>Recommended action</p><h2>Triage summary</h2></div>
        {result && (
          <StatusIndicator
            label={result.escalate ? "Escalate" : requiresReview ? "Manual review" : "Policy checked"}
            tone={result.escalate || requiresReview ? "danger" : "success"}
          />
        )}
      </div>
      {result ? <>
        <div className="primary-action"><span>Next action</span><strong>{result.next_action.replaceAll("_", " ")}</strong></div>
        <div className="decision-intent"><span>Intent</span><strong>{result.intent.replaceAll("_", " ")}</strong></div>
        <div className="decision-statuses">
          <span className="decision-status" aria-label={`Policy review status: ${policyStatusLabel(result.policy_status)}`}>
            {policyVerified
              ? <CheckCircle2 size={16} aria-hidden="true" />
              : <ShieldAlert size={16} aria-hidden="true" />}
            {policyStatusLabel(result.policy_status)}
          </span>
          <span className="decision-status">Urgency: <strong>{result.urgency}</strong></span>
          <span className="decision-status">
            {result.escalate ? "Escalation required" : "Human review remains required"}
          </span>
        </div>
        {result.policy_status === "no_approved_policy" && (
          <p className="policy-caveat">
            Similar past cases are context only. They are not approved policy and do not authorize an action.
          </p>
        )}
        {result.proposal_checks.length > 0 && (
          <section className="proposal-checks" aria-label="Per-proposal policy checks">
            <h3>Per-proposal policy checks</h3>
            <ul className="proposal-check-list">
              {result.proposal_checks.map((check) => (
                <li key={check.proposal_id}>
                  <strong>{check.proposal_id.replaceAll("-", " ")}: {check.status.replaceAll("_", " ")}</strong>
                  <span>Verification: {check.verification_result.replaceAll("_", " ")}</span>
                  <span>Policy references: {check.policy_references.join(", ") || "none"}</span>
                </li>
              ))}
            </ul>
          </section>
        )}
        {result.verified_proposals.length > 0 && (
          <section className="verified-proposals" aria-label="Policy-verified proposals">
            <h3>Proposals with passing policy checks</h3>
            <ul>
              {result.verified_proposals.map((proposal) => (
                <li key={proposal.proposal_id}>
                  <p>{proposal.text}</p>
                  <small>
                    Policy: {proposal.policy_references.join(", ")} · Verification: {proposal.verification_result}
                    ({proposal.verification_method})
                  </small>
                </li>
              ))}
            </ul>
          </section>
        )}
        <div className="response"><span>Customer response · human review required</span><p>{result.suggested_response}</p></div>
        {result.escalation_reason && <div className="escalation-reason"><span><ShieldAlert size={15} /> Escalation reason</span><p>{result.escalation_reason}</p></div>}
        {result.degraded_mode && <div className="warning" role="status">A safe fallback was used. Review the triage and decide manually.</div>}
      </> : <div className="empty"><strong>Ready for triage</strong><p>Run triage to classify the message and find similar past cases.</p></div>}
    </section>
  );
}
