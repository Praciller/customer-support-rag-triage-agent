"""Pinned text-only BGE-small ONNX inference, independent of FastEmbed/Pillow.

Keep the model repo and revision immutable. Any model, tokenizer, or pooling
change requires explicit retrieval and grounding reevaluation before release.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

MODEL_NAME = "BAAI/bge-small-en-v1.5"
MODEL_REPO = "Qdrant/bge-small-en-v1.5-onnx-Q"
MODEL_REVISION = "aa8f8b060edb00e03bfdd08813a2949946c8ba55"
MODEL_FILES = (
    "model_optimized.onnx",
    "tokenizer.json",
    "tokenizer_config.json",
    "config.json",
    "special_tokens_map.json",
)


class OnnxBgeEmbedder:
    """Same quantized Qdrant/ONNX model and CLS/L2 normalization as FastEmbed."""

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        dimension: int = 384,
        batch_size: int = 32,
    ) -> None:
        if model_name != MODEL_NAME or dimension != 384:
            raise ValueError("Only the reviewed 384-d BGE-small-v1.5 ONNX model is permitted")
        if batch_size < 1:
            raise ValueError("ONNX batch size must be positive")
        self.model_name = model_name
        self.dimension = dimension
        self.batch_size = batch_size
        self._tokenizer = None
        self._session = None

    def _load_model(self) -> None:
        if self._session is not None:
            return
        from huggingface_hub import snapshot_download
        from onnxruntime import InferenceSession
        from tokenizers import Tokenizer

        model_dir = Path(
            snapshot_download(
                repo_id=MODEL_REPO,
                revision=MODEL_REVISION,
                allow_patterns=list(MODEL_FILES),
                token=False,
            )
        )
        cfg = json.loads((model_dir / "tokenizer_config.json").read_text(encoding="utf-8"))
        if cfg.get("model_max_length") != 512:
            raise ValueError("Pinned BGE tokenizer maximum length has changed")
        tok = Tokenizer.from_file(str(model_dir / "tokenizer.json"))
        tok.enable_truncation(max_length=512, direction=cfg.get("truncation_side", "right"))
        pad = tok.padding or {}
        pad_token = pad.get("pad_token", cfg.get("pad_token"))
        pad_id = pad.get("pad_id")
        if pad_id is None and pad_token is not None:
            pad_id = tok.token_to_id(pad_token)
        if pad_token is None or pad_id is None:
            raise ValueError("Pinned BGE tokenizer padding metadata missing")
        tok.enable_padding(
            direction=cfg.get("padding_side", pad.get("direction", "right")),
            pad_id=pad_id,
            pad_type_id=pad.get("pad_type_id", 0),
            pad_token=pad_token,
            length=None,
        )
        session = InferenceSession(
            str(model_dir / "model_optimized.onnx"), providers=["CPUExecutionProvider"]
        )
        names = {node.name for node in session.get_inputs()}
        if "input_ids" not in names or not names <= {
            "input_ids",
            "attention_mask",
            "token_type_ids",
        }:
            raise ValueError("Pinned BGE ONNX input contract changed")
        self._tokenizer = tok
        self._session = session

    def _run(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        self._load_model()
        assert self._tokenizer is not None
        assert self._session is not None
        vectors: list[list[float]] = []
        input_names = {i.name for i in self._session.get_inputs()}
        for start in range(0, len(texts), self.batch_size):
            enc = self._tokenizer.encode_batch(texts[start : start + self.batch_size])
            ids = np.asarray([e.ids for e in enc], dtype=np.int64)
            inputs = {"input_ids": ids}
            if "attention_mask" in input_names:
                inputs["attention_mask"] = np.asarray(
                    [e.attention_mask for e in enc], dtype=np.int64
                )
            if "token_type_ids" in input_names:
                inputs["token_type_ids"] = np.zeros_like(ids)
            raw = self._session.run(None, inputs)[0]
            if raw.ndim == 3:
                raw = raw[:, 0, :]
            if raw.ndim != 2 or raw.shape != (len(enc), self.dimension):
                raise ValueError("Pinned BGE ONNX output contract changed")
            norm = np.maximum(np.linalg.norm(raw, axis=1, keepdims=True), 1e-12)
            vectors.extend((raw / norm).tolist())
        return vectors

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self.embed_documents(texts)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._run(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._run([text])[0]
