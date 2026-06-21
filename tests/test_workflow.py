from src.graph.workflow import TriageWorkflow
from src.llm.base import LLMRequest, ProviderResponse
from src.retrieval.retriever import SearchResult


class FakeRouter:
    def generate(
        self,
        request: LLMRequest,
        preferred_provider: str | None = None,
    ) -> ProviderResponse:
        responses = {
            "classify_intent": '{"intent":"delivery_issue","confidence":0.96}',
            "detect_urgency": (
                '{"urgency":"high","escalate":true,'
                '"escalation_reason":"Unresolved delivery and refund request"}'
            ),
            "generate_response": (
                '{"suggested_response":"Please share your order ID so we can review delivery '
                'status and refund options."}'
            ),
            "grounding_check": (
                '{"grounded":true,"grounding_score":0.88,'
                '"unsupported_claims":[],"confidence":0.9}'
            ),
        }
        return ProviderResponse(
            text=responses[request.task],
            provider="mock",
            model="mock-small",
        )


class FakeRetriever:
    def search(
        self,
        query: str,
        top_k: int,
        intent: str | None = None,
    ) -> list[SearchResult]:
        return [
            SearchResult(
                ticket_id="case-1",
                message="A delayed order needs refund review.",
                intent="delivery_issue",
                response="Ask for the order ID.",
                source="public_dataset",
                score=0.91,
                created_at=None,
                metadata={},
            )
        ]


def test_workflow_runs_required_nodes_in_order() -> None:
    workflow = TriageWorkflow(router=FakeRouter(), retriever=FakeRetriever())

    result = workflow.run(
        "  My order has not arrived and I want a refund now.  ",
        top_k=5,
    )

    assert result["intent"] == "delivery_issue"
    assert result["urgency"] == "high"
    assert result["escalate"] is True
    assert result["next_action"] == "ask_for_order_id"
    assert result["grounded"] is True
    assert [step["node"] for step in result["trace"]] == [
        "normalize_message",
        "classify_intent",
        "detect_urgency",
        "retrieve_similar_cases",
        "generate_support_response",
        "grounding_check",
        "suggest_next_action",
    ]


def test_workflow_trace_exposes_safe_node_metadata() -> None:
    workflow = TriageWorkflow(router=FakeRouter(), retriever=FakeRetriever())

    result = workflow.run("  My card has not arrived.  ", top_k=3)

    assert result["normalized_message"] == "My card has not arrived."
    assert result["total_latency_ms"] >= 0
    assert result["intent_confidence"] == 0.96
    assert all(
        {
            "node",
            "status",
            "duration_ms",
            "input_summary",
            "output_summary",
            "component",
            "cache_hit",
            "fallback",
            "degraded_mode",
        }.issubset(step)
        for step in result["trace"]
    )
    retrieval = result["trace"][3]
    assert retrieval["retrieved_document_count"] == 1
    assert retrieval["component"] == "qdrant"
