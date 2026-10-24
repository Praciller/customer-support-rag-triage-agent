"""Reproducible opt-in model equivalence on bundled, noncustomer fixture."""

import csv
import json
from pathlib import Path

import numpy as np
from fastembed import TextEmbedding

from src.retrieval.onnx_bge import OnnxBgeEmbedder

root = Path(__file__).resolve().parents[1]
records = json.loads((root / "data/demo/support_cases.json").read_text(encoding="utf-8"))["records"]
queries = list(csv.DictReader((root / "data/eval/eval_set.csv").open(encoding="utf-8", newline="")))
documents = [record["message"] for record in records]
messages = [item["message"] for item in queries]
legacy = TextEmbedding("BAAI/bge-small-en-v1.5")
modern = OnnxBgeEmbedder(batch_size=8)
old_docs = np.asarray(list(legacy.passage_embed(documents, batch_size=8, parallel=None)))
new_docs = np.asarray(modern.embed_documents(documents))
old_queries = np.asarray(list(legacy.query_embed(messages, batch_size=8, parallel=None)))
new_queries = np.asarray(modern.embed_documents(messages))
diff = max(
    float(np.max(np.abs(old_docs - new_docs))),
    float(np.max(np.abs(old_queries - new_queries))),
)
old_scores = old_queries @ old_docs.T
new_scores = new_queries @ new_docs.T
rank_equal = all(
    np.array_equal(np.argsort(-o)[:5], np.argsort(-n)[:5])
    for o, n in zip(old_scores, new_scores, strict=True)
)
print(
    json.dumps(
        {
            "source_records": len(documents),
            "evaluation_queries": len(messages),
            "embedding_dimension": int(new_docs.shape[1]),
            "max_absolute_difference": diff,
            "top5_order_unchanged": rank_equal,
            "max_score_difference": float(np.max(np.abs(old_scores - new_scores))),
        },
        indent=2,
    ),
    flush=True,
)
assert len(documents) == 27
assert len(messages) == 8
assert new_docs.shape == old_docs.shape == (27, 384)
assert diff < 0.00002
assert rank_equal
