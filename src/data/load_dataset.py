import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.config.settings import Settings, get_settings


def map_banking77_intent(label: str) -> str:
    normalized = label.lower().strip()
    if "cancel" in normalized or "terminate" in normalized:
        return "cancellation"
    if any(term in normalized for term in ("refund", "revert", "cashback")):
        return "refund_request"
    if any(
        term in normalized
        for term in ("not_recognised", "not_recognized", "compromised", "lost", "stolen", "twice")
    ):
        return "complaint"
    if any(term in normalized for term in ("arrival", "delivery", "tracking")):
        return "delivery_issue"
    if any(term in normalized for term in ("passcode", "pin", "identity", "personal_details")):
        return "account_access"
    if any(
        term in normalized
        for term in ("not_working", "failed", "beneficiary_not_allowed", "linking", "contactless")
    ):
        return "technical_issue"
    if any(
        term in normalized
        for term in (
            "balance",
            "cash",
            "charge",
            "cash_withdrawal",
            "exchange",
            "fee",
            "payment",
            "top_up",
            "transfer",
            "wrong_amount",
        )
    ):
        return "billing_issue"
    if any(
        term in normalized
        for term in (
            "acceptance",
            "age_limit",
            "country_support",
            "disposable",
            "expire",
            "physical_card",
            "spare_card",
            "supported",
            "virtual_card",
            "visa_or_mastercard",
        )
    ):
        return "product_question"
    return "other"


def load_records(settings: Settings, sample_size: int | None = None) -> list[dict[str, Any]]:
    if settings.dataset_provider.lower() == "csv":
        return _load_csv(settings, sample_size)
    try:
        return _load_huggingface(settings, sample_size)
    except Exception:
        if settings.csv_dataset_path.exists():
            return _load_csv(settings, sample_size)
        raise


def _load_huggingface(
    settings: Settings,
    sample_size: int | None,
) -> list[dict[str, Any]]:
    from datasets import load_dataset

    limit = sample_size or settings.dataset_sample_size
    config = settings.hf_dataset_config or None
    dataset = load_dataset(
        settings.hf_dataset_name,
        config,
        split=settings.hf_dataset_split,
    )
    if limit < len(dataset):
        dataset = dataset.shuffle(seed=42).select(range(limit))
    label_feature = dataset.features.get("label")
    records = []
    for index, row in enumerate(dataset):
        raw_label = str(row.get("label_text") or "")
        if not raw_label:
            raw_label = (
                label_feature.int2str(row["label"])
                if label_feature is not None and hasattr(label_feature, "int2str")
                else str(row.get("label", "other"))
            )
        records.append(
            {
                "id": f"{settings.hf_dataset_split}-banking77-{index}",
                "message": row.get("text", ""),
                "intent": map_banking77_intent(raw_label),
                "response": "",
                "source": settings.hf_dataset_name,
                "created_at": None,
                "metadata": {"original_intent": raw_label},
            }
        )
    return records


def _load_csv(settings: Settings, sample_size: int | None) -> list[dict[str, Any]]:
    frame = pd.read_csv(settings.csv_dataset_path)
    required = {settings.text_field, settings.intent_field}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {sorted(missing)}")
    if sample_size:
        frame = frame.head(sample_size)
    records = []
    for index, row in frame.iterrows():
        records.append(
            {
                "id": str(row.get("id", index)),
                "message": row[settings.text_field],
                "intent": row[settings.intent_field],
                "response": row.get(settings.response_field, ""),
                "source": row.get(settings.source_field, "csv_public_dataset"),
                "created_at": row.get("created_at"),
                "metadata": {},
            }
        )
    return records


def write_raw_dataset(
    settings: Settings,
    sample_size: int | None = None,
) -> dict[str, Any]:
    records = load_records(settings, sample_size)
    output = Path("data/raw/support_dataset.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(records)
    frame["metadata"] = frame["metadata"].map(json.dumps)
    frame.to_csv(output, index=False)
    metadata = {
        "name": settings.hf_dataset_name,
        "provider": settings.dataset_provider,
        "license": "CC BY 4.0",
        "records": len(records),
        "split": settings.hf_dataset_split,
        "source_url": f"https://huggingface.co/datasets/{settings.hf_dataset_name}",
        "upstream_dataset": "PolyAI/banking77",
        "raw_path": str(output),
    }
    Path("data/raw/dataset_metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    print(json.dumps(write_raw_dataset(get_settings()), indent=2))


if __name__ == "__main__":
    main()
