import { lazy, Suspense, useEffect, useState } from "react";

import { api } from "../../lib/api";
import { Badge, ErrorNotice, MetricCard } from "../../components";
import type { Evaluation } from "../../types/api";

const EvaluationChart = lazy(() => import("./EvaluationChart"));

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
  const intent = metrics.classification?.intent;
  const chartData = [
    { metric: "Precision", value: (metrics.retrieval_precision_at_k ?? 0) * 100 },
    { metric: "Intent", value: (metrics.intent_accuracy ?? 0) * 100 },
    { metric: "Urgency", value: (metrics.urgency_accuracy ?? 0) * 100 },
    { metric: "Grounded", value: (metrics.groundedness_pass_rate ?? 0) * 100 },
  ];
  if (loading) {
    return <section className="panel loading-panel" aria-live="polite">Loading measured evaluation artifacts...</section>;
  }
  if (metrics.status === "unavailable") {
    return <ErrorNotice message="Evaluation artifacts are unavailable. Run the documented evaluation command." />;
  }
  return (
    <div className="evaluation-layout">
      <section className="panel evaluation-method">
        <div>
          <p className="eyebrow-dark">Measured artifact</p>
          <h2>{(metrics.evaluation_mode ?? "unknown mode").replaceAll("_", " ")}</h2>
          <p>Banking77-derived fixture, deterministic provider, mapped-intent relevance labels.</p>
        </div>
        <Badge tone="success">No external LLM calls</Badge>
      </section>
      <div className="metric-grid">
        <MetricCard label={`Precision@${metrics.top_k ?? "K"}`} value={percent(metrics.retrieval_precision_at_k)} detail="Relevant cases in returned results" />
        <MetricCard label={`Recall@${metrics.top_k ?? "K"}`} value={percent(metrics.retrieval_recall_at_k)} detail="Known relevant fixture cases retrieved" />
        <MetricCard label="Intent accuracy" value={percent(metrics.intent_accuracy)} detail="Triage classification" />
        <MetricCard label="Intent macro F1" value={percent(metrics.intent_macro_f1)} detail="Balanced class quality" />
        <MetricCard label="Urgency accuracy" value={percent(metrics.urgency_accuracy)} detail="Escalation sensitivity" />
        <MetricCard label="Mock grounding verifier" value={percent(metrics.groundedness_pass_rate)} detail="Evidence-present workflow check" />
        <MetricCard label="Workflow success" value={percent(metrics.workflow_success_rate)} detail="All seven nodes completed" />
        <MetricCard label="MRR" value={metrics.retrieval_mrr?.toFixed(3) ?? "--"} detail={`nDCG ${(metrics.retrieval_ndcg_at_k ?? 0).toFixed(3)}`} />
        <MetricCard label="Avg latency" value={metrics.average_latency_ms ? `${Math.round(metrics.average_latency_ms)} ms` : "--"} detail="End-to-end workflow" />
        <MetricCard label="P50 / P95" value={`${Math.round(metrics.p50_latency_ms ?? 0)} / ${Math.round(metrics.p95_latency_ms ?? 0)} ms`} detail="Latency distribution" />
        <MetricCard label="Cache hit rate" value={percent(metrics.cache_hit_rate)} detail={`${metrics.fallback_count ?? 0} provider fallbacks`} />
        <MetricCard
          label="Provider usage"
          value={String(Object.values(metrics.provider_usage ?? {}).reduce((a, b) => a + b, 0))}
          detail={
            Object.entries(metrics.provider_usage ?? {})
              .map(([name, count]) => `${name}: ${count}`)
              .join(", ") || "No runs"
          }
        />
      </div>
      <Suspense fallback={<section className="panel evaluation-chart">Loading chart...</section>}>
        <EvaluationChart data={chartData} />
      </Suspense>
      {intent && (
        <section className="panel evaluation-table">
          <div className="section-title">
            <div><p>Classification detail</p><h2>Intent metrics by class</h2></div>
          </div>
          <div className="table-scroll">
            <table>
              <thead><tr><th>Intent</th><th>Precision</th><th>Recall</th><th>F1</th><th>Support</th></tr></thead>
              <tbody>
                {intent.labels.map((label) => {
                  const row = intent.per_class[label];
                  return (
                    <tr key={label}>
                      <th scope="row">{label.replaceAll("_", " ")}</th>
                      <td>{percent(row.precision)}</td>
                      <td>{percent(row.recall)}</td>
                      <td>{percent(row.f1)}</td>
                      <td>{row.support}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      )}
      <section className="panel limitations">
        <div className="section-title"><div><p>Interpretation</p><h2>Methodology and limitations</h2></div></div>
        <ul>{(metrics.limitations ?? []).map((item) => <li key={item}>{item}</li>)}</ul>
      </section>
    </div>
  );
}
