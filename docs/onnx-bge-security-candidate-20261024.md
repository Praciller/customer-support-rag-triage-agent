# Pinned ONNX BGE production-candidate review — 24 October 2026

**Candidate only; not a deployed Hugging Face Space.**

## Why

The previous FastEmbed 0.9.0 resolver required Pillow below 13 while
known advisories required Pillow 13. A forced dependency override was
explicitly rejected. The candidate removes FastEmbed and Pillow from
production entirely while retaining Qdrant's **same quantized ONNX BGE-small**
model and 384-dimensional embedding contract.

## Verified baseline

- Previous production resolver: 37 known Pillow 12.3.0 advisory IDs
  as of October 24, documented in historical Issue #93.
- Candidate resolved with `onnxruntime>=1.23,<1.25`,
  `tokenizers>=0.22,<1`, `huggingface-hub>=1,<2`.
- Strict Python 3.12 production `pip-audit==2.10.1`:
  **0 advisories**, neither FastEmbed nor Pillow installed in the
  candidate resolver graph.
- Exact public model revision:
  `Qdrant/bge-small-en-v1.5-onnx-Q@aa8f8b060edb00e03bfdd08813a2949946c8ba55`.
- Isolated on Windows comparing the same model weights, tokenization,
  CLS pooling and L2 normalization: 6 initial messages produced
  **zero maximum absolute vector difference**.
- Expanded to **27 original demo synthetic passages + 8 evaluation queries**:
  maximum vector difference **0**, **unchanged Top-5 ranking** for all
  evaluation queries, maximum dot-product difference
  **9.736324702025456e-08**. This is bounded functional evidence,
  not a generalized semantic-quality certification.
- The Docker-hf recipe changes only `EMBEDDING_PROVIDER` from
  `fastembed` to `onnx`; demo/mock/ingestion safety flags and
  seven-node graph are retained. Hashing CI smoke is not the release
  model smoke.

## Required validation before deployment

1. Verify candidate's exact source revision/commit and strict Python
   advisory scan; no exceptions.
2. Build `Dockerfile.hf` and verify *installed* package list and
   runtime identity.
3. Start only a loopback-bound container on 127.0.0.1:17860
   and run `python scripts/verify_local_onnx.py`; assert 27/27 indexed,
   correct BGE model/provider, 8 deterministic eval samples,
   seven completed stages, grounded and citation integrity, and HTTP 403
   for unauthenticated ingestion.
4. Human WCAG review at 390/768/1440, keyboard, screen-reader and
   native zoom; do not equate automated axe scans to manual review.
5. Obtain write-capable Space access. Produce a source bundle checksum
   and map exact GitHub revision to immutable Space commit and rollback.
   Only then deploy an explicitly approved release with a verified
   free-tier compute path.

**Not yet a live release or security attestation for existing Space**.
Live Space remains on older revision
`a2661562ff1a2a7b7f15e4b9145cb007c98444a5` until proven otherwise.
