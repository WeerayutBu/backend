"""OpenAI-compatible HTTP adapter implementing the LLM provider port."""

from typing import Any

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.config import Settings
from app.domain import ChatCommand, ChatResult


def is_retryable(exception: BaseException) -> bool:
    if isinstance(exception, (httpx.TimeoutException, httpx.NetworkError)):
        return True
    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code == 429 or exception.response.status_code >= 500
    return False


class OpenAICompatibleProvider:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings
        self.client = client or httpx.AsyncClient(
            base_url=f"{settings.provider_base_url.rstrip('/')}/",
            timeout=settings.request_timeout_seconds,
        )

    async def close(self) -> None:
        await self.client.aclose()

    async def chat(self, command: ChatCommand) -> ChatResult:
        response = await self._request(
            {
                "model": command.model or self.settings.default_model,
                "messages": [
                    {"role": message.role, "content": message.content}
                    for message in command.messages
                ],
                "temperature": command.temperature,
            }
        )
        return ChatResult(
            content=response["choices"][0]["message"]["content"],
            model=response.get("model", command.model or self.settings.default_model),
        )

    def _retry_decorator(self):
        return retry(
            stop=stop_after_attempt(self.settings.max_retries + 1),
            wait=wait_exponential(multiplier=0.25, min=0.25, max=2),
            retry=retry_if_exception(is_retryable),
            reraise=True,
        )

    async def _request(self, payload: dict[str, Any]) -> dict[str, Any]:
        @self._retry_decorator()
        async def send() -> dict[str, Any]:
            headers = {}
            if self.settings.provider_api_key:
                headers["Authorization"] = f"Bearer {self.settings.provider_api_key}"
            response = await self.client.post("chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

        return await send()
