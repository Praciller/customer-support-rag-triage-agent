import { useEffect, useState } from "react";

import { api } from "../../lib/api";
import { ErrorNotice } from "../../components/ui/ErrorNotice";
import type { Evaluation } from "../../types/api";

function MetricValue({ label, value, detail }: { label: string; value: string; detail?: string }) {
  return (
    <div className="evaluation-metric">
      <dt>{label}{detail && <small>{detail}</small>}</dt>
      <dd>{value}</dd>
    </div>
  );
}

export function EvaluationView() {
  const [metrics, setMetrics] = useState<Evaluation>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.evaluation()
      .then(setMetrics)
      .catch(() => setMetrics({ status: "unavailable" }))
      .finally(() => setLoading(false));
  }, []);

  const percent = (value?: number) => value === undefined ? "--" : `${Math.round(value * 100)}%`;
  const decimal = (value?: number) => value === undefined ? "--" : value.toFixed(3);
  const milliseconds = (value?: number) => value === undefined ? "--" : `${Math.round(value)} ms`;
  const intent = metrics.classification?.intent;
  const mode = metrics.evaluation_mode ?? "unknown_mode";
  const deterministic = mode === "deterministic_mock";
  const topK = metrics.top_k ?? "K";

  if (loading) {
    return <section className="panel loading-panel" aria-live="polite">Loading measured evaluation artifacts...</section>;
  }
  if (metrics.status === "unavailable") {
    return <ErrorNotice message="Evaluation artifacts are unavailable. Run the documented evaluation command." />;
  }

  return (
    <div className="evaluation-layout">
      <section className="panel evaluation-method" aria-labelledby="evaluation-mode-title">
        <div>
          <p className="eyebrow-dark">Measured artifact</p>
          <h2 id="evaluation-mode-title">{mode.replaceAll("_", " ")}</h2>
          <p>Banking77-derived fixture · mapped-intent relevance labels · not a production SLA.</p>
          {metrics.dataset?.sample_size !== undefined && (
            <p>Evaluation sample: {metrics.dataset.sample_size} labeled tickets</p>
          )}
        </div>
        <p className="evaluation-mode-note">
          {deterministic
            ? "No external LLM calls in this deterministic mock run"
            : "Inspect provider provenance and limitations before interpreting these metrics"}
        </p>
      </section>

      <div className="evaluation-groups">
        <section className="panel evaluation-group" aria-labelledby="retrieval-heading">
          <div className="section-title">
            <div><p>01 / Retrieval</p><h2 id="retrieval-heading">Retrieval quality</h2></div>
          </div>
          <dl className="evaluation-values">
            <MetricValue label={`Precision@${topK}`} value={percent(metrics.retrieval_precision_at_k)} detail="Relevant mapped-intent results in top K" />
            <MetricValue label={`Recall@${topK}`} value={percent(metrics.retrieval_recall_at_k)} detail="Known relevant fixture cases retrieved" />
            <MetricValue label="MRR" value={decimal(metrics.retrieval_mrr)} detail="Reciprocal rank of first relevant case" />
            <MetricValue label={`nDCG@${topK}`} value={decimal(metrics.retrieval_ndcg_at_k)} detail="Rank-weighted mapped-intent relevance" />
            <MetricValue label="Zero-result rate" value={percent(metrics.retrieval_zero_result_rate)} />
          </dl>
        </section>

        <section className="panel evaluation-group" aria-labelledby="workflow-heading">
          <div className="section-title">
            <div><p>02 / Workflow</p><h2 id="workflow-heading">Workflow checks</h2></div>
          </div>
          <dl className="evaluation-values">
            <MetricValue label="Intent accuracy" value={percent(metrics.intent_accuracy)} />
            <MetricValue label="Intent macro F1" value={percent(metrics.intent_macro_f1)} />
            <MetricValue label="Urgency accuracy" value={percent(metrics.urgency_accuracy)} />
            <MetricValue label="Urgency macro F1" value={percent(metrics.urgency_macro_f1)} />
            <MetricValue label="Mock grounding verifier" value={percent(metrics.groundedness_pass_rate)} detail="Evidence-present workflow check; not semantic entailment" />
            <MetricValue label="Workflow success" value={percent(metrics.workflow_success_rate)} detail="Seven nodes completed" />
            <MetricValue label="Unsupported-claim rate" value={percent(metrics.unsupported_claim_rate)} />
            <MetricValue label="Degraded-mode rate" value={percent(metrics.degraded_mode_rate)} />
          </dl>
        </section>

        <section className="panel evaluation-group" aria-labelledby="runtime-heading">
          <div className="section-title">
            <div><p>03 / Runtime</p><h2 id="runtime-heading">Runtime profile</h2></div>
          </div>
          <dl className="evaluation-values">
            <MetricValue label="Average latency" value={milliseconds(metrics.average_latency_ms)} />
            <MetricValue label="P50 latency" value={milliseconds(metrics.p50_latency_ms)} />
            <MetricValue label="P95 latency" value={milliseconds(metrics.p95_latency_ms)} />
            <MetricValue label="Cache hit rate" value={percent(metrics.cache_hit_rate)} />
            <MetricValue label="Provider fallbacks" value={metrics.fallback_count === undefined ? "--" : String(metrics.fallback_count)} />
            <MetricValue label="Provider usage" value={Object.values(metrics.provider_usage ?? {}).reduce((a, b) => a + b, 0).toString()} />
          </dl>
          <p className="evaluation-provider-detail">
            {Object.entries(metrics.provider_usage ?? {}).map(([name, count]) => `${name}: ${count}`).join(" · ") || "No provider usage recorded"}
          </p>
        </section>
      </div>

      {intent && (
        <section className="panel evaluation-table" aria-labelledby="classification-heading">
          <div className="section-title">
            <div><p>04 / Classification</p><h2 id="classification-heading">Intent metrics by class</h2></div>
          </div>
          <div className="table-scroll">
            <table>
              <thead><tr><th scope="col">Intent</th><th scope="col">Precision</th><th scope="col">Recall</th><th scope="col">F1</th><th scope="col">Support</th></tr></thead>
              <tbody>
                {intent.labels.map((label) => {
                  const row = intent.per_class[label];
                  return (
                    <tr key={label}>
                      <th scope="row">{label.replaceAll("_", " ")}</th>
                      <td data-label="Precision">{percent(row.precision)}</td>
                      <td data-label="Recall">{percent(row.recall)}</td>
                      <td data-label="F1">{percent(row.f1)}</td>
                      <td data-label="Support">{row.support}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      )}

      <section className="panel limitations" aria-labelledby="methodology-heading">
        <div className="section-title">
          <div><p>05 / Interpretation</p><h2 id="methodology-heading">Methodology and limitations</h2></div>
        </div>
        <p className="evaluation-limitation-intro">
          Retrieval relevance uses mapped intent, not human policy judgment. Mock grounding is not
          semantic entailment or real-provider answer-quality evidence.
        </p>
        <ul>{(metrics.limitations ?? []).map((item) => <li key={item}>{item}</li>)}</ul>
      </section>
    </div>
  );
}
