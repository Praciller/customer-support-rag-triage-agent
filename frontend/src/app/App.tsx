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
      const serverTimedOut =
        caught instanceof ApiResponseError && [408, 504].includes(caught.status);
      let message = "Triage failed unexpectedly. Check the API status before retrying manually.";
      let canRetry = true;
      if (didTimeout) {
        message = "Triage timed out after 60 seconds. The backend may still be starting or processing this request. It may finish after the timeout; wait before retrying, or choose Retry triage manually.";
      } else if (serverTimedOut) {
        message = "The backend timed out while processing triage. It may still be starting or finishing this request; wait before retrying, or choose Retry triage manually.";
      } else if (caught instanceof ApiResponseError && caught.status === 422) {
        message = "The backend rejected this message as invalid. Edit the message, then run triage again.";
        canRetry = false;
      } else if (caught instanceof ApiResponseError && caught.status === 429) {
        message = "The backend is rate limiting triage requests. Wait before choosing Retry triage manually.";
      } else if (caught instanceof ApiResponseError && [502, 503].includes(caught.status)) {
        message = `The backend is temporarily unavailable (HTTP ${caught.status}). Check its status, wait briefly, then choose Retry triage manually.`;
      } else if (caught instanceof ApiResponseError && caught.status >= 500) {
        message = `The backend returned an error (HTTP ${caught.status}). Check its status, then retry manually if appropriate.`;
      } else if (caught instanceof ApiResponseError) {
        message = `The backend rejected the request (HTTP ${caught.status}). Check the message and service access before running triage again.`;
        canRetry = false;
      } else if (caught instanceof TypeError) {
        message = "Could not reach the backend. Check your connection and API status, then choose Retry triage manually.";
      }
      setError(message);
      setRetryAvailable(canRetry);
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
