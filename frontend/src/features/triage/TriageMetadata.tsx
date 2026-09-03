import { Badge } from "../../components";
import type { TriageResult } from "../../types/api";

export function TriageMetadata({ result }: { result: TriageResult }) {
  return (
    <>
      <Badge>{result.provider_used} / {result.model_used}</Badge>
      <Badge>{result.cached ? "cache hit" : "fresh"}</Badge>
      <Badge>{result.total_latency_ms.toFixed(1)} ms total</Badge>
      {result.fallback_used && <Badge tone="warning">provider fallback</Badge>}
      {result.degraded_mode && <Badge tone="danger">degraded</Badge>}
    </>
  );
}
