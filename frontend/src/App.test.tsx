import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import { api } from "./api";

vi.mock("./api", () => ({
  api: {
    triage: vi.fn(),
    search: vi.fn(),
    evaluation: vi.fn(),
    providers: vi.fn(),
    dataset: vi.fn(),
  },
}));

beforeEach(() => vi.clearAllMocks());

describe("App", () => {
  it("renders the support triage workspace", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: /ticket triage/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /run triage/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /overview/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /dataset explorer/i })).toBeInTheDocument();
  });

  it("labels deterministic demo mode and loads a fraud example", () => {
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: /suspicious transaction/i }));

    expect(screen.getByText(/deterministic demo/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/customer message/i)).toHaveValue(
      "A cash withdrawal was made from my account, but I did not make it. This is urgent.",
    );
  });

  it("renders a complete triage decision and seven-node trace", async () => {
    vi.mocked(api.triage).mockResolvedValue({
      normalized_message: "My card has not arrived.",
      intent: "delivery_issue",
      intent_confidence: 0.94,
      urgency: "medium",
      escalate: false,
      escalation_reason: "",
      suggested_response: "Please share the card delivery reference.",
      retrieved_cases: [
        {
          ticket_id: "demo-delivery",
          message: "Where is the card I ordered?",
          intent: "delivery_issue",
          response: "",
          source: "mteb/banking77",
          score: 0.91,
          metadata: {},
        },
      ],
      grounded: true,
      grounding_score: 0.86,
      unsupported_claims: [],
      confidence: 0.88,
      next_action: "ask_for_order_id",
      provider_used: "mock",
      model_used: "mock-small",
      cached: false,
      fallback_used: false,
      degraded_mode: false,
      total_latency_ms: 18.4,
      trace: [
        "normalize_message",
        "classify_intent",
        "detect_urgency",
        "retrieve_similar_cases",
        "generate_support_response",
        "grounding_check",
        "suggest_next_action",
      ].map((node) => ({
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
        grounding_result: node === "grounding_check" ? true : null,
        error_category: null,
      })),
    });
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: /run triage/i }));

    expect(await screen.findByText("My card has not arrived.")).toBeInTheDocument();
    expect(screen.getByText(/18\.4 ms total/i)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /seven-node execution trace/i })).toBeInTheDocument();
    expect(screen.getByText(/7\. suggest next action/i)).toBeInTheDocument();
  });

  it("renders measured evaluation methodology and per-class results", async () => {
    vi.mocked(api.evaluation).mockResolvedValue({
      evaluation_mode: "deterministic_mock",
      retrieval_precision_at_k: 0.8,
      retrieval_recall_at_k: 1,
      retrieval_mrr: 0.9,
      retrieval_ndcg_at_k: 0.92,
      intent_accuracy: 0.875,
      intent_macro_f1: 0.84,
      urgency_accuracy: 1,
      groundedness_pass_rate: 1,
      workflow_success_rate: 1,
      unsupported_claim_rate: 0,
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
    });
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: /^evaluation$/i }));

    expect(await screen.findByText(/deterministic mock/i)).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: /precision/i })).toBeInTheDocument();
    expect(screen.getByText(/small deterministic fixture/i)).toBeInTheDocument();
  });
});
