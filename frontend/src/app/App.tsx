import { useEffect, useState } from "react";

import { api } from "../api";
import { Badge } from "../components";
import type { TriageResult } from "../types";
import { OverviewView } from "../features/overview/OverviewView";
import { SearchView } from "../features/search/SearchView";
import { sampleTicketMessage } from "../features/triage/TicketComposer";
import { TriageView } from "../features/triage/TriageView";
import { TraceView } from "../features/trace/TraceView";
import { EvaluationView } from "../features/evaluation/EvaluationView";
import { type View } from "./navigation";
import { AppShell } from "./shell/AppShell";

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
