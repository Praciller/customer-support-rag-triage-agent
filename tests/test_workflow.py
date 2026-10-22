import json

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
            "generate_response": json.dumps(
                {
                    "suggested_response": (
                        "Please share your order ID so we can review delivery status "
                        "and refund options."
                    ),
                    "evidence_references": [item.reference_id for item in request.evidence],
                }
            ),
            "grounding_check": (
                '{"grounded":true,"grounding_score":0.88,"unsupported_claims":[],"confidence":0.9}'
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


class EmptyRetriever:
    def search(
        self,
        query: str,
        top_k: int,
        intent: str | None = None,
    ) -> list[SearchResult]:
        return []


def test_workflow_runs_required_nodes_in_order() -> None:
    workflow = TriageWorkflow(router=FakeRouter(), retriever=FakeRetriever())

    result = workflow.run(
        "  My order has not arrived and I want a refund now.  ",
        top_k=5,
    )

    assert result["intent"] == "delivery_issue"
    assert result["urgency"] == "high"
    assert result["escalate"] is True
    assert result["next_action"] == "escalate_to_human"
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


def test_workflow_cannot_mark_response_grounded_without_retrieved_evidence() -> None:
    workflow = TriageWorkflow(router=FakeRouter(), retriever=EmptyRetriever())

    result = workflow.run("My card has not arrived.", top_k=3)

    assert result["grounded"] is False
    assert result["grounding_score"] <= 0.25
    assert result["confidence"] <= 0.4
    assert result["unsupported_claims"] == ["No retrieved cases were available."]
    assert result["next_action"] == "manual_review"
    assert result["trace"][5]["grounding_result"] is False


def test_critical_delivery_escalates_before_requesting_order_id() -> None:
    class CriticalRouter(FakeRouter):
        def generate(
            self, request: LLMRequest, preferred_provider: str | None = None
        ) -> ProviderResponse:
            if request.task == "detect_urgency":
                return ProviderResponse(
                    text=json.dumps(
                        {
                            "urgency": "critical",
                            "escalate": "false",
                            "escalation_reason": "Urgent security risk",
                        }
                    ),
                    provider="mock",
                    model="mock-small",
                )
            return super().generate(request, preferred_provider)

    result = TriageWorkflow(router=CriticalRouter(), retriever=FakeRetriever()).run(
        "My order has not arrived and I suspect fraud", top_k=5
    )

    assert result["urgency"] == "critical"
    assert result["escalate"] is True
    assert result["next_action"] == "escalate_to_human"


def test_filtered_search_miss_retries_without_intent_filter() -> None:
    class FilterMissRetriever(FakeRetriever):
        def __init__(self) -> None:
            self.intents: list[str | None] = []

        def search(self, query: str, top_k: int, intent: str | None = None) -> list[SearchResult]:
            self.intents.append(intent)
            return [] if intent is not None else super().search(query, top_k, intent)

    retriever = FilterMissRetriever()
    result = TriageWorkflow(router=FakeRouter(), retriever=retriever).run(
        "My order has not arrived", top_k=5
    )

    assert retriever.intents == ["delivery_issue", None]
    assert result["retrieved_cases"]
    assert "unfiltered_fallback=true" in result["trace"][3]["output_summary"]


def test_missing_citations_do_not_automatically_cite_every_retrieved_case() -> None:
    class MissingCitationRouter(FakeRouter):
        def generate(
            self, request: LLMRequest, preferred_provider: str | None = None
        ) -> ProviderResponse:
            if request.task == "generate_response":
                return ProviderResponse(
                    text='{"suggested_response":"Please share your order ID."}',
                    provider="mock",
                    model="mock-small",
                )
            return super().generate(request, preferred_provider)

    result = TriageWorkflow(router=MissingCitationRouter(), retriever=FakeRetriever()).run(
        "My order has not arrived", top_k=5
    )

    assert result["evidence_references"] == []
    assert result["citation_integrity"] is False
    assert result["grounded"] is False
    assert result["next_action"] == "manual_review"


def test_invalid_grounding_payload_does_not_mark_response_grounded() -> None:
    class InvalidGroundingRouter(FakeRouter):
        def generate(
            self, request: LLMRequest, preferred_provider: str | None = None
        ) -> ProviderResponse:
            if request.task == "grounding_check":
                return ProviderResponse(
                    text=json.dumps(
                        {
                            "grounded": "false",
                            "grounding_score": "NaN",
                            "unsupported_claims": ["A claim has no support."],
                            "confidence": 0.9,
                        }
                    ),
                    provider="mock",
                    model="mock-small",
                )
            return super().generate(request, preferred_provider)

    result = TriageWorkflow(router=InvalidGroundingRouter(), retriever=FakeRetriever()).run(
        "My order has not arrived", top_k=5
    )

    assert result["grounded"] is False
    assert result["grounding_score"] == 0
    assert result["next_action"] == "manual_review"
    assert result["unsupported_claims"] == ["A claim has no support."]
