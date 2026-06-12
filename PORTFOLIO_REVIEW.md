# Portfolio Review

## Skills Demonstrated

- Designed a typed seven-stage LangGraph workflow with inspectable node traces.
- Built semantic retrieval with local sentence-transformer embeddings and Qdrant filters.
- Implemented Gemini, Groq, and Cerebras routing with cache-first execution, retries, fallback,
  safe degradation, and provider metadata.
- Exposed validated FastAPI endpoints and a responsive React/Vite support operations console.
- Added deterministic offline evaluation, Docker Compose, CI, tests, and operational docs.

## Reviewer Path

1. Read the architecture and model-routing sections in `README.md`.
2. Run `docker compose up --build`.
3. Ingest the real dataset with `POST /ingest`.
4. Submit a ticket in the triage page and inspect retrieved cases plus the seven-node trace.
5. Run the test and evaluation commands.

## Honest Readiness

This is a strong portfolio demonstration of RAG orchestration and reliability patterns. It is
not production-ready customer support automation: Banking77 does not contain company policy,
generated replies require human review, and public deployment needs authentication and abuse
controls.
