# ADR 0005: Separate similar cases from approved policy

- Status: Accepted
- Date: 2026-11-14
- Supersedes: grounding and case-authority assumptions in ADR 0004

## Context

The public demo has no organization-approved policy source. Banking77-derived cases and synthetic
past tickets can provide similar-case context, but they cannot establish what an organization
allows. Provider grounding flags, existing citations, and similarity percentages do not prove
that each proposed action is authorized. The default response must abstain while retaining intent
and urgency for human prioritization.

## Decision

- Keep similar past cases in a separately typed, untrusted context field with
  `evidence_type=similar_past_case` and `approved_policy=false`.
- Keep retrieved cases out of proposal-generation evidence. Never use their references as policy
  references.
- Default to zero approved policy sources and no configured policy verifier. Withhold generated
  proposals, return a short fixed acknowledgement, and set `next_action=manual_review`.
- For any explicitly configured approved-policy integration, require every returned proposal to
  have its own approved policy reference and a passing verifier result. Unsupported, conflicting,
  uncertain, missing, invalid, failed, or degraded-generation checks withhold proposals.
- Preserve intent, urgency, escalation, similar-case context, and per-proposal review results for
  the human reviewer.
- Remove uncalibrated grounding and confidence scores. Describe the current policy gate as
  structural; do not claim semantic entailment or policy correctness from mock or fixture tests.
- Change the public response contract to version 2.0 and update the frontend, tests, evaluation,
  and current documentation. Do not deploy or merge as part of this change.

## Consequences

- Old clients expecting grounding/confidence/citation fields or `ask_for_order_id` are incompatible
  and must adopt the version 2 policy fields.
- The default public demo intentionally routes all cases to human review until an owner approves a
  real policy source and a suitable verifier.
- Synthetic policy fixtures test control flow only. They are not public policy content and do not
  establish semantic correctness.
- Earlier screenshots, dated deployment reports, ADR 0004, and design plans record prior behavior;
  they are historical and do not describe this local version 2 implementation.
