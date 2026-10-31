# Synthetic Thai Policy Retrieval Slice

Mode: `offline_character_bigram_lexical_baseline`; offline only; no external provider or paid API.
Dataset: `synthetic-thai-enterprise-policy-v1` (5 records, all synthetic).

## Scope and denominator

Cases: **8**; positive retrieval: **5**;
negative abstention: **3**; injection:
**1**. Correct: **8/8**;
permission-safe: **8/8**.

| Case | Expected abstain | Did abstain | Result |
| --- | --- | --- | --- |
| `q-refund-duplicate` | no | no | PASS |
| `q-account-email` | no | no | PASS |
| `q-delivery` | no | no | PASS |
| `q-finance-authorized` | no | no | PASS |
| `q-hr-authorized` | no | no | PASS |
| `q-finance-denied` | yes | yes | PASS |
| `q-no-evidence` | yes | yes | PASS |
| `q-injection` | yes | yes | PASS |

## Invariants

| Check | Result |
| --- | --- |
| `cases_present` | PASS |
| `positive_cases_present` | PASS |
| `negative_abstention_cases_present` | PASS |
| `injection_cases_present` | PASS |
| `permission_filter_pass` | PASS |
| `case_accuracy_pass` | PASS |
| `injection_cannot_expand_permission` | PASS |

## Limitations and upgrade path

- All records and queries are synthetic; they do not define enterprise policy.
- Character bigram overlap is lexical, not Thai semantic retrieval or embeddings.
- Permission labels filter this fixture; they are not production authorization.
- Injection tests filter behavior, not semantic LLM immunity.

Practical next steps: review policy taxonomy and access labels with policy owners; expand a
reviewed,
non-sensitive Thai benchmark with adjudicated relevance and refusal labels; compare this baseline
with a locally hosted Thai-capable embedding model and reranker; evaluate citation support and
adversarial cases with human reviewers before considering live inference. Enforce identity-derived
authorization at a trusted service boundary, outside the retriever fixture.
