# Portfolio review

## Skills demonstrated

- Typed seven-node LangGraph orchestration with inspectable node-level execution evidence.
- Local semantic retrieval using BGE embeddings and Qdrant with idempotent fixture bootstrap.
- Deterministic no-key generation, grounding, provider routing, cache, retry, fallback, and safe
  degraded behavior.
- FastAPI trust-boundary validation, protected ingestion, configurable CORS/timeouts/rate limits,
  readiness, and secret-safe status output.
- Responsive React operations console with triage, retrieval, trace, evaluation, data, and
  infrastructure views.
- Reproducible offline metrics, tests, lint, container builds, and CI without external LLM calls.

## Reviewer path

1. Read the first screen and measured-results table in `README.md`.
2. Open the [public demo](https://pracill-customer-support-rag-triage-agent.hf.space/).
3. Select **Card not arrived**, run triage, and inspect three retrieved cases plus seven trace nodes.
4. Open **Evaluation** and compare the UI with `reports/evaluation/results.json`.
5. Review `docs/security.md` and `docs/deployment.md` for production trade-offs.

## Strongest engineering evidence

- Stable UUID5 IDs make demo bootstrap idempotent instead of recreating the index on every start.
- All model-backed nodes use a common provider/cache/fallback contract while preserving
  task-specific routing.
- The public demo is useful without credentials and labels mock behavior honestly.
- Trace responses expose operational metadata without prompts, secrets, environment values, or
  stack traces.
- The same bounded fixture supports startup, integration tests, evaluation, and screenshots.

## Measured evidence

The July 19, 2026 FastEmbed evaluation used 8 labeled queries and 27 indexed records. Intent and
urgency accuracy were 100%; Precision@5 was 37.5%, standard Recall@5 62.5%, MRR 0.771, nDCG@5
0.611, and workflow success 100%. These are deterministic regression measurements, not production
claims. The mock grounding-verifier pass rate is workflow evidence, not semantic-entailment proof.

The July 26 public smoke test verified Hugging Face revision
`255b7272544c9222e1fde5351598779049615162`, synchronized from GitHub
`81baa5f727da21e9cd1577ebc4131ace2fbf2b37`. `/ready` returned 200 with 27 indexed records; one
mock triage returned 3 retrieval matches, a complete 7/7 trace, grounded status, and
`ask_for_order_id`, while public ingestion returned 403. The deployed Evaluation view showed
Precision@5 37.5% (38% displayed), Recall@5 62.5% (63% displayed), MRR 0.771, and nDCG@5 0.611.
Desktop and 390-pixel mobile checks had no page-level overflow and no browser warnings or errors.
The live triage remains a single-ticket deployment smoke result, not an aggregate evaluation metric.

## Cost-conscious decisions

- Deterministic mock provider by default; real providers optional.
- Local embeddings, embedded/server Qdrant, and SQLite cache.
- In-memory rate limiting instead of Redis for a single-instance demo.
- Small committed fixture instead of repeated full-dataset downloads.
- CPU-only Hugging Face image with no billing-enabled dependency.

## Honest readiness

The repository and public deterministic demo are reviewable. It is not autonomous production
support: the dataset is not policy, responses require human review, and in-memory controls do not
scale across instances. Free CPU hosting may cold-start.

## Interview talking points

- Why a fixed graph is easier to evaluate and govern than an open-ended agent loop.
- How stable fixture IDs prevent duplicate vector ingestion.
- Why measured Recall@5 is 62.5% and Precision@5 remains the clearest improvement opportunity.
- How mock mode separates workflow reliability from provider availability and cost.
- Which controls must change for multi-tenant, sensitive, or horizontally scaled use.
