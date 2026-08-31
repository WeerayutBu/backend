"""Application data with no FastAPI, Pydantic, Redis, or HTTP dependencies."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class Message:
    role: Literal["system", "user", "assistant"]
    content: str


@dataclass(frozen=True, slots=True)
class ChatCommand:
    messages: tuple[Message, ...]
    model: str | None = None
    temperature: float = 0.2


@dataclass(frozen=True, slots=True)
class ChatResult:
    content: str
    model: str
    cached: bool = False


@dataclass(frozen=True, slots=True)
class JobResult:
    job_id: str
    status: str
    result: ChatResult | None = None
