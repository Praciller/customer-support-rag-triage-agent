import { Badge } from "../../components/ui/Badge";
import type { TriageResult } from "../../types/api";

export function TriageMetadata({ result }: { result: TriageResult }) {
  return (
    <>
      <Badge>{result.provider_used} / {result.model_used}</Badge>
      <Badge tone={result.grounded ? "success" : "danger"}>
        {result.grounded ? `${Math.round(result.grounding_score * 100)}% grounded` : `Not grounded (${Math.round(result.grounding_score * 100)}%)`}
      </Badge>
      <Badge>{result.cached ? "cache hit" : "fresh"}</Badge>
      <Badge>{result.total_latency_ms.toFixed(1)} ms total</Badge>
      <Badge tone={result.citation_integrity ? "success" : "danger"}>
        {result.citation_integrity ? "citations checked" : "citation rejected"}
      </Badge>
      {result.fallback_used && <Badge tone="warning">provider fallback</Badge>}
      {result.degraded_mode && <Badge tone="danger">degraded</Badge>}
    </>
  );
}
