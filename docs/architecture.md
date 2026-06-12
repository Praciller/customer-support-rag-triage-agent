# Architecture

```mermaid
flowchart LR
  UI[React operations console] --> API[FastAPI]
  API --> G[LangGraph triage workflow]
  G --> R[Qdrant retriever]
  R --> E[Local BGE embeddings]
  G --> C[SQLite response cache]
  G --> P[Provider router]
  P --> GM[Gemini]
  P --> GR[Groq]
  P --> CE[Cerebras]
```

The API owns validation and service construction. The seven-node graph owns orchestration.
Retrieval, provider clients, routing, caching, prompts, and configuration remain isolated.
The frontend only calls the backend and never receives provider credentials.
