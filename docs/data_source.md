# Data source

## Public source

- Dataset: `mteb/banking77`
- Upstream: `PolyAI/banking77`
- Source: <https://huggingface.co/datasets/mteb/banking77>
- License recorded by the fixture: CC BY 4.0
- Full upstream size: 13,069 English banking support queries across 77 labels

## Demo fixture

`data/demo/support_cases.json` contains 27 bounded records and metadata revision
`demo-fixture-v1`. Whitespace is normalized, each upstream intent remains in
`metadata.original_intent`, and records are mapped into nine operational intents used by the
workflow. Stable ticket IDs produce stable Qdrant UUID5 point IDs.

The fixture is committed so startup, CI, and evaluation do not download or embed the full dataset.
The index bootstrap embeds only records missing from the target collection.

## Intended use and limitations

The data demonstrates support-intent retrieval and workflow behavior. It contains no private
tickets, credentials, or personal company data. Banking77 contains customer questions and labels,
not approved responses or real company policy. Retrieved records are similarity evidence only and
must not be treated as policy truth.

CSV/full-dataset ingestion remains an optional local workflow. Public demo ingestion is disabled.
