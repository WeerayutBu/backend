import hashlib
import json

from app.cache import Cache
from app.models import ChatRequest, ChatResponse
from app.provider import LLMProvider


class ChatService:
    def __init__(self, provider: LLMProvider, cache: Cache, cache_ttl_seconds: int) -> None:
        self.provider = provider
        self.cache = cache
        self.cache_ttl_seconds = cache_ttl_seconds

    async def chat(self, request: ChatRequest) -> ChatResponse:
        key = self._cache_key(request)
        cached = await self.cache.get(key)
        if cached:
            return ChatResponse(**cached, cached=True)

        response = await self.provider.chat(request)
        await self.cache.set(key, response.model_dump(exclude={"cached"}), self.cache_ttl_seconds)
        return response

    @staticmethod
    def _cache_key(request: ChatRequest) -> str:
        body = json.dumps(request.model_dump(), sort_keys=True, separators=(",", ":"))
        return f"chat:{hashlib.sha256(body.encode()).hexdigest()}"

