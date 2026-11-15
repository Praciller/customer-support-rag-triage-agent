"""Policy gate tests use synthetic verifier outputs, never demo policy data."""

import pytest

from src.policy import ProposalVerification, review_proposals

SYNTHETIC_POLICY_REFERENCE = "synthetic-test-policy-card-17"


@pytest.fixture
def synthetic_approved_policy_references() -> set[str]:
    # Test-only IDs. No file under data/demo or production code uses this value.
    return {SYNTHETIC_POLICY_REFERENCE}


def test_missing_approved_policy_withholds_each_proposal() -> None:
    result = review_proposals(
        ["Ask for an order ID.", "Offer a refund."],
        approved_policy_references=(),
        verifier=lambda _: pytest.fail("verifier must not run without approved policy"),
    )

    assert result.status == "no_approved_policy"
    assert [item.status for item in result.checks] == [
        "no_approved_policy",
        "no_approved_policy",
    ]
    assert all(item.verification_result == "not_run" for item in result.checks)
    assert result.verified_proposals == ()


def test_synthetic_supported_policy_requires_reference_and_passing_check(
    synthetic_approved_policy_references: set[str],
) -> None:
    result = review_proposals(
        ["Ask for a tracking reference."],
        approved_policy_references=synthetic_approved_policy_references,
        verifier=lambda _: ProposalVerification(
            status="supported",
            policy_references=(SYNTHETIC_POLICY_REFERENCE,),
            verification_result="passed",
            verification_method="synthetic_test_verifier",
        ),
    )

    assert result.status == "verified"
    assert len(result.verified_proposals) == 1
    proposal = result.verified_proposals[0]
    assert proposal.policy_references == (SYNTHETIC_POLICY_REFERENCE,)
    assert proposal.verification_result == "passed"
    assert proposal.verification_method == "synthetic_test_verifier"


@pytest.mark.parametrize(
    ("status", "verification_result"),
    [
        ("unsupported", "failed"),
        ("conflicting", "failed"),
        ("uncertain", "uncertain"),
    ],
)
def test_synthetic_non_supporting_policy_outcomes_withhold_all_proposals(
    status: str,
    verification_result: str,
    synthetic_approved_policy_references: set[str],
) -> None:
    result = review_proposals(
        ["Offer a refund."],
        approved_policy_references=synthetic_approved_policy_references,
        verifier=lambda _: ProposalVerification(
            status=status,  # type: ignore[arg-type]
            policy_references=(SYNTHETIC_POLICY_REFERENCE,),
            verification_result=verification_result,  # type: ignore[arg-type]
            verification_method="synthetic_test_verifier",
        ),
    )

    assert result.status == status
    assert result.checks[0].status == status
    assert result.verified_proposals == ()


def test_invalid_policy_reference_fails_closed(
    synthetic_approved_policy_references: set[str],
) -> None:
    result = review_proposals(
        ["Ask for an order ID."],
        approved_policy_references=synthetic_approved_policy_references,
        verifier=lambda _: ProposalVerification(
            status="supported",
            policy_references=("fabricated-policy-reference",),
            verification_result="passed",
            verification_method="synthetic_test_verifier",
        ),
    )

    assert result.status == "verification_failed"
    assert result.checks[0].status == "verification_failed"
    assert result.checks[0].policy_references == ()
    assert result.verified_proposals == ()


def test_verifier_exception_fails_closed(
    synthetic_approved_policy_references: set[str],
) -> None:
    def failed_verifier(_: str) -> ProposalVerification:
        raise RuntimeError("synthetic verifier failure")

    result = review_proposals(
        ["Ask for an order ID."],
        approved_policy_references=synthetic_approved_policy_references,
        verifier=failed_verifier,
    )

    assert result.status == "verification_failed"
    assert result.checks[0].verification_result == "failed"
    assert result.verified_proposals == ()


@pytest.mark.parametrize(
    "malformed_result",
    [
        None,
        {"status": "supported", "policy_references": [SYNTHETIC_POLICY_REFERENCE]},
        ProposalVerification(
            status="supported",
            policy_references=(SYNTHETIC_POLICY_REFERENCE,),
            verification_result="passed",
            verification_method="",
        ),
    ],
)
def test_malformed_verifier_result_fails_closed(
    malformed_result: object,
    synthetic_approved_policy_references: set[str],
) -> None:
    result = review_proposals(
        ["Ask for an order ID."],
        approved_policy_references=synthetic_approved_policy_references,
        verifier=lambda _: malformed_result,  # type: ignore[return-value]
    )

    assert result.status == "verification_failed"
    assert result.checks[0].status == "verification_failed"
    assert result.checks[0].verification_result == "failed"
    assert result.verified_proposals == ()


def test_degraded_generation_fails_closed_even_if_policy_verifier_would_pass(
    synthetic_approved_policy_references: set[str],
) -> None:
    def verifier_must_not_run(_: str) -> ProposalVerification:
        pytest.fail("degraded candidate must not be verified")

    result = review_proposals(
        ["Ask for a tracking reference."],
        approved_policy_references=synthetic_approved_policy_references,
        verifier=verifier_must_not_run,
        generation_degraded=True,
    )

    assert result.status == "verification_failed"
    assert result.checks[0].verification_method == "degraded_generation"
    assert result.checks[0].verification_result == "failed"
    assert result.verified_proposals == ()


def test_uncertain_check_never_allows_an_otherwise_supported_proposal(
    synthetic_approved_policy_references: set[str],
) -> None:
    result = review_proposals(
        ["Ask for an order ID."],
        approved_policy_references=synthetic_approved_policy_references,
        verifier=lambda _: ProposalVerification(
            status="supported",
            policy_references=(SYNTHETIC_POLICY_REFERENCE,),
            verification_result="uncertain",
            verification_method="synthetic_test_verifier",
        ),
    )

    assert result.status == "verification_failed"
    assert result.verified_proposals == ()
