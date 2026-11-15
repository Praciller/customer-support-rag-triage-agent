# Deterministic evaluation

## Reproduce

```powershell
$env:DEMO_MODE="true"
$env:MOCK_LLM_MODE="true"
$env:QDRANT_MODE="memory"
$env:EMBEDDING_PROVIDER="onnx"
$env:LLM_CACHE_ENABLED="false"
$env:EVAL_OUTPUT_PATH="reports/evaluation/results.json"
.venv\Scripts\python.exe -m src.evaluation.evaluate_triage
```

Artifacts:

- `reports/evaluation/results.json`
- `reports/evaluation/summary.md`
- `reports/evaluation/confusion_matrix.json`

The checked-in report is a local deterministic fixture result. It is not evidence about the
deployed public demo, production latency, customer outcomes, or policy correctness.

## What the triage evaluation measures

The run uses 8 labeled synthetic tickets, 27 bounded Banking77-derived demo cases, local
`BAAI/bge-small-en-v1.5` embeddings, and deterministic mock inference. The retrieved cases
provide similar-case context only. The default workflow has **no approved policy source**.

- Intent and urgency accuracy: exact label match.
- Macro F1: unweighted F1 across observed labels.
- Precision@K and recall@K: relevance is defined by mapped intent labels in this fixture.
- MRR and nDCG@K: ranking of mapped-intent relevant cases.
- Workflow success: whether all seven graph nodes completed.
- Policy review: counts of policy statuses, manual-review routes, proposals seen/withheld, and verified proposals. `method` is `structural_policy_gate_counts`.

The policy-review fields measure routing and response-shape invariants. With no approved policy
source, proposals must be withheld, the acknowledgement must remain policy-neutral, and the
ticket must route to human review. The evaluation does **not** score semantic entailment, policy
correctness, or whether a real organization permits any action. There is no grounding percentage,
calibrated confidence, or unsupported-claim rate in the current contract.

Separate unit and integration tests use explicitly synthetic policy IDs and verifier outputs to
exercise supported, unsupported, conflicting, uncertain, invalid-reference, and verifier-error
branches. Those fixtures test fail-closed control flow only; they are not policy content and do
not establish that a verifier can judge real policy text.

The adversarial structural evaluation uses `tests/fixtures/adversarial_retrieval.json`, an
explicitly synthetic fixture. It checks that similar cases and provider-supplied grounding or
citation claims cannot authorize proposals. It does not establish semantic prompt-injection
immunity.

## Separate synthetic Thai policy retrieval slice

`data/eval/thai_policy_slice.json` contains synthetic Thai policy records and questions with
explicit scope and permission labels. `src.evaluation.evaluate_thai_policy` filters by both
labels before scoring character-bigram overlap, and abstains when no authorized record passes the
lexical threshold. The evaluation reports positive, negative/abstention, and prompt-injection
counts alongside the denominator. It is offline and does not use the production RAG graph,
Banking77 fixtures, external models, or embeddings. Permission labels demonstrate filter
behavior only; they are not an identity system or production authorization control. See the
[generated report](../reports/evaluation/thai_policy_slice.md).

## Provider attribution and limitations

Evaluation mode is assigned from providers actually recorded in inference-node traces, not
providers merely configured in the application:

- `deterministic_mock`: all observed inference nodes used the mock route with no fallback or
  degradation.
- `real_provider`: all observed inference nodes used the external route without fallback or
  degradation. This label does not establish model quality.
- `mixed_or_degraded`: fallback, degraded, or mixed provider execution.

The fixture has one example per intent and rules intentionally aligned to those examples.
Retrieval relevance uses mapped intent, not human policy judgment. Latency is a local snapshot.
Mock results measure repeatable workflow behavior, not real-provider answer quality. The public
demo has no policy source or semantic verifier configured.

For independent human judgments, use the offline rubric and private CSV scorer in
[human_review.md](human_review.md). Human judgments are not inferred from the deterministic test
set or published automatically by CI.
