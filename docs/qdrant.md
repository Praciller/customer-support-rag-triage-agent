# Qdrant

Qdrant runs locally on ports `6333` and `6334`. The `support_tickets` collection stores
384-dimensional normalized `BAAI/bge-small-en-v1.5` vectors and payload metadata.

Search supports top-k, a minimum similarity threshold, and an optional normalized intent filter.
Development reset is controlled by `QDRANT_RECREATE_COLLECTION`.

```powershell
docker compose up -d qdrant
python -m src.indexing.build_qdrant_index
```
