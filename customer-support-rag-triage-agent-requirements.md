# Customer Support RAG Triage Agent - Full Project Requirements

## 1. Project Summary

**Repository name:** `customer-support-rag-triage-agent`

Build a practical AI Engineer portfolio project: a customer support triage assistant using a real public support dataset, Qdrant VectorDB, LangGraph workflow, FastAPI, and React/Vite.

The system should receive a customer message, classify intent, detect urgency, retrieve similar past cases, generate a grounded support response, verify grounding, and show the agent trace.

This is not a generic chatbot. It is a support workflow assistant with retrieval, triage, fallback routing, caching, and evaluation.

---

## 2. Why This Project

This project adds modern AI Engineer skills to the portfolio:

- LangGraph agent workflow
- LangChain-based RAG utilities
- Qdrant VectorDB
- local sentence-transformers embeddings
- provider routing across Gemini, Groq, and Cerebras
- cache-before-call strategy
- fallback provider strategy
- retrieval evaluation
- grounded response generation
- FastAPI backend
- React/Vite dashboard
- Docker Compose local system

It fits better than a research-paper RAG project because it is business-facing and aligned with customer support / workflow automation.

---

## 3. Core Use Case

A support agent receives a customer message.

The system should:

1. Normalize the message
2. Classify support intent
3. Detect urgency and escalation risk
4. Retrieve similar support cases from Qdrant
5. Retrieve relevant response examples or knowledge snippets
6. Generate a concise support response suggestion
7. Verify the response is grounded in retrieved context
8. Suggest the next action
9. Return provider/model/cache metadata
10. Show the LangGraph workflow trace in the UI

Example input:

```txt
My order has not arrived and customer service keeps ignoring me. I want a refund now.
```

Example output:

```json
{
  "intent": "delivery_issue",
  "urgency": "high",
  "escalate": true,
  "escalation_reason": "Refund request and unresolved delivery issue",
  "suggested_response": "I'm sorry your order has not arrived. Please share your order ID so we can check the delivery status and review available refund options.",
  "retrieved_cases": [
    {
      "text": "Customer reported delayed delivery and requested refund.",
      "score": 0.87,
      "intent": "delivery_issue",
      "source": "public_dataset"
    }
  ],
  "grounded": true,
  "grounding_score": 0.82,
  "next_action": "ask_for_order_id",
  "provider_used": "gemini",
  "model_used": "gemini-2.0-flash-lite",
  "cached": false,
  "degraded_mode": false
}
```

---

## 4. Dataset Requirements

### Main Rule

Use a real public customer support / ticket / customer message dataset.

Synthetic/generated data is allowed only for tests, examples, and schema validation. It must not be the main dataset.

### Primary Dataset Strategy

Use Hugging Face datasets as the preferred source if available.

Recommended dataset categories to validate during implementation:

- customer support intent classification datasets
- public customer service conversation datasets
- Bitext-style customer support datasets
- support ticket datasets with message and category fields
- public customer support Twitter / TWCS-style datasets if available without Kaggle token

The implementation must document the selected dataset in `docs/data_source.md`.

### CSV Fallback

If the Hugging Face dataset is unavailable, the project must support CSV import from a real public dataset.

Required CSV minimum schema:

```csv
id,message,intent,response,source,created_at
1,"Where is my order?","delivery_issue","Please share your order ID.","public_dataset","2024-01-01"
```

Minimum required fields:

- `message`
- `intent` or `category`

Useful optional fields:

- `response`
- `resolution`
- `source`
- `created_at`
- `channel`
- `sentiment`
- `priority`

### Data Documentation

Create `docs/data_source.md` with:

- dataset name
- dataset source
- license or usage note when available
- fields used
- sample size used
- preprocessing decisions
- limitations

---

## 5. Recommended Tech Stack

### Backend

- Python 3.10+
- FastAPI
- Pydantic
- LangGraph
- LangChain
- Qdrant client
- sentence-transformers
- Hugging Face `datasets`
- pandas
- scikit-learn
- httpx
- python-dotenv
- diskcache or SQLite cache
- pytest

### Vector Database

- Qdrant via Docker Compose

### Frontend

- React
- Vite
- TypeScript
- Tailwind CSS
- Recharts
- Axios or Fetch API

### DevOps

- Docker Compose
- GitHub Actions CI
- `.env.example`
- local-first execution

---

## 6. Model Provider Strategy

The project must support three free-tier providers:

1. Google Gemini API through Google AI Studio
2. Groq API
3. Cerebras AI API

### Important Note

Provider model names, availability, and free-tier limits can change. All provider names and model names must be read from `.env`. Do not hardcode them as the only option in source code.

### Provider Priority

Default provider order:

```txt
gemini,groq,cerebras
```

### Recommended Model Routing

Use the lowest-cost and fastest model that is still suitable for each task.

| Task | Default provider | Notes |
|---|---|---|
| intent classification | Groq or Gemini | small/fast model is enough |
| urgency detection | Groq or Gemini | small/fast model is enough |
| response generation | Gemini | use Google AI Studio primary |
| grounding check | Gemini or Groq | small/fast model is enough |
| fallback generation | Groq | fast fallback |
| last-resort fallback | Cerebras | only if previous providers fail |

### Recommended Default Models

Use these values in `.env.example`:

```env
GEMINI_DEFAULT_MODEL=gemini-2.0-flash-lite
GEMINI_FALLBACK_MODEL=gemini-2.0-flash
GROQ_DEFAULT_MODEL=llama-3.1-8b-instant
GROQ_FALLBACK_MODEL=llama-3.3-70b-versatile
CEREBRAS_DEFAULT_MODEL=llama3.1-8b
```

If any model is unavailable at implementation time, replace it with the smallest currently available free-tier model for that provider and document the change in `docs/model_routing.md`.

### Model Usage Rules

- Use cache before calling any provider.
- Do not call multiple LLMs unless needed.
- Retry a provider once before switching.
- Use small/fast models for classification and grounding.
- Use Gemini Flash Lite as the default generation model.
- Do not use large models unless fallback or low-confidence output requires it.
- Log provider and model used.
- Never log API keys.

---

## 7. Embedding Strategy

### Requirement

Do not use paid embedding APIs in version 1.

Use local sentence-transformers embeddings.

### Default Embedding Model

```env
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
```

Reason:

- strong English retrieval quality for a small model
- good for customer support semantic search
- CPU-friendly
- 384-dimensional embeddings
- no API cost
- works well with Qdrant

### Multilingual Alternative

If the selected dataset is multilingual or Thai/English mixed:

```env
EMBEDDING_MODEL=intfloat/multilingual-e5-small
```

### Qdrant Vector Size

For `BAAI/bge-small-en-v1.5`:

```env
QDRANT_VECTOR_SIZE=384
```

The implementation should derive vector size automatically when possible, but `.env.example` should still include the default.

---

## 8. Cache and Fallback Requirements

### Cache

The project must cache LLM responses before making provider calls.

Recommended cache backends:

- diskcache
- SQLite

Cache key must include:

- provider
- model
- task type
- prompt hash
- retrieved context hash
- temperature

Cache behavior:

- check cache before every LLM call
- store successful responses
- do not cache provider errors
- support TTL
- allow cache disable through `.env`

### Fallback

If the primary provider fails:

1. Retry same provider once with exponential backoff
2. Switch to next provider in priority order
3. If all providers fail, return safe fallback response
4. Mark `degraded_mode=true`

Safe fallback response:

```txt
I could not generate a reliable response right now. Please review the retrieved similar cases and respond manually.
```

### Provider Health Endpoint

Add:

```http
GET /provider-health
```

It should show configured providers, selected models, cache status, and fallback order without exposing API keys.

---

## 9. LangGraph Workflow

Required workflow:

```txt
START
  ↓
normalize_message
  ↓
classify_intent
  ↓
detect_urgency
  ↓
retrieve_similar_cases
  ↓
generate_support_response
  ↓
grounding_check
  ↓
suggest_next_action
  ↓
END
```

Required nodes:

- `normalize_message`
- `classify_intent`
- `detect_urgency`
- `retrieve_similar_cases`
- `generate_support_response`
- `grounding_check`
- `suggest_next_action`

### Intent Labels

Default intent labels:

- `delivery_issue`
- `refund_request`
- `billing_issue`
- `technical_issue`
- `account_access`
- `product_question`
- `complaint`
- `cancellation`
- `other`

### Urgency Labels

- `low`
- `medium`
- `high`
- `critical`

Urgency detection should also return:

- `escalate`
- `escalation_reason`

### Response Generation Rules

Generated support responses must:

- be concise
- be polite
- not invent policy
- not promise refunds unless context supports it
- ask for missing information when needed
- cite retrieved cases/context
- mark low confidence when context is insufficient

### Grounding Check

The grounding check must return:

- `grounded`
- `grounding_score`
- `unsupported_claims`
- `confidence`

### Suggested Next Actions

Allowed actions:

- `reply_to_customer`
- `ask_for_order_id`
- `request_more_info`
- `escalate_to_human`
- `manual_review`

---

## 10. Qdrant / RAG Requirements

### Default Collection

```env
QDRANT_COLLECTION=support_tickets
```

### Payload Fields

Each vector payload should include:

- `ticket_id`
- `message`
- `intent`
- `response`
- `source`
- `created_at`
- `metadata`

### Indexing Pipeline

Required scripts:

```txt
src/data/load_dataset.py
src/data/clean_dataset.py
src/indexing/build_documents.py
src/indexing/embed_documents.py
src/indexing/build_qdrant_index.py
```

### Retrieval Requirements

- support top-k retrieval
- support optional intent/category filter
- return similarity score
- return payload metadata
- support rebuild index command
- support collection reset in development mode

Default retrieval values:

```env
RETRIEVAL_TOP_K=5
RETRIEVAL_MIN_SCORE=0.35
```

---

## 11. FastAPI Requirements

### Required Endpoints

```http
GET /health
GET /dataset-info
GET /provider-health
POST /ingest
POST /triage
POST /search-similar
GET /eval/results
```

### POST /triage Request

```json
{
  "message": "My order has not arrived and I want a refund.",
  "top_k": 5
}
```

### POST /triage Response

```json
{
  "intent": "delivery_issue",
  "urgency": "high",
  "escalate": true,
  "escalation_reason": "Refund request and delivery issue",
  "suggested_response": "I'm sorry your order has not arrived...",
  "retrieved_cases": [],
  "grounded": true,
  "grounding_score": 0.81,
  "next_action": "ask_for_order_id",
  "provider_used": "gemini",
  "model_used": "gemini-2.0-flash-lite",
  "cached": false,
  "degraded_mode": false,
  "trace": []
}
```

### API Rules

- validate message length
- reject empty message
- limit `top_k`
- do not expose API keys
- return provider/model metadata
- return cache hit status
- return degraded mode status
- enable CORS for frontend
- include Swagger docs

---

## 12. Frontend Requirements

Required pages:

- Overview
- Ticket Triage
- Semantic Search
- Agent Trace
- Evaluation Dashboard
- Dataset Explorer
- Provider Status

### Ticket Triage Page

Show:

- message input
- intent
- urgency
- escalation flag
- escalation reason
- suggested response
- retrieved similar cases
- grounding score
- next action
- provider/model used
- cache hit status
- degraded mode status

### Semantic Search Page

Show:

- search input
- top-k selector
- intent filter
- similar tickets
- similarity scores
- metadata

### Agent Trace Page

Show LangGraph steps:

- normalize_message
- classify_intent
- detect_urgency
- retrieve_similar_cases
- generate_support_response
- grounding_check
- suggest_next_action

### Evaluation Dashboard

Show:

- retrieval precision@k
- intent accuracy
- urgency detection metrics
- groundedness pass rate
- average latency
- cache hit rate
- provider usage count
- fallback count

### Provider Status Page

Show:

- configured providers
- primary provider
- fallback provider order
- selected models
- cache status
- embedding model
- Qdrant collection

Do not show API keys.

---

## 13. Evaluation Requirements

Required evaluation scripts:

```txt
src/evaluation/evaluate_retrieval.py
src/evaluation/evaluate_triage.py
```

Required reports:

```txt
reports/evaluation_report.md
reports/evaluation_metrics.json
```

Metrics:

- retrieval precision@k
- recall@k if labels allow
- intent accuracy
- macro F1
- urgency accuracy
- groundedness pass rate
- average latency
- cache hit rate
- provider fallback rate

Evaluation must run without calling real APIs when `MOCK_LLM_MODE=true`.

---

## 14. Non-Functional Requirements

### Cost

- must be free-tier friendly
- must use local embeddings
- must cache LLM calls
- must avoid unnecessary provider calls
- must use small/fast models by default
- must support mock mode for tests

### Reliability

- provider fallback required
- timeout required
- retry limit required
- safe fallback response required
- degraded mode flag required

### Security

- API keys loaded only from environment variables
- never commit `.env`
- never expose keys to frontend
- never log keys
- frontend must call only backend API

### Maintainability

- provider clients isolated
- LangGraph nodes modular
- prompts stored separately
- Pydantic schemas used for API
- retrieval layer separated from graph layer
- config centralized in `src/config/settings.py`

### Testing

Required tests:

```txt
tests/test_api.py
tests/test_cache.py
tests/test_provider_router.py
tests/test_retriever.py
tests/test_workflow.py
```

Tests must not call real LLM APIs.

---

## 15. Repository Structure

```txt
customer-support-rag-triage-agent/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile.api
├── data/
│   ├── raw/
│   ├── processed/
│   └── eval/
├── prompts/
│   ├── classify_intent.md
│   ├── detect_urgency.md
│   ├── generate_response.md
│   └── grounding_check.md
├── src/
│   ├── api/
│   │   └── main.py
│   ├── config/
│   │   └── settings.py
│   ├── data/
│   │   ├── load_dataset.py
│   │   └── clean_dataset.py
│   ├── indexing/
│   │   ├── build_documents.py
│   │   ├── embed_documents.py
│   │   └── build_qdrant_index.py
│   ├── retrieval/
│   │   └── retriever.py
│   ├── graph/
│   │   ├── state.py
│   │   ├── nodes.py
│   │   └── workflow.py
│   ├── llm/
│   │   ├── base.py
│   │   ├── router.py
│   │   ├── cache.py
│   │   ├── gemini_client.py
│   │   ├── groq_client.py
│   │   └── cerebras_client.py
│   ├── evaluation/
│   │   ├── evaluate_retrieval.py
│   │   └── evaluate_triage.py
│   └── utils/
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   └── src/
├── reports/
│   ├── evaluation_report.md
│   └── evaluation_metrics.json
├── docs/
│   ├── architecture.md
│   ├── data_source.md
│   ├── model_routing.md
│   ├── qdrant.md
│   ├── langgraph_workflow.md
│   ├── evaluation.md
│   └── deployment.md
└── tests/
    ├── test_api.py
    ├── test_cache.py
    ├── test_provider_router.py
    ├── test_retriever.py
    └── test_workflow.py
```

---

## 16. Docker Compose Requirements

Required services:

- `api`
- `frontend`
- `qdrant`

Expected URLs:

```txt
Frontend: http://localhost:5173
API: http://localhost:8000
API Docs: http://localhost:8000/docs
Qdrant: http://localhost:6333
```

Qdrant ports:

```txt
6333
6334
```

---

## 17. Environment Variables

Create `.env.example` with these variables:

```env
# App
APP_ENV=development
APP_NAME=customer-support-rag-triage-agent
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_ORIGIN=http://localhost:5173
LOG_LEVEL=INFO

# Dataset
DATASET_PROVIDER=huggingface
HF_DATASET_NAME=
HF_DATASET_CONFIG=
HF_DATASET_SPLIT=train
DATASET_SAMPLE_SIZE=1000
CSV_DATASET_PATH=data/raw/support_dataset.csv
TEXT_FIELD=message
INTENT_FIELD=intent
RESPONSE_FIELD=response
SOURCE_FIELD=source

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=support_tickets
QDRANT_VECTOR_SIZE=384
QDRANT_DISTANCE=Cosine
QDRANT_RECREATE_COLLECTION=false

# Embeddings
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DEVICE=cpu
EMBEDDING_BATCH_SIZE=32
NORMALIZE_EMBEDDINGS=true

# Retrieval
RETRIEVAL_TOP_K=5
RETRIEVAL_MIN_SCORE=0.35
RETRIEVAL_MAX_CONTEXT_CHARS=4000

# LLM Provider Routing
LLM_PROVIDER_PRIORITY=gemini,groq,cerebras
LLM_DEFAULT_PROVIDER=gemini
LLM_TIMEOUT_SECONDS=30
LLM_MAX_RETRIES=1
LLM_RETRY_BACKOFF_SECONDS=2
LLM_TEMPERATURE=0.2
LLM_MAX_OUTPUT_TOKENS=512
MOCK_LLM_MODE=false

# Gemini / Google AI Studio
GEMINI_API_KEY=
GEMINI_DEFAULT_MODEL=gemini-2.0-flash-lite
GEMINI_FALLBACK_MODEL=gemini-2.0-flash

# Groq
GROQ_API_KEY=
GROQ_DEFAULT_MODEL=llama-3.1-8b-instant
GROQ_FALLBACK_MODEL=llama-3.3-70b-versatile

# Cerebras
CEREBRAS_API_KEY=
CEREBRAS_DEFAULT_MODEL=llama3.1-8b

# Task-specific model routing
INTENT_MODEL_PROVIDER=groq
INTENT_MODEL_NAME=llama-3.1-8b-instant
URGENCY_MODEL_PROVIDER=groq
URGENCY_MODEL_NAME=llama-3.1-8b-instant
RESPONSE_MODEL_PROVIDER=gemini
RESPONSE_MODEL_NAME=gemini-2.0-flash-lite
GROUNDING_MODEL_PROVIDER=gemini
GROUNDING_MODEL_NAME=gemini-2.0-flash-lite

# Cache
LLM_CACHE_ENABLED=true
LLM_CACHE_BACKEND=disk
LLM_CACHE_DIR=.cache/llm
LLM_CACHE_TTL_SECONDS=86400

# Limits and safety
MAX_MESSAGE_CHARS=2000
MAX_TOP_K=10
ENABLE_SAFE_FALLBACK=true
RETURN_AGENT_TRACE=true

# Evaluation
EVAL_DATA_PATH=data/eval/eval_set.csv
EVAL_OUTPUT_PATH=reports/evaluation_metrics.json
```

---

## 18. CLI Commands

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

### Data and Indexing

```bash
python -m src.data.load_dataset
python -m src.data.clean_dataset
python -m src.indexing.build_documents
python -m src.indexing.embed_documents
python -m src.indexing.build_qdrant_index
```

### Evaluation

```bash
python -m src.evaluation.evaluate_retrieval
python -m src.evaluation.evaluate_triage
```

### API

```bash
uvicorn src.api.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
npm run build
```

### Docker

```bash
docker compose up --build
```

---

## 19. Deployment Recommendation

Version 1 should be local-first.

Recommended deployment mode:

```txt
Frontend: Vercel or Netlify static showcase
Backend: local Docker Compose
Qdrant: local Docker Compose
Live LLM calls: local only
```

Do not expose provider API keys in frontend deployment.

Optional future deployment:

- backend on Hugging Face Spaces Docker / Render / Railway / Fly.io
- Qdrant local or managed Qdrant if free tier is acceptable

---

## 20. README Requirements

README must include:

- Project Overview
- Why this is not a generic chatbot
- Dataset Source
- Tech Stack
- Architecture
- LangGraph Workflow
- Qdrant Vector Search
- LLM Provider Routing
- Embedding Strategy
- Caching and Fallback
- Setup Instructions
- Environment Variables
- Data Loading
- Indexing
- API Usage
- Frontend Usage
- Evaluation
- Screenshots
- Limitations
- Future Improvements
- Resume Bullet

---

## 21. Limitations

Document these limitations:

- free-tier provider limits can change
- model names can change
- dataset may not reflect all real business policies
- generated responses require human review
- similar case retrieval does not guarantee correct policy
- this is a portfolio demo, not autonomous customer support replacement

---

## 22. Future Improvements

- add reranker model
- add multilingual support
- add human feedback loop
- add response rating
- add real help center document ingestion
- add ticket assignment recommendation
- add Slack/Discord workflow integration
- add LangSmith or OpenTelemetry tracing if free setup is practical
- add managed Qdrant deployment option

---

## 23. Definition of Done

The project is complete when:

- real support dataset is loaded and documented
- Qdrant index is built
- local embedding model works
- LangGraph workflow runs end-to-end
- provider routing supports Gemini, Groq, and Cerebras
- cache works before provider calls
- fallback works when provider fails
- FastAPI endpoints work
- React frontend works
- evaluation report exists
- Docker Compose starts api, frontend, and qdrant
- tests pass without real API calls
- README is complete and recruiter-friendly
- `PORTFOLIO_REVIEW.md` explains skills demonstrated

---

# Codex Implementation Prompt

Use this prompt after creating and cloning the new repository.

```txt
You are working inside my new GitHub repository.

Repository name:
customer-support-rag-triage-agent

Goal:
Build a practical AI Engineer portfolio project: a customer support RAG triage agent using a real public support dataset, LangGraph, LangChain, Qdrant, local embeddings, FastAPI, and React/Vite.

Important:
- Use Qdrant as the VectorDB, not Chroma.
- Use a real public customer support / ticket / message dataset.
- Do not use generated synthetic data as the main dataset.
- Synthetic data is allowed only for tests.
- Use Hugging Face datasets as primary data source if available.
- Support CSV import fallback.
- Use Google Gemini API as the primary LLM provider.
- Support Groq API as fallback provider.
- Support Cerebras API as second fallback provider.
- Use the smallest free-tier models that are still practical.
- Keep all provider names and model names configurable through .env.
- Use local sentence-transformers embeddings, not paid embedding APIs.
- Use BAAI/bge-small-en-v1.5 as the default embedding model.
- Add LLM response caching before provider calls.
- Add fallback provider routing.
- Add mock LLM mode for tests.
- Never expose API keys in frontend.
- Never commit .env.
- Keep the project local-first and free-tier friendly.

Recommended default models:
GEMINI_DEFAULT_MODEL=gemini-2.0-flash-lite
GEMINI_FALLBACK_MODEL=gemini-2.0-flash
GROQ_DEFAULT_MODEL=llama-3.1-8b-instant
GROQ_FALLBACK_MODEL=llama-3.3-70b-versatile
CEREBRAS_DEFAULT_MODEL=llama3.1-8b

If any model is unavailable at implementation time, replace it with the lowest currently available free-tier model for that provider and document the change in docs/model_routing.md.

Functional Requirements:
1. Create the modular monorepo structure.
2. Add .env.example with all required variables.
3. Load a real public customer support dataset.
4. Add CSV import fallback.
5. Clean and normalize message, intent, response, and metadata fields.
6. Build document records for vector search.
7. Generate embeddings using BAAI/bge-small-en-v1.5.
8. Store vectors and payloads in Qdrant.
9. Implement top-k semantic retrieval with optional intent filtering.
10. Implement LangGraph workflow:
   - normalize_message
   - classify_intent
   - detect_urgency
   - retrieve_similar_cases
   - generate_support_response
   - grounding_check
   - suggest_next_action
11. Implement LLM provider router with Gemini, Groq, and Cerebras.
12. Add retries, timeout, fallback, degraded mode, and cache.
13. Add FastAPI endpoints:
   - GET /health
   - GET /dataset-info
   - GET /provider-health
   - POST /ingest
   - POST /triage
   - POST /search-similar
   - GET /eval/results
14. Add React/Vite frontend pages:
   - Overview
   - Ticket Triage
   - Semantic Search
   - Agent Trace
   - Evaluation Dashboard
   - Dataset Explorer
   - Provider Status
15. Add evaluation scripts for retrieval, triage, groundedness, latency, cache hit rate, and provider fallback rate.
16. Add Docker Compose with api, frontend, and qdrant.
17. Add tests for provider routing, cache, retriever, API, and workflow.
18. Add README and docs.
19. Create PORTFOLIO_REVIEW.md.

Non-Functional Requirements:
1. Must be free-tier friendly.
2. Must use local embeddings.
3. Must avoid unnecessary LLM calls.
4. Must cache LLM responses.
5. Must support mock LLM mode for tests.
6. Must not call real APIs during tests.
7. Must validate user input.
8. Must not expose provider keys.
9. Must not require deployment for v1.
10. Must be understandable by recruiters and hiring managers.

After implementation:
Create PORTFOLIO_REVIEW.md explaining:
- Implemented features
- AI engineering skills demonstrated
- RAG skills demonstrated
- LangGraph workflow design
- Qdrant usage
- LLM provider routing strategy
- Remaining gaps
- How to present this project in resume and LinkedIn
```
