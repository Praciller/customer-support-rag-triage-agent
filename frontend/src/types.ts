export type TraceStep = {
  node: string;
  detail: string;
  duration_ms: number;
  status: string;
  input_summary: string;
  output_summary: string;
  component: string;
  provider: string | null;
  model: string | null;
  cache_hit: boolean;
  fallback: boolean;
  degraded_mode: boolean;
  retrieved_document_count: number;
  grounding_result: boolean | null;
  evidence_references: string[];
  error_category: string | null;
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
  normalized_message: string;
  intent: string;
  intent_confidence: number;
  urgency: string;
  escalate: boolean;
  escalation_reason: string;
  suggested_response: string;
  retrieved_cases: SimilarCase[];
  evidence_references: string[];
  citation_integrity: boolean;
  grounded: boolean;
  grounding_score: number;
  unsupported_claims: string[];
  confidence: number;
  next_action: string;
  provider_used: string;
  model_used: string;
  cached: boolean;
  fallback_used: boolean;
  degraded_mode: boolean;
  total_latency_ms: number;
  trace: TraceStep[];
};

export type Evaluation = {
  top_k?: number;
  retrieval_precision_at_k?: number;
  retrieval_recall_at_k?: number;
  intent_accuracy?: number;
  intent_macro_f1?: number;
  urgency_accuracy?: number;
  urgency_macro_f1?: number;
  groundedness_pass_rate?: number;
  average_latency_ms?: number;
  cache_hit_rate?: number;
  provider_usage?: Record<string, number>;
  fallback_count?: number;
  retrieval_mrr?: number;
  retrieval_ndcg_at_k?: number;
  retrieval_zero_result_rate?: number;
  unsupported_claim_rate?: number;
  degraded_mode_rate?: number;
  workflow_success_rate?: number;
  p50_latency_ms?: number;
  p95_latency_ms?: number;
  evaluation_mode?: string;
  dataset?: {
    sample_size?: number;
    retrieval_corpus_size?: number;
    fixture_revision?: string;
  };
  classification?: {
    intent?: {
      labels: string[];
      per_class: Record<string, { precision: number; recall: number; f1: number; support: number }>;
      confusion_matrix: number[][];
    };
  };
  limitations?: string[];
  status?: string;
};
