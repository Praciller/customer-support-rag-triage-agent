FROM node:24-alpine AS frontend

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim

RUN useradd -m -u 1000 user
USER user

ENV PATH="/home/user/.local/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_ENV=production \
    API_HOST=0.0.0.0 \
    API_PORT=7860 \
    DEMO_MODE=true \
    MOCK_LLM_MODE=true \
    ALLOW_PUBLIC_INGEST=false \
    QDRANT_MODE=local \
    QDRANT_PATH=/tmp/qdrant \
    LLM_CACHE_DIR=/tmp/llm-cache \
    EMBEDDING_PROVIDER=fastembed \
    EMBEDDING_DEVICE=cpu \
    EMBEDDING_BATCH_SIZE=8 \
    TOKENIZERS_PARALLELISM=false

WORKDIR /home/user/app
COPY --chown=user:user requirements.production.txt ./
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.production.txt

COPY --chown=user:user . .
COPY --from=frontend --chown=user:user /frontend/dist frontend/dist

EXPOSE 7860
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "7860"]
