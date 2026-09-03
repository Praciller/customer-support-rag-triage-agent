import { Search } from "lucide-react";
import { lazy, Suspense, useEffect, useState } from "react";

import { api } from "../api";
import { Badge, CaseList, ErrorNotice, MetricCard, TraceList } from "../components";
import type { Evaluation, SimilarCase, TriageResult } from "../types";
import { OverviewView } from "../features/overview/OverviewView";
import { sampleTicketMessage } from "../features/triage/TicketComposer";
import { TriageView } from "../features/triage/TriageView";
import { type View } from "./navigation";
import { AppShell } from "./shell/AppShell";

const EvaluationChart = lazy(() => import("../EvaluationChart"));

export default function App() {
  const [view, setView] = useState<View>("triage");
  const [message, setMessage] = useState<string>(sampleTicketMessage);
  const [result, setResult] = useState<TriageResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [apiStatus, setApiStatus] = useState<"checking" | "connected" | "unavailable">(
    "checking",
  );

  useEffect(() => {
    api.health()
      .then(() => setApiStatus("connected"))
      .catch(() => setApiStatus("unavailable"));
  }, []);

  async function runTriage() {
    if (!message.trim()) return;
    setLoading(true);
    setError("");
    try {
      const data = await api.triage(message, 5);
      setResult(data);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Triage failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell view={view} setView={setView} apiStatus={apiStatus}>
        {view === "overview" && <OverviewView setView={setView} />}
        {view === "triage" && (
          <TriageView
            message={message}
            setMessage={setMessage}
            run={runTriage}
            loading={loading}
            result={result}
            error={error}
          />
        )}
        {view === "search" && <SearchView />}
        {view === "trace" && <TraceView trace={result?.trace ?? []} />}
        {view === "evaluation" && <EvaluationView />}
        {view === "dataset" && <DatasetView />}
        {view === "providers" && <ProviderView />}
    </AppShell>
  );
}

function SearchView() {
  const [query, setQuery] = useState("card delivery is late");
  const [intent, setIntent] = useState("");
  const [topK, setTopK] = useState(5);
  const [cases, setCases] = useState<SimilarCase[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  async function search() {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    try {
      setCases(await api.search(query, topK, intent));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Search failed.");
    } finally {
      setLoading(false);
    }
  }
  return (
    <section className="panel page-panel">
      <div className="section-title"><div><p>Vector retrieval</p><h2>Search indexed support tickets</h2></div></div>
      <div className="search-row">
        <input
          aria-label="Search support tickets"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <select
          aria-label="Intent filter"
          value={intent}
          onChange={(event) => setIntent(event.target.value)}
        >
          <option value="">All intents</option>
          {["delivery_issue", "refund_request", "billing_issue", "technical_issue", "account_access", "product_question", "complaint", "cancellation", "other"].map((value) => <option key={value}>{value}</option>)}
        </select>
        <select
          aria-label="Top K"
          value={topK}
          onChange={(event) => setTopK(Number(event.target.value))}
        >
          {[3, 5, 8, 10].map((value) => (
            <option key={value} value={value}>Top {value}</option>
          ))}
        </select>
        <button className="primary" onClick={search} disabled={loading || !query.trim()}>
          <Search size={16} />{loading ? "Searching..." : "Search"}
        </button>
      </div>
      {error && <ErrorNotice message={error} />}
      <CaseList cases={cases} />
    </section>
  );
}

function TraceView({ trace }: { trace: TriageResult["trace"] }) {
  return <section className="panel page-panel"><div className="section-title"><div><p>LangGraph</p><h2>Seven-node execution trace</h2></div></div><TraceList trace={trace} /></section>;
}

function EvaluationView() {
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

function DatasetView() {
  const [data, setData] = useState<Record<string, unknown>>({});
  useEffect(() => { api.dataset().then(setData).catch(() => setData({ status: "unavailable" })); }, []);
  const intents = (data.intents ?? {}) as Record<string, number>;
  const records = Number(data.records || 0);
  return (
    <section className="panel page-panel">
      <div className="section-title">
        <div><p>Public source</p><h2>Banking77 dataset explorer</h2></div>
        <Badge>{records} records</Badge>
      </div>
      <div className="dataset-summary">
        <div><span>Dataset</span><strong>{String(data.name ?? "Not loaded")}</strong></div>
        <div><span>License</span><strong>{String(data.license ?? "Unknown")}</strong></div>
        <div><span>Split</span><strong>{String(data.split ?? "Unknown")}</strong></div>
        <div><span>Source</span><strong>{String(data.upstream_dataset ?? data.name ?? "Unknown")}</strong></div>
      </div>
      <h3 className="subheading">Mapped intent distribution</h3>
      <div className="intent-bars">
        {Object.entries(intents).map(([intent, count]) => (
          <div key={intent}>
            <span>{intent.replaceAll("_", " ")}</span>
            <div><i style={{ width: `${Math.max(4, (count / Math.max(records, 1)) * 100)}%` }} /></div>
            <strong>{count}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}

function ProviderView() {
  const [data, setData] = useState<Record<string, unknown>>({});
  useEffect(() => { api.providers().then(setData).catch(() => setData({ status: "unavailable" })); }, []);
  return (
    <section className="panel page-panel">
      <div className="section-title"><div><p>Runtime</p><h2>Provider and infrastructure status</h2></div></div>
      <div className="config-list">
        {Object.entries(data).map(([key, value]) => (
          <div key={key}><span>{key.replaceAll("_", " ")}</span><code>{typeof value === "object" ? JSON.stringify(value) : String(value)}</code></div>
        ))}
      </div>
    </section>
  );
}
