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

const demoTickets = [
  {
    label: "Card not arrived",
    message: "My card has still not arrived and I need help before I travel tomorrow.",
  },
  {
    label: "Cash withdrawal",
    message: "My cash withdrawal is still pending and I need to understand why.",
  },
  {
    label: "Transfer pending",
    message: "My transfer has been pending since yesterday. What should I do?",
  },
  {
    label: "Card stolen",
    message: "My card was stolen and I need urgent help protecting my account.",
  },
  {
    label: "Account access",
    message: "I forgot my passcode and cannot sign in to the app.",
  },
  {
    label: "Suspicious transaction",
    message: "A cash withdrawal was made from my account, but I did not make it. This is urgent.",
  },
  {
    label: "Payment reversed",
    message: "My card payment was reversed even though I already received the item.",
  },
] as const;

const sample = demoTickets[0].message;

export default function App() {
  const [view, setView] = useState<View>("triage");
  const [message, setMessage] = useState<string>(sample);
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
    <div className="app-shell antialiased">
      <aside>
        <div className="brand"><Bot size={22} /><span>ResolveOps</span></div>
        <p className="eyebrow">Support intelligence</p>
        <nav aria-label="Main navigation">
          {nav.map((item) => (
            <button
              aria-current={view === item.id ? "page" : undefined}
              className={view === item.id ? "active" : ""}
              key={item.id}
              onClick={() => setView(item.id)}
            >
              <item.icon size={18} />{item.label}
            </button>
          ))}
        </nav>
        <div className="system-card">
          <span><CircleDot size={14} />Deterministic demo</span>
          <strong>No API key required</strong>
          <small>Mock provider and bounded local index</small>
        </div>
      </aside>
      <main>
        <header className="topbar">
          <div>
            <p className="breadcrumb">Workspace <ChevronRight size={13} /> {nav.find((x) => x.id === view)?.label}</p>
            <h1>{nav.find((x) => x.id === view)?.label}</h1>
          </div>
          <Badge tone={apiStatus === "connected" ? "success" : apiStatus === "unavailable" ? "danger" : "neutral"}>
            <Activity size={13} />
            {apiStatus === "connected"
              ? "API connected"
              : apiStatus === "unavailable"
                ? "API unavailable"
                : "Checking API"}
          </Badge>
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
        <textarea
          aria-label="Customer message"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          maxLength={2000}
        />
        <div className="example-tickets" aria-label="Example tickets">
          {demoTickets.map((ticket) => (
            <button
              className="example-ticket"
              key={ticket.label}
              onClick={() => setMessage(ticket.message)}
              type="button"
            >
              {ticket.label}
            </button>
          ))}
        </div>
        <div className="actions">
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
                <Badge>{result.provider_used} / {result.model_used}</Badge>
                <Badge tone={result.grounded ? "success" : "danger"}>{Math.round(result.grounding_score * 100)}% grounded</Badge>
                <Badge>{result.cached ? "cache hit" : "fresh"}</Badge>
                <Badge>{result.total_latency_ms.toFixed(1)} ms total</Badge>
                <Badge tone={result.citation_integrity ? "success" : "danger"}>
                  {result.citation_integrity ? "citations checked" : "citation rejected"}
                </Badge>
                {result.fallback_used && <Badge tone="warning">provider fallback</Badge>}
                {result.degraded_mode && <Badge tone="danger">degraded</Badge>}
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
        <article className="panel evidence">
          <div className="section-title"><div><p>Retrieval</p><h2>Similar cases</h2></div><Badge>{result?.retrieved_cases.length ?? 0} found</Badge></div>
          <CaseList cases={result?.retrieved_cases ?? []} />
        </article>
      </section>
      <section className="panel inline-trace">
        <div className="section-title">
          <div><p>Execution evidence</p><h2>Seven-node execution trace</h2></div>
          <Badge>{result?.trace.length ?? 0} / 7 complete</Badge>
        </div>
        <TraceList trace={result?.trace ?? []} />
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
