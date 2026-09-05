import type { TriageResult } from "../../types/api";
import { TriageMetadata } from "./TriageMetadata";

export function TechnicalDetails({ result }: { result: TriageResult }) {
  return (
    <details className="technical-details" aria-label="Technical details">
      <summary>Technical details</summary>
      <div className="technical-details-body">
        <div className="technical-detail"><span>Provider / model</span><code>{result.provider_used} / {result.model_used}</code></div>
        <div className="technical-detail"><span>Cache</span><code>{result.cached ? "hit" : "fresh"}</code></div>
        <div className="technical-detail"><span>Latency</span><code>{result.total_latency_ms.toFixed(1)} ms total</code></div>
        <div className="technical-detail"><span>Normalized input</span><code>{result.normalized_message}</code></div>
        <div className="metadata"><TriageMetadata result={result} /></div>
      </div>
    </details>
  );
}
