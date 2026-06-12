export type TraceStep = {
  node: string;
  detail: string;
  duration_ms: number;
  status: string;
};

export type SimilarCase = {
  ticket_id: string;
  message: string;
  intent: string;
  response: string;
  source: string;
  score: number;
  metadata: Record<string, unknown>;
};

export type TriageResult = {
  intent: string;
  urgency: string;
  escalate: boolean;
  escalation_reason: string;
  suggested_response: string;
  retrieved_cases: SimilarCase[];
  grounded: boolean;
  grounding_score: number;
  unsupported_claims: string[];
  confidence: number;
  next_action: string;
  provider_used: string;
  model_used: string;
  cached: boolean;
  degraded_mode: boolean;
  trace: TraceStep[];
};

export type Evaluation = {
  retrieval_precision_at_k?: number;
  retrieval_recall_at_k?: number;
  intent_accuracy?: number;
  urgency_accuracy?: number;
  groundedness_pass_rate?: number;
  average_latency_ms?: number;
  cache_hit_rate?: number;
  provider_usage?: Record<string, number>;
  fallback_count?: number;
  status?: string;
};
