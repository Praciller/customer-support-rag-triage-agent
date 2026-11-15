from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.config.settings import get_settings
from src.policy import SAFE_ABSTENTION_RESPONSE


class TriageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str
    top_k: int = Field(default=5, ge=1)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("message must not be empty")
        if len(value) > get_settings().max_message_chars:
            raise ValueError("message exceeds configured length limit")
        return value

    @field_validator("top_k")
    @classmethod
    def validate_top_k(cls, value: int) -> int:
        if value > get_settings().max_top_k:
            raise ValueError("top_k exceeds configured limit")
        return value


class SearchRequest(TriageRequest):
    intent: str | None = None


class IngestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recreate: bool = False
    sample_size: int | None = Field(default=None, ge=1, le=1000)


class TraceStepResponse(BaseModel):
    node: str
    detail: str
    duration_ms: float = Field(ge=0)
    status: str
    input_summary: str
    output_summary: str
    component: str
    provider: str | None = None
    model: str | None = None
    cache_hit: bool
    fallback: bool
    degraded_mode: bool
    retrieved_document_count: int = Field(ge=0)
    policy_status: str | None = None
    similar_case_references: list[str] = Field(default_factory=list)
    policy_references: list[str] = Field(default_factory=list)
    error_category: str | None = None


class SimilarCaseResponse(BaseModel):
    ticket_id: str
    evidence_type: Literal["similar_past_case"] = "similar_past_case"
    approved_policy: Literal[False] = False
    message: str
    intent: str
    response: str
    source: str
    score: float
    created_at: str | None = None
    metadata: dict[str, Any]


class ProposalCheckResponse(BaseModel):
    proposal_id: str
    status: Literal[
        "supported",
        "unsupported",
        "conflicting",
        "uncertain",
        "no_approved_policy",
        "verification_failed",
    ]
    policy_references: list[str] = Field(default_factory=list)
    verification_result: Literal["passed", "failed", "uncertain", "not_run"]
    verification_method: str


class VerifiedProposalResponse(BaseModel):
    proposal_id: str
    text: str
    policy_references: list[str] = Field(min_length=1)
    verification_result: Literal["passed"]
    verification_method: str


class TriageResponse(BaseModel):
    normalized_message: str
    intent: str
    urgency: str
    escalate: bool
    escalation_reason: str
    suggested_response: str
    retrieved_cases: list[SimilarCaseResponse]
    similar_case_references: list[str] = Field(default_factory=list)
    policy_status: Literal[
        "verified",
        "unsupported",
        "conflicting",
        "uncertain",
        "no_approved_policy",
        "verification_failed",
        "no_proposals",
    ]
    proposal_checks: list[ProposalCheckResponse] = Field(default_factory=list)
    verified_proposals: list[VerifiedProposalResponse] = Field(default_factory=list)
    policy_references: list[str] = Field(default_factory=list)
    next_action: str
    provider_used: str
    model_used: str
    cached: bool
    fallback_used: bool
    degraded_mode: bool
    total_latency_ms: float = Field(ge=0)
    trace: list[TraceStepResponse]

    @model_validator(mode="after")
    def validate_policy_gate(self) -> "TriageResponse":
        similar_case_ids = set(self.similar_case_references) | {
            case.ticket_id for case in self.retrieved_cases
        }
        checked_policy_references = set(self.policy_references) | {
            reference for check in self.proposal_checks for reference in check.policy_references
        }
        if similar_case_ids & checked_policy_references:
            raise ValueError("similar case references cannot be policy references")

        if self.policy_status != "verified":
            if self.verified_proposals:
                raise ValueError("unverified proposals cannot be returned")
            if self.policy_references:
                raise ValueError("policy references require verified proposals")
            if self.next_action != "manual_review":
                raise ValueError("unverified output must route to manual review")
            if self.suggested_response != SAFE_ABSTENTION_RESPONSE:
                raise ValueError("unverified output must use the safe abstention response")
            return self

        if not self.verified_proposals:
            raise ValueError("verified policy status requires a verified proposal")
        checks = {check.proposal_id: check for check in self.proposal_checks}
        proposal_ids = [proposal.proposal_id for proposal in self.verified_proposals]
        if (
            len(checks) != len(self.proposal_checks)
            or len(set(proposal_ids)) != len(proposal_ids)
            or set(checks) != set(proposal_ids)
        ):
            raise ValueError("every proposal check must match exactly one verified proposal")
        for proposal in self.verified_proposals:
            check = checks.get(proposal.proposal_id)
            if (
                check is None
                or check.status != "supported"
                or check.verification_result != "passed"
                or not check.policy_references
                or not proposal.policy_references
                or not set(proposal.policy_references).issubset(self.policy_references)
                or set(proposal.policy_references) != set(check.policy_references)
                or proposal.verification_method != check.verification_method
            ):
                raise ValueError("each verified proposal requires a passing approved policy check")
        if set(self.policy_references) != {
            reference
            for proposal in self.verified_proposals
            for reference in proposal.policy_references
        }:
            raise ValueError("policy references must match the verified proposals")
        if self.suggested_response != "\n".join(
            proposal.text for proposal in self.verified_proposals
        ):
            raise ValueError("response text must match the verified proposals")
        return self
