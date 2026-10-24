"""No-network contract tests for the pinned production BGE ONNX provider."""

from types import SimpleNamespace

import numpy as np
import pytest

from src.retrieval.onnx_bge import MODEL_NAME, MODEL_REVISION, OnnxBgeEmbedder


class FakeTokenizer:
    def encode_batch(self, texts):
        return [
            SimpleNamespace(
                ids=[101, len(text), 102],
                attention_mask=[1, 1, 1],
            )
            for text in texts
        ]


class FakeSession:
    def __init__(self, bad_shape=False):
        self.batches = []
        self.bad_shape = bad_shape

    def get_inputs(self):
        return [SimpleNamespace(name=n) for n in ("input_ids", "attention_mask", "token_type_ids")]

    def run(self, output_names, inputs):
        assert output_names is None
        self.batches.append(inputs)
        dims = 383 if self.bad_shape else 384
        raw = np.zeros((len(inputs["input_ids"]), 3, dims), dtype=np.float32)
        raw[:, 0, 0] = 3
        raw[:, 0, 1] = 4
        raw[:, 1, 0] = 9000  # Must use CLS pooling, not mean pooling
        return [raw]


def fake_model(batch_size=2):
    obj = OnnxBgeEmbedder(MODEL_NAME, dimension=384, batch_size=batch_size)
    obj._tokenizer = FakeTokenizer()
    obj._session = FakeSession()
    return obj


def test_pinned_revision_is_full_hash():
    assert len(MODEL_REVISION) == 40
    assert all(x in "0123456789abcdef" for x in MODEL_REVISION)


def test_document_and_query_embeddings_use_same_normalized_cls():
    obj = fake_model()
    inputs = ["a", "bbb", "ccccc"]
    vectors = obj.embed_documents(inputs)
    assert len(vectors) == 3
    assert all(len(v) == 384 for v in vectors)
    assert np.allclose([v[:2] for v in vectors], [[0.6, 0.8]] * 3, atol=1e-6)
    assert len(obj._session.batches) == 2
    assert np.array_equal(obj._session.batches[0]["token_type_ids"], np.zeros((2, 3)))
    assert obj.embed_query("hello") == obj.embed(["hello"])[0]


def test_empty_documents_do_not_load_model():
    obj = OnnxBgeEmbedder()
    assert obj.embed_documents([]) == []
    assert obj._session is None


def test_invalid_model_dimension_and_batch_fail_closed():
    with pytest.raises(ValueError, match="reviewed"):
        OnnxBgeEmbedder("other")
    with pytest.raises(ValueError, match="reviewed"):
        OnnxBgeEmbedder(dimension=128)
    with pytest.raises(ValueError, match="batch size"):
        OnnxBgeEmbedder(batch_size=0)


def test_unexpected_onnx_output_shape_rejected():
    obj = fake_model()
    obj._session = FakeSession(bad_shape=True)
    with pytest.raises(ValueError, match="output contract"):
        obj.embed_query("hello")
