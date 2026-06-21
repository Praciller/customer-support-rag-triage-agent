import json
from pathlib import Path
from typing import Any

import numpy as np

from src.api.services import build_embedder
from src.config.settings import get_settings


def embed_documents(
    input_path: Path = Path("data/processed/support_documents.jsonl"),
    output_path: Path = Path("data/processed/support_embeddings.npy"),
) -> dict[str, Any]:
    settings = get_settings()
    documents = [
        json.loads(line)
        for line in input_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    embedder = build_embedder(settings)
    vectors = np.asarray(embedder.embed([item["message"] for item in documents]))
    np.save(output_path, vectors)
    metadata = {
        "documents": len(documents),
        "model": settings.embedding_model,
        "dimensions": int(vectors.shape[1]) if vectors.size else 0,
        "path": str(output_path),
    }
    output_path.with_suffix(".json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    print(json.dumps(embed_documents(), indent=2))


if __name__ == "__main__":
    main()
