"""Verify the optional dataset-loader path without network or customer data."""

from datasets import ClassLabel, Dataset, Features, Value

from src.config.settings import Settings
from src.data.load_dataset import _load_huggingface


def test_huggingface_classlabel_mapping_on_supported_datasets(monkeypatch) -> None:
    """Ensure the Datasets major upgrade retains the Banking77 label contract."""
    fixture = Dataset.from_dict(
        {
            "text": ["Where is my card?", "I paid a withdrawal fee."],
            "label": [0, 1],
        },
        features=Features(
            {
                "text": Value("string"),
                "label": ClassLabel(names=["card_arrival", "cash_withdrawal"]),
            }
        ),
    )

    def offline_load_dataset(name: str, config: str | None, *, split: str) -> Dataset:
        assert name == "mteb/banking77"
        assert config == "default"
        assert split == "train"
        return fixture

    monkeypatch.setattr("datasets.load_dataset", offline_load_dataset)
    settings = Settings(
        _env_file=None,
        hf_dataset_name="mteb/banking77",
        hf_dataset_config="default",
        hf_dataset_split="train",
        dataset_sample_size=2,
    )
    records = _load_huggingface(settings, sample_size=2)
    assert [record["intent"] for record in records] == ["delivery_issue", "billing_issue"]
    assert [record["metadata"]["original_intent"] for record in records] == [
        "card_arrival", "cash_withdrawal",
    ]
    assert all(record["source"] == "mteb/banking77" for record in records)


def test_huggingface_sample_limit_on_supported_datasets(monkeypatch) -> None:
    fixture = Dataset.from_dict({"text": ["one", "two", "three"]})
    monkeypatch.setattr("datasets.load_dataset", lambda *_args, **_kwargs: fixture)
    settings = Settings(_env_file=None, dataset_sample_size=1)
    records = _load_huggingface(settings, sample_size=1)
    assert len(records) == 1
    assert records[0]["intent"] == "other"
