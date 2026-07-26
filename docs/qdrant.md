# Qdrant

Qdrant runs locally on ports `6333` and `6334`. The `support_tickets` collection stores
384-dimensional normalized `BAAI/bge-small-en-v1.5` vectors and payload metadata.

Search supports top-k, a minimum similarity threshold, and an optional normalized intent filter.
Development reset is controlled by `QDRANT_RECREATE_COLLECTION`.

Demo bootstrap is idempotent: each fixture ticket maps to a stable UUID5 point ID, existing IDs are
retrieved first, and only missing records are embedded and uploaded. Upserts preserve payload
metadata and prevent duplicate fixture records across restarts. Empty collections return no evidence;
the workflow then forces manual review rather than treating a draft as grounded.

```powershell
docker compose up -d qdrant
python -m src.indexing.build_qdrant_index
```
