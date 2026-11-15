import json

import pytest

from src.api.schemas import TriageResponse
from src.graph.workflow import TriageWorkflow
from src.llm.base import LLMRequest, ProviderResponse
from src.policy import SAFE_ABSTENTION_RESPONSE, ProposalVerification
from src.retrieval.retriever import SearchResult

SYNTHETIC_POLICY_REFERENCE = "synthetic-test-policy-delivery-01"


class FakeRouter:
    def __init__(self) -> None:
        self.requests: list[LLMRequest] = []

    def generate(
        self,
        request: LLMRequest,
        preferred_provider: str | None = None,
    ) -> ProviderResponse:
        self.requests.append(request)
        if request.task == "classify_intent":
            payload = {"intent": "delivery_issue", "confidence": 0.96}
        elif request.task == "detect_urgency":
            payload = {
                "urgency": "high" if "urgent" in request.user_ticket.lower() else "medium",
                "escalate": "urgent" in request.user_ticket.lower(),
                "escalation_reason": "Customer says urgent"
                if "urgent" in request.user_ticket.lower()
                else "",
            }
        elif request.task == "generate_response":
            payload = {
                "proposals": [
                    "Ask for the order ID to review delivery status.",
                    "Offer available refund options.",
                ],
                # These provider claims are deliberately untrusted and ignored.
                "grounded": True,
                "grounding_score": 0.86,
                "evidence_references": ["case-1"],
                "policy_references": ["fabricated-provider-policy-reference"],
            }
        else:
            pytest.fail(f"unexpected inference task: {request.task}")
        return ProviderResponse(
            text=json.dumps(payload),
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


def test_similar_cases_and_provider_citations_do_not_count_as_policy() -> None:
    router = FakeRouter()
    result = TriageWorkflow(router=router, retriever=FakeRetriever()).run(
        "My card has not arrived and I travel tomorrow.", top_k=5
    )

    generation_request = next(
        request for request in router.requests if request.task == "generate_response"
    )
    assert result["retrieved_cases"]
    assert result["similar_case_references"] == ["case-1"]
    assert generation_request.evidence == ()
    assert result["policy_status"] == "no_approved_policy"
    assert result["proposal_checks"] == [
        {
            "proposal_id": "proposal-1",
            "status": "no_approved_policy",
            "policy_references": [],
            "verification_result": "not_run",
            "verification_method": "not_run",
        },
        {
            "proposal_id": "proposal-2",
            "status": "no_approved_policy",
            "policy_references": [],
            "verification_result": "not_run",
            "verification_method": "not_run",
        },
    ]
    assert result["verified_proposals"] == []
    assert result["policy_references"] == []
    assert result["next_action"] == "manual_review"
    assert "refund" not in result["suggested_response"].lower()
    assert "order id" not in result["suggested_response"].lower()
    assert "grounded" not in result
    assert "grounding_score" not in result


def test_workflow_runs_seven_nodes_and_traces_policy_and_case_references() -> None:
    result = TriageWorkflow(router=FakeRouter(), retriever=FakeRetriever()).run(
        "My card has not arrived.", top_k=3
    )

    assert result["intent"] == "delivery_issue"
    assert result["urgency"] == "medium"
    assert result["policy_status"] == "no_approved_policy"
    assert result["total_latency_ms"] >= 0
    assert [step["node"] for step in result["trace"]] == [
        "normalize_message",
        "classify_intent",
        "detect_urgency",
        "retrieve_similar_cases",
        "generate_support_response",
        "policy_gate",
        "suggest_next_action",
    ]
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
            "policy_status",
            "similar_case_references",
            "policy_references",
        }.issubset(step)
        for step in result["trace"]
    )
    assert result["trace"][3]["similar_case_references"] == ["case-1"]
    assert result["trace"][5]["policy_status"] == "no_approved_policy"


def test_empty_retrieval_still_abstains_and_preserves_full_workflow() -> None:
    result = TriageWorkflow(router=FakeRouter(), retriever=EmptyRetriever()).run(
        "My card has not arrived.", top_k=3
    )

    assert result["retrieved_cases"] == []
    assert result["policy_status"] == "no_approved_policy"
    assert result["next_action"] == "manual_review"
    assert result["verified_proposals"] == []
    assert len(result["trace"]) == 7


def test_supported_synthetic_policy_check_is_returned_per_proposal() -> None:
    router = FakeRouter()
    workflow = TriageWorkflow(
        router=router,
        retriever=FakeRetriever(),
        approved_policy_references={SYNTHETIC_POLICY_REFERENCE},
        policy_verifier=lambda _: ProposalVerification(
            status="supported",
            policy_references=(SYNTHETIC_POLICY_REFERENCE,),
            verification_result="passed",
            verification_method="synthetic_test_verifier",
        ),
    )

    result = workflow.run("My card has not arrived.", top_k=3)

    assert result["policy_status"] == "verified"
    assert len(result["proposal_checks"]) == 2
    assert all(check["status"] == "supported" for check in result["proposal_checks"])
    assert len(result["verified_proposals"]) == 2
    assert all(
        proposal["policy_references"] == [SYNTHETIC_POLICY_REFERENCE]
        and proposal["verification_result"] == "passed"
        and proposal["verification_method"] == "synthetic_test_verifier"
        for proposal in result["verified_proposals"]
    )
    assert result["next_action"] == "reply_to_customer"


def test_provider_claimed_policy_reference_is_ignored_with_host_verifier() -> None:
    approved_reference = "synthetic-approved-policy-delivery-01"
    result = TriageWorkflow(
        router=FakeRouter(),
        retriever=FakeRetriever(),
        approved_policy_references={approved_reference},
        policy_verifier=lambda _: ProposalVerification(
            status="supported",
            policy_references=(approved_reference,),
            verification_result="passed",
            verification_method="synthetic_test_verifier",
        ),
    ).run("My card has not arrived.", top_k=3)

    assert result["policy_status"] == "verified"
    assert result["policy_references"] == [approved_reference]
    assert "fabricated" not in str(result["policy_references"])
    assert all(
        check["policy_references"] == [approved_reference] for check in result["proposal_checks"]
    )


def test_string_policy_configuration_is_not_split_into_authority_ids() -> None:
    verifier_called = False

    def verifier(_: str) -> ProposalVerification:
        nonlocal verifier_called
        verifier_called = True
        return ProposalVerification(
            status="supported",
            policy_references=("p",),
            verification_result="passed",
            verification_method="synthetic_test_verifier",
        )

    result = TriageWorkflow(
        router=FakeRouter(),
        retriever=FakeRetriever(),
        approved_policy_references="policy-A",
        policy_verifier=verifier,
    ).run("My card has not arrived.", top_k=3)

    assert result["policy_status"] == "no_approved_policy"
    assert result["verified_proposals"] == []
    assert result["suggested_response"] == SAFE_ABSTENTION_RESPONSE
    assert verifier_called is False


@pytest.mark.parametrize(
    ("failed_status", "verification_result"),
    [
        ("unsupported", "failed"),
        ("conflicting", "failed"),
        ("uncertain", "uncertain"),
    ],
)
def test_mixed_proposal_results_abstain_and_validate_as_api_response(
    failed_status: str,
    verification_result: str,
) -> None:
    calls = 0

    def mixed_verifier(_: str) -> ProposalVerification:
        nonlocal calls
        calls += 1
        return ProposalVerification(
            status="supported" if calls == 1 else failed_status,  # type: ignore[arg-type]
            policy_references=(SYNTHETIC_POLICY_REFERENCE,),
            verification_result=("passed" if calls == 1 else verification_result),  # type: ignore[arg-type]
            verification_method="synthetic_test_verifier",
        )

    result = TriageWorkflow(
        router=FakeRouter(),
        retriever=FakeRetriever(),
        approved_policy_references={SYNTHETIC_POLICY_REFERENCE},
        policy_verifier=mixed_verifier,
    ).run("My card has not arrived.", top_k=3)

    assert result["policy_status"] == failed_status
    assert result["verified_proposals"] == []
    assert result["next_action"] == "manual_review"
    assert result["suggested_response"] == SAFE_ABSTENTION_RESPONSE
    assert result["policy_references"] == []
    TriageResponse.model_validate(result)


def test_invalid_policy_reference_abstains() -> None:
    result = TriageWorkflow(
        router=FakeRouter(),
        retriever=FakeRetriever(),
        approved_policy_references={SYNTHETIC_POLICY_REFERENCE},
        policy_verifier=lambda _: ProposalVerification(
            status="supported",
            policy_references=("fabricated-policy-reference",),
            verification_result="passed",
            verification_method="synthetic_test_verifier",
        ),
    ).run("My card has not arrived.", top_k=3)

    assert result["policy_status"] == "verification_failed"
    assert all(check["status"] == "verification_failed" for check in result["proposal_checks"])
    assert result["verified_proposals"] == []
    assert result["policy_references"] == []
    assert result["next_action"] == "manual_review"


def test_verifier_exception_abstains() -> None:
    def failing_verifier(_: str) -> ProposalVerification:
        raise RuntimeError("synthetic verifier failure")

    result = TriageWorkflow(
        router=FakeRouter(),
        retriever=FakeRetriever(),
        approved_policy_references={SYNTHETIC_POLICY_REFERENCE},
        policy_verifier=failing_verifier,
    ).run("My card has not arrived.", top_k=3)

    assert result["policy_status"] == "verification_failed"
    assert all(check["verification_result"] == "failed" for check in result["proposal_checks"])
    assert result["next_action"] == "manual_review"
    assert "order id" not in result["suggested_response"].lower()


def test_degraded_classification_remains_degraded_and_routes_to_review() -> None:
    class DegradedClassificationRouter(FakeRouter):
        def generate(
            self, request: LLMRequest, preferred_provider: str | None = None
        ) -> ProviderResponse:
            response = super().generate(request, preferred_provider)
            if request.task == "classify_intent":
                return ProviderResponse(
                    text=response.text,
                    provider="mock",
                    model=response.model,
                    degraded_mode=True,
                    fallback_used=True,
                )
            return response

    result = TriageWorkflow(router=DegradedClassificationRouter(), retriever=FakeRetriever()).run(
        "My card has not arrived.", top_k=3
    )

    assert result["degraded_mode"] is True
    assert result["fallback_used"] is True
    assert result["policy_status"] == "no_approved_policy"
    assert result["next_action"] == "manual_review"
    assert result["trace"][1]["degraded_mode"] is True


@pytest.mark.parametrize(
    ("policy_status", "urgency", "verified_proposals", "expected"),
    [
        ("no_approved_policy", "medium", [], "manual_review"),
        ("uncertain", "medium", [], "manual_review"),
        ("verified", "critical", [{"proposal_id": "p1"}], "escalate_to_human"),
        ("verified", "medium", [{"proposal_id": "p1"}], "reply_to_customer"),
    ],
)
def test_policy_gate_precedes_next_action_rules(
    policy_status: str,
    urgency: str,
    verified_proposals: list[dict[str, str]],
    expected: str,
) -> None:
    workflow = TriageWorkflow(router=FakeRouter(), retriever=FakeRetriever())
    state = {
        "normalized_message": "My order has not arrived",
        "intent": "delivery_issue",
        "urgency": urgency,
        "escalate": urgency in {"high", "critical"},
        "policy_status": policy_status,
        "verified_proposals": verified_proposals,
        "trace": [],
    }

    outcome = workflow._suggest_next_action(state)

    assert outcome["next_action"] == expected
    assert outcome["trace"][-1]["node"] == "suggest_next_action"
