.PHONY: setup lint format test eval api demo clean

DEMO_ENV = DEMO_MODE=true MOCK_LLM_MODE=true QDRANT_MODE=memory EMBEDDING_PROVIDER=hashing RETRIEVAL_MIN_SCORE=0 LLM_CACHE_ENABLED=false

setup:
	python -m pip install -r requirements.txt

lint:
	ruff check src tests
	ruff format --check src tests

format:
	ruff check --fix src tests
	ruff format src tests

test:
	python -m pytest

eval:
	$(DEMO_ENV) python -m src.evaluation.evaluate_triage

api:
	uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000

demo: eval
	@echo API: GET /health, POST /triage, POST /answer, POST /evaluate, GET /metrics/sample

clean:
	python -c "import shutil; [shutil.rmtree(path, ignore_errors=True) for path in ('.cache', '.data', '.qdrant', '.pytest_cache', '.ruff_cache', 'frontend/dist')]"
