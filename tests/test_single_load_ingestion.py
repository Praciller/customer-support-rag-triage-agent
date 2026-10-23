"""Ingestion must use one bounded source snapshot for raw and indexed records."""

import json
from types import SimpleNamespace

import pandas as pd

import src.api.services as service_module
import src.data.load_dataset as dataset_module
from src.config.settings import Settings


def sample_records():
    return [
        {
            "id": "synthetic-1",
            "message": "  Card   not arrived. ",
            "intent": "delivery_issue",
            "response": "",
            "source": "synthetic",
            "created_at": None,
            "metadata": {"original_intent": "card_arrival"},
        },
        {
            "id": "synthetic-2",
            "message": "  Refund   please ",
            "intent": "refund_request",
            "response": None,
            "source": "synthetic",
            "created_at": None,
            "metadata": {"original_intent": "refund_not_showing_up"},
        },
    ]


def test_service_ingest_loads_once_and_indexes_the_same_raw_records(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    records = sample_records()
    requests = []
    captures = []

    def load_once(settings, sample_size):
        requests.append(sample_size)
        assert len(requests) == 1, "Dataset must not be fetched twice"
        return records

    def unexpected_reload(*_args, **_kwargs):
        raise AssertionError("Writing a supplied source snapshot must never reload it")

    def index(docs, recreate):
        captures.extend(docs)
        assert recreate is False
        return len(docs)

    monkeypatch.setattr(service_module, "load_records", load_once)
    monkeypatch.setattr(dataset_module, "load_records", unexpected_reload)
    settings = Settings(_env_file=None, dataset_provider="huggingface")
    service = service_module.ApplicationServices(
        settings=settings,
        retriever=SimpleNamespace(index=index),
        workflow=object(),
        provider_names=["mock"],
    )

    result = service.ingest(recreate=False, sample_size=2)

    assert requests == [2]
    assert result["indexed"] == 2
    assert result["dataset"]["records"] == 2
    assert [doc.ticket_id for doc in captures] == ["synthetic-1", "synthetic-2"]
    assert [doc.message for doc in captures] == ["Card not arrived.", "Refund please"]
    raw = pd.read_csv(tmp_path / "data/raw/support_dataset.csv")
    assert raw["id"].tolist() == [doc.ticket_id for doc in captures]
    assert raw["message"].tolist() == [record["message"] for record in records]
    assert json.loads(raw.iloc[0]["metadata"])["original_intent"] == "card_arrival"


def test_standalone_raw_dataset_writer_still_loads_source(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    requests = []

    def fake_load(settings, sample_size):
        requests.append(sample_size)
        return sample_records()

    monkeypatch.setattr(dataset_module, "load_records", fake_load)
    metadata = dataset_module.write_raw_dataset(
        Settings(_env_file=None, dataset_provider="csv"),
        sample_size=2,
    )

    assert requests == [2]
    assert metadata["records"] == 2
    assert (tmp_path / "data/raw/support_dataset.csv").is_file()
    assert (tmp_path / "data/raw/dataset_metadata.json").is_file()
