import type { Evaluation, SimilarCase, TriageResult } from "../types/api";

const API_URL = import.meta.env.VITE_API_URL ?? "";

export class ApiResponseError extends Error {
  constructor(message: string, readonly status: number) {
    super(message);
    this.name = "ApiResponseError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new ApiResponseError(detail || `Request failed: ${response.status}`, response.status);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<Record<string, unknown>>("/health"),
  triage: (message: string, topK: number, signal?: AbortSignal) =>
    request<TriageResult>("/triage", {
      method: "POST",
      body: JSON.stringify({ message, top_k: topK }),
      signal,
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
