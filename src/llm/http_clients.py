from typing import Any

import httpx

from src.llm.base import LLMRequest, ProviderResponse


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: str, timeout_seconds: float) -> None:
        self.api_key = api_key
        self.client = httpx.Client(timeout=timeout_seconds)

    def generate(self, request: LLMRequest) -> ProviderResponse:
        response = self.client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{request.model}:generateContent",
            params={"key": self.api_key},
            json={
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": self._combined_prompt(request)}],
                    }
                ],
                "generationConfig": {
                    "temperature": request.temperature,
                    "maxOutputTokens": request.max_output_tokens,
                    "responseMimeType": "application/json",
                },
            },
        )
        response.raise_for_status()
        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return ProviderResponse(text=text, provider=self.name, model=request.model)

    @staticmethod
    def _combined_prompt(request: LLMRequest) -> str:
        if not request.context:
            return request.prompt
        return f"{request.prompt}\n\nRetrieved context:\n{request.context}"


class OpenAICompatibleProvider:
    def __init__(
        self,
        name: str,
        api_key: str,
        base_url: str,
        timeout_seconds: float,
    ) -> None:
        self.name = name
        self.client = httpx.Client(
            base_url=base_url,
            timeout=timeout_seconds,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    def generate(self, request: LLMRequest) -> ProviderResponse:
        response = self.client.post(
            "/chat/completions",
            json={
                "model": request.model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Return valid JSON only. Never invent policy or unsupported facts."
                        ),
                    },
                    {
                        "role": "user",
                        "content": self._combined_prompt(request),
                    },
                ],
                "temperature": request.temperature,
                "max_tokens": request.max_output_tokens,
                "response_format": {"type": "json_object"},
            },
        )
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        text = data["choices"][0]["message"]["content"]
        return ProviderResponse(text=text, provider=self.name, model=request.model)

    @staticmethod
    def _combined_prompt(request: LLMRequest) -> str:
        if not request.context:
            return request.prompt
        return f"{request.prompt}\n\nRetrieved context:\n{request.context}"
