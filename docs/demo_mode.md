# Demo mode

## Contract

```env
DEMO_MODE=true
MOCK_LLM_MODE=true
BOOTSTRAP_DEMO_DATA=true
ALLOW_PUBLIC_INGEST=false
```

Demo mode routes classification, urgency, and proposal generation to `mock/deterministic-small`, bootstraps the bounded public fixture, and makes no network inference call. Similar past cases are context only. There is no approved policy source or verifier configured in the public demo, so generated proposals are withheld and every ticket gets a short acknowledgement plus `manual_review`.

## Bootstrap

Startup checks stable IDs in Qdrant and embeds only missing records. `/ready` returns 200 after all 27 records exist. `/health` remains a liveness endpoint and reports `not_ready` if bootstrap fails.

## Included ticket examples

The UI includes card delivery, cash withdrawal, pending transfer, stolen card, account access, suspicious transaction, and reversed payment examples aligned to the fixture taxonomy. Custom text is also accepted up to the configured length limit.

## Honesty boundary

The UI labels deterministic mode explicitly. Local output is not presented as a network model response. The fixture is not company policy, retrieved case content is untrusted, and every response requires human review.
