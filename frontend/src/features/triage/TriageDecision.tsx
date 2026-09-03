import { Badge } from "../../components";
import type { TriageResult } from "../../types";
import { TriageMetadata } from "./TriageMetadata";

export function TriageDecision({ result }: { result: TriageResult | null }) {
  return (
    <article className="panel decision">
      <div className="section-title"><div><p>Decision</p><h2>Triage summary</h2></div>{result && <Badge tone={result.escalate ? "danger" : "success"}>{result.escalate ? "Escalate" : "Standard queue"}</Badge>}</div>
      {result ? (
        <>
          <div className="facts">
            <div><span>Intent</span><strong>{result.intent.replaceAll("_", " ")}</strong></div>
            <div><span>Urgency</span><strong>{result.urgency}</strong></div>
            <div><span>Intent confidence</span><strong>{Math.round(result.intent_confidence * 100)}%</strong></div>
            <div><span>Next action</span><strong>{result.next_action.replaceAll("_", " ")}</strong></div>
          </div>
          <div className="normalized-output">
            <span>Normalized message</span>
            <p>{result.normalized_message}</p>
          </div>
          <div className="response"><span>Suggested response</span><p>{result.suggested_response}</p></div>
          {result.escalation_reason && (
            <div className="escalation-reason">
              <span>Escalation reason</span>
              <p>{result.escalation_reason}</p>
            </div>
          )}
          <div className="metadata">
            <Badge tone={result.grounded ? "success" : "danger"}>{Math.round(result.grounding_score * 100)}% grounded</Badge>
            <Badge tone={result.citation_integrity ? "success" : "danger"}>
              {result.citation_integrity ? "citations checked" : "citation rejected"}
            </Badge>
            <TriageMetadata result={result} />
          </div>
          {result.degraded_mode && (
            <div className="warning" role="status">
              A safe fallback was used. Review retrieved evidence and respond manually.
            </div>
          )}
          {!!result.unsupported_claims.length && (
            <div className="warning">
              Unsupported claims: {result.unsupported_claims.join("; ")}
            </div>
          )}
        </>
      ) : <div className="empty">Run triage to classify, retrieve, draft, and verify a response.</div>}
    </article>
  );
}
