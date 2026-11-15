import type { Evaluation, TriageResult } from "../types/api";

export function makeTriageResult(overrides: Partial<TriageResult> = {}): TriageResult {
  const traceNodes = [
    "normalize_message",
    "classify_intent",
    "detect_urgency",
    "retrieve_similar_cases",
    "generate_support_response",
    "policy_gate",
    "suggest_next_action",
  ];

  const base: TriageResult = {
    normalized_message: "My card has not arrived.",
    intent: "delivery_issue",
    urgency: "medium",
    escalate: false,
    escalation_reason: "",
    suggested_response: "Thanks for reaching out. A support specialist needs to review this before we can advise on next steps.",
    retrieved_cases: [
      {
        ticket_id: "demo-delivery",
        evidence_type: "similar_past_case",
        approved_policy: false,
        message: "Where is the card I ordered?",
        intent: "delivery_issue",
        response: "",
        source: "mteb/banking77",
        score: 0.91,
        metadata: {},
      },
    ],
    similar_case_references: ["demo-delivery"],
    policy_status: "no_approved_policy",
    proposal_checks: [
      {
        proposal_id: "proposal-1",
        status: "no_approved_policy",
        policy_references: [],
        verification_result: "not_run",
        verification_method: "not_run",
      },
      {
        proposal_id: "proposal-2",
        status: "no_approved_policy",
        policy_references: [],
        verification_result: "not_run",
        verification_method: "not_run",
      },
    ],
    verified_proposals: [],
    policy_references: [],
    next_action: "manual_review",
    provider_used: "mock",
    model_used: "mock-small",
    cached: false,
    fallback_used: false,
    degraded_mode: false,
    total_latency_ms: 18.4,
    trace: traceNodes.map((node) => ({
      node,
      detail: `${node} complete`,
      duration_ms: 1,
      status: "completed",
      input_summary: "bounded input",
      output_summary: "bounded output",
      component: "local",
      provider: node.includes("intent") ? "mock" : null,
      model: node.includes("intent") ? "mock-small" : null,
      cache_hit: false,
      fallback: false,
      degraded_mode: false,
      retrieved_document_count: node === "retrieve_similar_cases" ? 1 : 0,
      policy_status: node === "policy_gate" ? "no_approved_policy" : null,
      similar_case_references: node === "retrieve_similar_cases" ? ["demo-delivery"] : [],
      policy_references: [],
      error_category: null,
    })),
  };

  return { ...base, ...overrides };
}

export function makeEvaluation(overrides: Partial<Evaluation> = {}): Evaluation {
  const base: Evaluation = {
    evaluation_mode: "deterministic_mock",
    top_k: 5,
    retrieval_precision_at_k: 0.8,
    retrieval_recall_at_k: 1,
    retrieval_mrr: 0.9,
    retrieval_ndcg_at_k: 0.92,
    intent_accuracy: 0.875,
    intent_macro_f1: 0.84,
    urgency_accuracy: 1,
    policy_review: {
      method: "structural_policy_gate_counts",
      sample_size: 8,
      no_approved_policy_cases: 8,
      manual_review_routes: 8,
      proposals_seen: 10,
      proposals_withheld: 10,
      verified_proposals: 0,
      no_policy_abstentions_satisfy_structural_invariants: true,
    },
    workflow_success_rate: 1,
    cache_hit_rate: 0,
    average_latency_ms: 20,
    p50_latency_ms: 18,
    p95_latency_ms: 31,
    fallback_count: 0,
    provider_usage: { mock: 8 },
    classification: {
      intent: {
        labels: ["delivery_issue"],
        per_class: {
          delivery_issue: { precision: 1, recall: 0.5, f1: 0.67, support: 2 },
        },
        confusion_matrix: [[1]],
      },
    },
    limitations: ["Small deterministic fixture; not a production SLA."],
  };

  return { ...base, ...overrides };
}
