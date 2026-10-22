# Offline human-reviewed support evaluation

The deterministic Banking77 benchmark measures reproducibility, **not** whether a support
draft is semantically grounded or policy-safe. This separate, manually annotated rubric
can measure expert judgments. It contains **no prefilled human decisions**.

## Reviewer preparation

1. Choose a frozen run of synthetic or properly authorized/de-identified support cases.
   Record its actual source SHA and provider/model ID. Keep the source materials, ticket
   text, replies, evidence, and reviewers' private notes in access-controlled storage.
   Do not put them in GitHub issues, CI artifacts, public datasets, or this repository.
2. For each sampled case, compare the suggested next action to escalation policy;
   inspect *every factual claim* against the cited source, and check that the draft does
   not expose personal information, fabricate guarantees, or claim unsupported policy.
3. Have reviewers independently record one row per sample. Prefer two reviewers;
   resolve disagreements with a documented adjudication, rather than overriding scores.
4. Save a local CSV under `private_evaluation/reviews.csv` using the template
   `data/eval/human_review_template.csv`. That directory is gitignored.

## Label contract

The CSV requires these fields:

| Field | Meaning |
| --- | --- |
| `sample_id` | Opaque synthetic or pseudonymous sample identifier |
| `run_id` | Identical frozen evaluation run for every row |
| `source_sha` | Source revision (7–40 hexadecimal characters), user-attested |
| `model_id` | Same model/provider identity for all reviews in the batch |
| `reviewer_id` | Reviewer pseudonym, kept only in private input |
| `reviewed_at_utc` | ISO 8601 timestamp with explicit UTC offset |
| `action_appropriate` | Is human action/escalation appropriate? |
| `citation_supported` | Does each factual claim have support from cited evidence? |
| `policy_safe` | Does the draft avoid unauthorized guarantees and unsafe disclosures? |

Each judgment is `pass`, `fail`, or `uncertain`. Only `citation_supported`
also accepts `not_applicable` when the draft makes **no cited factual claim**.
Do not use `not_applicable` to excuse unchecked citations. Empty or duplicated
records, mixed provenance, invalid timestamps, or invalid verdicts fail validation.

## Aggregate results

```powershell
python -m src.evaluation.human_review --input private_evaluation/reviews.csv --output private_evaluation/summary.json --expected-samples 25
```

The tool produces only aggregate status and dimension counts. Conflicting independent
reviews are `disputed`, not automatically averaged. Uncertain/disputed/failing cases
do not count toward `strict_pass_fraction`. Single-reviewer sample count is explicit.
`review_coverage` is available only if you pass a known expected sample count.

A report is not a human evaluation until genuine reviewers complete the private
annotation file. The tool cannot verify an asserted model version, reviewer identity,
semantic entailment, or correctness of the judgments. No human-review score is
generated from the mock fixture in CI. This tooling is not a substitute for
authentication, PII controls, policy approval, or production monitoring.
