import { useEffect, useState } from "react";

import { ApiResponseError, api } from "../lib/api";
import type { TriageResult } from "../types/api";
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

const TRIAGE_TIMEOUT_MS = 60_000;

export default function App() {
  const [view, setView] = useState<View>("triage");
  const [message, setMessage] = useState<string>(sampleTicketMessage);
  const [result, setResult] = useState<TriageResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [retryAvailable, setRetryAvailable] = useState(false);
  const [apiStatus, setApiStatus] = useState<"checking" | "connected" | "unavailable">(
    "checking",
  );

  useEffect(() => {
    api.health()
      .then(() => setApiStatus("connected"))
      .catch(() => setApiStatus("unavailable"));
  }, []);

  async function runTriage() {
    if (!message.trim() || loading) return;
    setLoading(true);
    setError("");
    setResult(null);
    setRetryAvailable(false);
    const controller = new AbortController();
    let didTimeout = false;
    let timeoutId: number | undefined;
    const timeout = new Promise<never>((_, reject) => {
      timeoutId = window.setTimeout(() => {
        didTimeout = true;
        controller.abort();
        reject(new Error("Triage request timed out."));
      }, TRIAGE_TIMEOUT_MS);
    });
    try {
      const data = await Promise.race([
        api.triage(message, 5, controller.signal),
        timeout,
      ]);
      setResult(data);
    } catch (caught) {
      const serverTimedOut = caught instanceof ApiResponseError && caught.status === 504;
      setError(didTimeout
        ? "Triage timed out after 60 seconds. The backend may still be starting or processing this request. It may finish after the timeout; wait before retrying, or choose Retry triage manually."
        : serverTimedOut
          ? "The backend timed out while processing triage. It may still be starting or finishing this request; wait before retrying, or choose Retry triage manually."
          : "Triage could not be completed. The backend may be starting after an idle period. Check its status, then choose Retry triage manually.");
      setRetryAvailable(true);
    } finally {
      if (timeoutId !== undefined) window.clearTimeout(timeoutId);
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
            retryAvailable={retryAvailable}
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
