"""Fail-closed policy review primitives.

The public demo has no approved policy source. Similar cases are intentionally
not accepted by this module as policy references.
"""

from collections.abc import Collection, Sequence
from dataclasses import dataclass
from typing import Literal, Protocol

SAFE_ABSTENTION_RESPONSE = (
    "Thanks for reaching out. A support specialist needs to review this "
    "before we can advise on next steps."
)

CheckStatus = Literal[
    "supported",
    "unsupported",
    "conflicting",
    "uncertain",
    "no_approved_policy",
    "verification_failed",
]
VerificationResult = Literal["passed", "failed", "uncertain", "not_run"]
PolicyStatus = Literal[
    "verified",
    "unsupported",
    "conflicting",
    "uncertain",
    "no_approved_policy",
    "verification_failed",
    "no_proposals",
]


@dataclass(frozen=True)
class ProposalVerification:
    """A verifier result; it does not imply semantic entailment by itself."""

    status: CheckStatus
    policy_references: tuple[str, ...] = ()
    verification_result: VerificationResult = "uncertain"
    verification_method: str = "unspecified"


class ProposalVerifier(Protocol):
    def __call__(self, proposal: str) -> ProposalVerification: ...


@dataclass(frozen=True)
class ProposalCheck:
    proposal_id: str
    status: CheckStatus
    policy_references: tuple[str, ...]
    verification_result: VerificationResult
    verification_method: str


@dataclass(frozen=True)
class VerifiedProposal:
    proposal_id: str
    text: str
    policy_references: tuple[str, ...]
    verification_result: Literal["passed"]
    verification_method: str


@dataclass(frozen=True)
class PolicyReview:
    status: PolicyStatus
    checks: tuple[ProposalCheck, ...]
    verified_proposals: tuple[VerifiedProposal, ...]


def review_proposals(
    proposals: Sequence[str],
    *,
    approved_policy_references: Collection[str] = (),
    similar_case_references: Collection[str] = (),
    verifier: ProposalVerifier | None = None,
    proposal_parse_failed: bool = False,
    generation_degraded: bool = False,
) -> PolicyReview:
    """Allow proposals only with a passing check against an approved policy ID.

    This is a structural gate. It does not perform or claim semantic entailment.
    """

    approved_policy_references, _ = normalize_reference_collection(approved_policy_references)
    similar_case_references, valid_similar_case_references = normalize_reference_collection(
        similar_case_references
    )
    normalized = [proposal.strip() for proposal in proposals if proposal.strip()]
    if proposal_parse_failed and approved_policy_references:
        check = ProposalCheck(
            proposal_id="proposal-1",
            status="verification_failed",
            policy_references=(),
            verification_result="failed",
            verification_method="malformed_provider_output",
        )
        return PolicyReview("verification_failed", (check,), ())
    if not normalized:
        status: PolicyStatus = (
            "no_approved_policy" if not approved_policy_references else "no_proposals"
        )
        return PolicyReview(status, (), ())

    if not approved_policy_references:
        checks = tuple(
            ProposalCheck(
                proposal_id=f"proposal-{index}",
                status="no_approved_policy",
                policy_references=(),
                verification_result="not_run",
                verification_method="not_run",
            )
            for index, _ in enumerate(normalized, start=1)
        )
        return PolicyReview("no_approved_policy", checks, ())

    if not valid_similar_case_references:
        checks = tuple(
            ProposalCheck(
                proposal_id=f"proposal-{index}",
                status="verification_failed",
                policy_references=(),
                verification_result="failed",
                verification_method="invalid_similar_case_references",
            )
            for index, _ in enumerate(normalized, start=1)
        )
        return PolicyReview("verification_failed", checks, ())

    if generation_degraded:
        checks = tuple(
            ProposalCheck(
                proposal_id=f"proposal-{index}",
                status="verification_failed",
                policy_references=(),
                verification_result="failed",
                verification_method="degraded_generation",
            )
            for index, _ in enumerate(normalized, start=1)
        )
        return PolicyReview("verification_failed", checks, ())

    if verifier is None:
        checks = tuple(
            ProposalCheck(
                proposal_id=f"proposal-{index}",
                status="verification_failed",
                policy_references=(),
                verification_result="failed",
                verification_method="unavailable",
            )
            for index, _ in enumerate(normalized, start=1)
        )
        return PolicyReview("verification_failed", checks, ())

    checks: list[ProposalCheck] = []
    verified: list[VerifiedProposal] = []
    for index, proposal in enumerate(normalized, start=1):
        proposal_id = f"proposal-{index}"
        try:
            result = verifier(proposal)
            if not isinstance(result, ProposalVerification):
                raise TypeError("verifier returned an unexpected result type")
            if result.status not in {
                "supported",
                "unsupported",
                "conflicting",
                "uncertain",
                "no_approved_policy",
                "verification_failed",
            }:
                raise ValueError("verifier returned an invalid status")
            if result.verification_result not in {"passed", "failed", "uncertain", "not_run"}:
                raise ValueError("verifier returned an invalid verification result")
            if (
                not isinstance(result.verification_method, str)
                or not result.verification_method.strip()
                or len(result.verification_method) > 80
            ):
                raise ValueError("verifier returned an invalid method")
            if not isinstance(result.policy_references, tuple) or any(
                not isinstance(reference, str) or not reference or reference != reference.strip()
                for reference in result.policy_references
            ):
                raise ValueError("verifier returned malformed policy references")
            references = tuple(dict.fromkeys(result.policy_references))
        except Exception:
            result = ProposalVerification(
                status="verification_failed",
                verification_result="failed",
                verification_method="error",
            )
            references = ()
        valid_references = bool(references) and all(
            reference in approved_policy_references for reference in references
        )
        references_collide_with_case = bool(set(references) & similar_case_references)
        supported_and_verified = (
            result.status == "supported"
            and result.verification_result == "passed"
            and valid_references
            and not references_collide_with_case
        )
        status = result.status
        verification_result = result.verification_result
        method = result.verification_method
        if references_collide_with_case:
            status = "verification_failed"
            verification_result = "failed"
            method = "similar_case_reference"
        elif result.status == "supported" and not supported_and_verified:
            status = "verification_failed"
            verification_result = "failed"
            method = "invalid_policy_reference_or_result"
        elif references and not all(
            reference in approved_policy_references for reference in references
        ):
            status = "verification_failed"
            verification_result = "failed"
            method = "invalid_policy_reference"

        checks.append(
            ProposalCheck(
                proposal_id=proposal_id,
                status=status,
                policy_references=references
                if all(reference in approved_policy_references for reference in references)
                and not references_collide_with_case
                else (),
                verification_result=verification_result,
                verification_method=method,
            )
        )
        if supported_and_verified and status == "supported":
            verified.append(
                VerifiedProposal(
                    proposal_id=proposal_id,
                    text=proposal,
                    policy_references=references,
                    verification_result="passed",
                    verification_method=method,
                )
            )

    status = _overall_status(checks)
    if status != "verified":
        return PolicyReview(status, tuple(checks), ())
    return PolicyReview(status, tuple(checks), tuple(verified))


def normalize_reference_collection(
    references: Collection[str],
) -> tuple[frozenset[str], bool]:
    """Return a normalized reference set and whether the collection is valid."""

    if isinstance(references, (str, bytes)):
        return frozenset(), False
    try:
        values = tuple(references)
    except Exception:
        return frozenset(), False
    if any(
        not isinstance(reference, str) or not reference or reference != reference.strip()
        for reference in values
    ):
        return frozenset(), False
    return frozenset(values), True


def _overall_status(checks: Sequence[ProposalCheck]) -> PolicyStatus:
    statuses = {check.status for check in checks}
    for status in (
        "verification_failed",
        "conflicting",
        "uncertain",
        "unsupported",
    ):
        if status in statuses:
            return status
    if statuses == {"supported"} and all(
        check.verification_result == "passed" and check.policy_references for check in checks
    ):
        return "verified"
    return "verification_failed"
