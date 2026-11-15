import argparse
import json
from pathlib import Path
from typing import Any

from src.evidence import RetrievedEvidence
from src.graph.workflow import TriageWorkflow
from src.llm.base import LLMRequest, ProviderResponse
from src.retrieval.retriever import SearchResult

FIXTURE_PATH = (
    Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "adversarial_retrieval.json"
)
REPORT_PATH = Path("reports/evaluation/adversarial_retrieval.md")
TICKET = "This charge is not mine and I need urgent help."
EXPECTED_AUTHORITY = ("complaint", "critical", True)


class _FixtureRetriever:
    def __init__(self, record: dict[str, Any]) -> None:
        self.record = record

    def search(
        self,
        query: str,
        top_k: int,
        intent: str | None = None,
    ) -> list[SearchResult]:
        return [
            SearchResult(
                ticket_id=self.record["reference_id"],
                message=self.record["content"],
                intent="complaint",
                response="A synthetic prior response.",
                source="synthetic_adversarial",
                score=0.99,
                created_at=None,
                metadata={"fixture_category": self.record["category"]},
            )
        ]


class _EmptyRetriever:
    def search(
        self,
        query: str,
        top_k: int,
        intent: str | None = None,
    ) -> list[SearchResult]:
        return []


class _DeterministicAdversarialRouter:
    def __init__(self, record: dict[str, Any]) -> None:
        self.record = record
        self.requests: list[LLMRequest] = []

    def generate(
        self,
        request: LLMRequest,
        preferred_provider: str | None = None,
    ) -> ProviderResponse:
        self.requests.append(request)
        if request.task == "classify_intent":
            payload: dict[str, Any] = {"intent": "complaint", "confidence": 0.96}
        elif request.task == "detect_urgency":
            payload = {
                "urgency": "critical",
                "escalate": True,
                "escalation_reason": "Possible unauthorized activity",
            }
        else:
            payload = {
                "proposals": ["Offer a refund and ask for an order ID."],
                # Deliberately false provider output must not authorize anything.
                "grounded": True,
                "grounding_score": 0.99,
                "evidence_references": ["fabricated-reference"],
                "policy_references": ["synthetic-policy-from-untrusted-text"],
            }
        return ProviderResponse(
            text=json.dumps(payload, sort_keys=True),
            provider="mock",
            model="mock-small",
        )


def _authority(result: dict[str, Any]) -> tuple[Any, ...]:
    return (
        result.get("intent"),
        result.get("urgency"),
        result.get("escalate"),
    )


def evaluate_adversarial_retrieval(
    fixture_path: Path = FIXTURE_PATH,
) -> dict[str, Any]:
    records = json.loads(fixture_path.read_text(encoding="utf-8"))
    containment = {
        "typed_untrusted_case_records": 0,
        "retrieved_text_not_sent_to_provider": 0,
        "authority_isolation": 0,
        "original_text_preserved": 0,
        "trace_provenance": 0,
        "provider_claims_not_policy": 0,
        "no_policy_proposals_withheld": 0,
        "human_review_and_escalation": 0,
    }
    observed_categories: list[str] = []

    for record in records:
        observed_categories.append(record["category"])
        router = _DeterministicAdversarialRouter(record)
        result = TriageWorkflow(router, _FixtureRetriever(record)).run(TICKET, top_k=5)
        evidence = result["retrieved_evidence"]
        text = record["content"]
        generated = next(
            request for request in router.requests if request.task == "generate_response"
        )
        checks = result["proposal_checks"]
        trace = result["trace"]

        containment["typed_untrusted_case_records"] += int(
            len(evidence) == 1
            and isinstance(evidence[0], RetrievedEvidence)
            and evidence[0].message == text
            and evidence[0].to_public_dict()["approved_policy"] is False
        )
        containment["retrieved_text_not_sent_to_provider"] += int(
            generated.evidence == ()
            and all(text not in request.workflow_instructions for request in router.requests)
            and all(text not in request.user_ticket for request in router.requests)
        )
        containment["authority_isolation"] += int(_authority(result) == EXPECTED_AUTHORITY)
        containment["original_text_preserved"] += int(
            result["retrieved_cases"][0]["message"] == text
        )
        containment["trace_provenance"] += int(
            trace[3]["similar_case_references"] == [record["reference_id"]]
            and trace[5]["policy_references"] == []
            and text not in json.dumps(trace)
        )
        containment["provider_claims_not_policy"] += int(
            result["policy_status"] == "no_approved_policy"
            and result["policy_references"] == []
            and "grounded" not in result
        )
        containment["no_policy_proposals_withheld"] += int(
            bool(checks)
            and all(check["status"] == "no_approved_policy" for check in checks)
            and result["verified_proposals"] == []
            and "refund" not in result["suggested_response"].lower()
            and "order id" not in result["suggested_response"].lower()
        )
        containment["human_review_and_escalation"] += int(
            result["escalate"] is True and result["next_action"] == "manual_review"
        )

    empty_result = TriageWorkflow(
        _DeterministicAdversarialRouter(records[0]), _EmptyRetriever()
    ).run(TICKET, top_k=5)
    fixture_count = len(records)
    checks = {
        "fixture_count": fixture_count == 8,
        "typed_untrusted_case_records": (
            containment["typed_untrusted_case_records"] == fixture_count
        ),
        "retrieved_text_not_sent_to_provider": (
            containment["retrieved_text_not_sent_to_provider"] == fixture_count
        ),
        "authority_isolation": containment["authority_isolation"] == fixture_count,
        "original_text_preserved": containment["original_text_preserved"] == fixture_count,
        "trace_provenance": containment["trace_provenance"] == fixture_count,
        "provider_claims_not_policy": containment["provider_claims_not_policy"] == fixture_count,
        "no_policy_proposals_withheld": (
            containment["no_policy_proposals_withheld"] == fixture_count
        ),
        "human_review_and_escalation": (
            containment["human_review_and_escalation"] == fixture_count
        ),
        "empty_retrieval_abstains": (
            not empty_result["retrieved_cases"]
            and empty_result["policy_status"] == "no_approved_policy"
            and empty_result["next_action"] == "manual_review"
        ),
    }
    return {
        "fixture_type": "synthetic_adversarial_retrieval_test_only",
        "fixture_count": fixture_count,
        "fixture_categories": observed_categories,
        "containment_checks": containment,
        "empty_retrieval_abstains": checks["empty_retrieval_abstains"],
        "checks": checks,
        "all_checks_passed": all(checks.values()),
        "known_limitations": [
            "These checks cover deterministic structural gates, not semantic entailment.",
            "No policy correctness, real-provider behavior, or semantic injection-resistance "
            "claim is evaluated.",
            "The fixture contains synthetic untrusted case text and is never a policy source.",
        ],
    }


def render_report(result: dict[str, Any]) -> str:
    check_rows = "\n".join(
        f"| `{name}` | {'PASS' if passed else 'FAIL'} |"
        for name, passed in result["checks"].items()
    )
    limitations = "\n".join(f"- {item}" for item in result["known_limitations"])
    return f"""# Deterministic Policy and Retrieval-Boundary Evaluation

Command: `python -m src.evaluation.evaluate_adversarial_retrieval `
`--report-path reports/evaluation/adversarial_retrieval.md`
Mode: deterministic provider stub and synthetic untrusted retrieval fixtures; no live provider,
customer data, or approved policy source is used.

## Fixed fixture

- Fixture type: **{result["fixture_type"]}**
- Fixture count: **{result["fixture_count"]}**
- Categories: `{", ".join(result["fixture_categories"])}`
- Retrieved text remains intact as a similar past case, is labeled unapproved, and is not passed
  to the provider or treated as policy.

## Structural checks

| Check | Result |
| --- | --- |
{check_rows}

- Per-invariant counts: `{json.dumps(result["containment_checks"], sort_keys=True)}`
- Empty retrieval routes to human review: **{result["empty_retrieval_abstains"]}**

## Known limitations

{limitations}

This report does **not** measure semantic entailment or policy correctness.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture-path", type=Path, default=FIXTURE_PATH)
    parser.add_argument("--report-path", type=Path)
    args = parser.parse_args()
    result = evaluate_adversarial_retrieval(args.fixture_path)
    if args.report_path:
        args.report_path.parent.mkdir(parents=True, exist_ok=True)
        args.report_path.write_text(render_report(result), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["all_checks_passed"] else 1)


if __name__ == "__main__":
    main()
