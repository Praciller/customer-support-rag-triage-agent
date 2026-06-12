import type { Evaluation, SimilarCase, TriageResult } from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  triage: (message: string, topK: number) =>
    request<TriageResult>("/triage", {
      method: "POST",
      body: JSON.stringify({ message, top_k: topK }),
    }),
  search: (message: string, topK: number, intent?: string) =>
    request<SimilarCase[]>("/search-similar", {
      method: "POST",
      body: JSON.stringify({ message, top_k: topK, intent: intent || null }),
    }),
  evaluation: () => request<Evaluation>("/eval/results"),
  providers: () => request<Record<string, unknown>>("/provider-health"),
  dataset: () => request<Record<string, unknown>>("/dataset-info"),
};
