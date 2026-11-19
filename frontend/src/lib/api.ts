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
  triage: async (message: string, topK: number, signal?: AbortSignal) => {
    const result = await request<TriageResult>("/triage", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-ResolveOps-API-Version": "2" },
      body: JSON.stringify({ message, top_k: topK }),
      signal,
    });
    if (
      !result || typeof result !== "object"
      || typeof result.policy_status !== "string"
      || !Array.isArray(result.proposal_checks)
      || !Array.isArray(result.verified_proposals)
      || !Array.isArray(result.policy_references)
      || !Array.isArray(result.similar_case_references)
      || "grounded" in result || "grounding_score" in result
    ) {
      throw new ApiResponseError("API version mismatch. Reload after the coordinated release.", 426);
    }
    return result;
  },
  search: (message: string, topK: number, intent?: string) =>
    request<SimilarCase[]>("/search-similar", {
      method: "POST",
      body: JSON.stringify({ message, top_k: topK, intent: intent || null }),
    }),
  evaluation: async () => {
    const result = await request<Evaluation>("/eval/results");
    if (result?.status === "not_evaluated" || result?.status === "unavailable") return result;
    if (result?.policy_review?.method !== "structural_policy_gate_counts") {
      throw new ApiResponseError("Compatible API v2 evaluation results are unavailable.", 426);
    }
    return result;
  },
  providers: () => request<Record<string, unknown>>("/provider-health"),
  dataset: () => request<Record<string, unknown>>("/dataset-info"),
};
