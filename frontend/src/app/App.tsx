import { useEffect, useState } from "react";

import { api } from "../api";
import type { TriageResult } from "../types";
import { DatasetView } from "../features/dataset/DatasetView";
import { EvaluationView } from "../features/evaluation/EvaluationView";
import { OverviewView } from "../features/overview/OverviewView";
import { ProviderView } from "../features/providers/ProviderView";
import { SearchView } from "../features/search/SearchView";
import { sampleTicketMessage } from "../features/triage/TicketComposer";
import { TriageView } from "../features/triage/TriageView";
import { TraceView } from "../features/trace/TraceView";
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

