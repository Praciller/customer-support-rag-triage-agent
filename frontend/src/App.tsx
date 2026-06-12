import {
  Activity,
  BarChart3,
  Bot,
  ChevronRight,
  CircleDot,
  Database,
  GitBranch,
  LayoutDashboard,
  Search,
  Send,
  ServerCog,
} from "lucide-react";
import { lazy, Suspense, useEffect, useState } from "react";

import { api } from "./api";
import { Badge, CaseList, ErrorNotice, MetricCard, TraceList } from "./components";
import type { Evaluation, SimilarCase, TriageResult } from "./types";

const EvaluationChart = lazy(() => import("./EvaluationChart"));

type View =
  | "overview"
  | "triage"
  | "search"
  | "trace"
  | "evaluation"
  | "dataset"
  | "providers";

const nav: { id: View; label: string; icon: typeof LayoutDashboard }[] = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "triage", label: "Ticket triage", icon: LayoutDashboard },
  { id: "search", label: "Semantic search", icon: Search },
  { id: "trace", label: "Agent trace", icon: GitBranch },
  { id: "evaluation", label: "Evaluation", icon: BarChart3 },
  { id: "dataset", label: "Dataset explorer", icon: Database },
  { id: "providers", label: "Provider status", icon: ServerCog },
];

const sample = "My card has still not arrived and I need help before I travel tomorrow.";

export default function App() {
  const [view, setView] = useState<View>("triage");
  const [message, setMessage] = useState(sample);
  const [result, setResult] = useState<TriageResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

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
    <div className="app-shell antialiased">
      <aside>
        <div className="brand"><Bot size={22} /><span>ResolveOps</span></div>
        <p className="eyebrow">Support intelligence</p>
        <nav aria-label="Main navigation">
          {nav.map((item) => (
            <button
              className={view === item.id ? "active" : ""}
              key={item.id}
              onClick={() => setView(item.id)}
            >
              <item.icon size={18} />{item.label}
            </button>
          ))}
        </nav>
        <div className="system-card">
          <span><CircleDot size={14} />System status</span>
          <strong>Operational</strong>
          <small>Mock mode works without API keys</small>
        </div>
      </aside>
      <main>
        <header className="topbar">
          <div>
            <p className="breadcrumb">Workspace <ChevronRight size={13} /> {nav.find((x) => x.id === view)?.label}</p>
            <h1>{nav.find((x) => x.id === view)?.label}</h1>
          </div>
          <Badge tone="success"><Activity size={13} /> API connected</Badge>
        </header>
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
      </main>
    </div>
  );
}

function OverviewView({ setView }: { setView: (view: View) => void }) {
  return (
    <div className="overview-grid">
      <section className="panel overview-hero">
        <p className="eyebrow-dark">Retrieval-grounded operations</p>
        <h2>Move from incoming message to a reviewable support decision.</h2>
        <p>
          Classify intent, assess urgency, retrieve similar Banking77 cases, draft a response,
          verify grounding, and inspect all seven LangGraph steps.
        </p>
        <button className="primary" onClick={() => setView("triage")}>
          Open triage workspace <ChevronRight size={16} />
        </button>
      </section>
      <MetricCard label="Workflow" value="7 nodes" detail="Typed and traceable" />
      <MetricCard label="Retrieval" value="Local BGE" detail="Qdrant semantic search" />
      <MetricCard label="Reliability" value="3 providers" detail="Cache, retry, fallback" />
    </div>
  );
}

function TriageView({
  message,
  setMessage,
  run,
  loading,
  result,
  error,
}: {
  message: string;
  setMessage: (value: string) => void;
  run: () => void;
  loading: boolean;
  result: TriageResult | null;
  error: string;
}) {
  return (
    <div className="workspace">
      <section className="panel composer">
        <div className="section-title"><div><p>Incoming request</p><h2>Customer message</h2></div><code>{message.length}/2000</code></div>
        <textarea value={message} onChange={(event) => setMessage(event.target.value)} maxLength={2000} />
        <div className="actions">
          <button className="secondary" onClick={() => setMessage(sample)}>Load example</button>
          <button className="primary" onClick={run} disabled={loading || !message.trim()}>
            <Send size={16} />{loading ? "Running workflow..." : "Run triage"}
          </button>
        </div>
        {error && <ErrorNotice message={error} />}
      </section>
      <section className="result-grid">
        <article className="panel decision">
          <div className="section-title"><div><p>Decision</p><h2>Triage summary</h2></div>{result && <Badge tone={result.escalate ? "danger" : "success"}>{result.escalate ? "Escalate" : "Standard queue"}</Badge>}</div>
          {result ? (
            <>
              <div className="facts">
                <div><span>Intent</span><strong>{result.intent.replaceAll("_", " ")}</strong></div>
                <div><span>Urgency</span><strong>{result.urgency}</strong></div>
                <div><span>Confidence</span><strong>{Math.round(result.confidence * 100)}%</strong></div>
                <div><span>Next action</span><strong>{result.next_action.replaceAll("_", " ")}</strong></div>
              </div>
              <div className="response"><span>Suggested response</span><p>{result.suggested_response}</p></div>
              {result.escalation_reason && (
                <div className="escalation-reason">
                  <span>Escalation reason</span>
                  <p>{result.escalation_reason}</p>
                </div>
              )}
              <div className="metadata">
                <Badge>{result.provider_used} / {result.model_used}</Badge>
                <Badge tone={result.grounded ? "success" : "danger"}>{Math.round(result.grounding_score * 100)}% grounded</Badge>
                <Badge>{result.cached ? "cache hit" : "fresh"}</Badge>
                {result.degraded_mode && <Badge tone="danger">degraded</Badge>}
              </div>
            </>
          ) : <div className="empty">Run triage to classify, retrieve, draft, and verify a response.</div>}
        </article>
        <article className="panel evidence">
          <div className="section-title"><div><p>Retrieval</p><h2>Similar cases</h2></div><Badge>{result?.retrieved_cases.length ?? 0} found</Badge></div>
          <CaseList cases={result?.retrieved_cases ?? []} />
        </article>
      </section>
    </div>
  );
}

function SearchView() {
  const [query, setQuery] = useState("card delivery is late");
  const [intent, setIntent] = useState("");
  const [topK, setTopK] = useState(5);
  const [cases, setCases] = useState<SimilarCase[]>([]);
  const [error, setError] = useState("");
  async function search() {
    setError("");
    try {
      setCases(await api.search(query, topK, intent));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Search failed.");
    }
  }
  return (
    <section className="panel page-panel">
      <div className="section-title"><div><p>Vector retrieval</p><h2>Search indexed support tickets</h2></div></div>
      <div className="search-row">
        <input value={query} onChange={(event) => setQuery(event.target.value)} />
        <select value={intent} onChange={(event) => setIntent(event.target.value)}>
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
        <button className="primary" onClick={search}><Search size={16} />Search</button>
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
  useEffect(() => { api.evaluation().then(setMetrics).catch(() => setMetrics({ status: "unavailable" })); }, []);
  const percent = (value?: number) => value === undefined ? "--" : `${Math.round(value * 100)}%`;
  const chartData = [
    { metric: "Precision", value: (metrics.retrieval_precision_at_k ?? 0) * 100 },
    { metric: "Intent", value: (metrics.intent_accuracy ?? 0) * 100 },
    { metric: "Urgency", value: (metrics.urgency_accuracy ?? 0) * 100 },
    { metric: "Grounded", value: (metrics.groundedness_pass_rate ?? 0) * 100 },
  ];
  return (
    <div className="evaluation-layout">
      <div className="metric-grid">
        <MetricCard label="Precision@K" value={percent(metrics.retrieval_precision_at_k)} detail="Relevant cases retrieved" />
        <MetricCard label="Intent accuracy" value={percent(metrics.intent_accuracy)} detail="Triage classification" />
        <MetricCard label="Urgency accuracy" value={percent(metrics.urgency_accuracy)} detail="Escalation sensitivity" />
        <MetricCard label="Groundedness" value={percent(metrics.groundedness_pass_rate)} detail="Drafts passing verifier" />
        <MetricCard label="Avg latency" value={metrics.average_latency_ms ? `${Math.round(metrics.average_latency_ms)} ms` : "--"} detail="End-to-end workflow" />
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
