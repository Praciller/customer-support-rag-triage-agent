from __future__ import annotations

from typing import Any

import httpx

from src.llm.base import LLMRequest, ProviderResponse


class ExternalProvider:
    """Generic server-side adapter for an externally hosted GenAI endpoint."""

    name = "external"

    def __init__(
        self,
        endpoint: str,
        api_key: str = "",
        timeout_seconds: float = 30,
        client: httpx.Client | None = None,
    ) -> None:
        endpoint = endpoint.strip()
        if not endpoint:
            raise ValueError("External inference endpoint is required")
        self.endpoint = endpoint
        self.api_key = api_key.strip()
        self._client = client or httpx.Client(timeout=timeout_seconds)

    def generate(self, request: LLMRequest) -> ProviderResponse:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = self._client.post(
            self.endpoint,
            headers=headers,
            json={
                "task": request.task,
                "workflow_instructions": request.workflow_instructions,
                "user_ticket": request.user_ticket,
                "candidate_response": request.candidate_response,
                "evidence": [item.to_provider_payload() for item in request.evidence],
                "model": request.model,
                "temperature": request.temperature,
                "max_output_tokens": request.max_output_tokens,
            },
        )
        response.raise_for_status()
        payload: Any = response.json()
        if not isinstance(payload, dict):
            raise ValueError("External inference response must be a JSON object")
        text = payload.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("External inference response must contain non-empty text")
        model = payload.get("model")
        if not isinstance(model, str) or not model.strip():
            model = request.model
        return ProviderResponse(text=text, provider=self.name, model=model)
