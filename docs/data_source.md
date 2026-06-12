# Data Source

The primary dataset is [mteb/banking77](https://huggingface.co/datasets/mteb/banking77),
a script-free mirror of the upstream [PolyAI Banking77 dataset](https://huggingface.co/datasets/PolyAI/banking77).
It contains 13,069 English online-banking support queries across 77 fine-grained intents and
is distributed under CC BY 4.0.

The project uses the mirror because current `datasets` releases reject the upstream legacy
loading script. `label_text` is deterministically mapped into the nine portfolio-level support
intents. The fields used are `text`, `label`, and `label_text`; the original label is retained
in `metadata.original_intent`. The checked baseline shuffles with seed 42 and samples 1,000
training records before whitespace normalization and intent mapping.

Banking77 contains customer questions and intent labels, not authoritative policy responses.
Retrieved examples are therefore similarity evidence, not business-policy truth.
CSV import remains available through `DATASET_PROVIDER=csv`.
