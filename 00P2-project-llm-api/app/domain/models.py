"""Application data with no FastAPI, Pydantic, Redis, or HTTP dependencies."""

from dataclasses import dataclass
from typing import Literal

MAX_MESSAGES = 50
MAX_MESSAGE_CHARS = 20_000
MAX_TOTAL_CHARS = 100_000
MAX_MODEL_CHARS = 200


@dataclass(frozen=True, slots=True)
class Message:
    role: Literal["system", "user", "assistant"]
    content: str


@dataclass(frozen=True, slots=True)
class ChatCommand:
    messages: tuple[Message, ...]
    model: str | None = None
    temperature: float = 0.2

    def __post_init__(self) -> None:
        if not 1 <= len(self.messages) <= MAX_MESSAGES:
            raise ValueError(f"Messages must contain 1-{MAX_MESSAGES} items")
        invalid_message = any(
            not message.content or len(message.content) > MAX_MESSAGE_CHARS
            for message in self.messages
        )
        if invalid_message:
            raise ValueError(f"Each message must contain 1-{MAX_MESSAGE_CHARS} characters")
        if sum(len(message.content) for message in self.messages) > MAX_TOTAL_CHARS:
            raise ValueError(f"Messages must contain at most {MAX_TOTAL_CHARS} characters in total")
        if self.model is not None and not 1 <= len(self.model) <= MAX_MODEL_CHARS:
            raise ValueError(f"Model must contain 1-{MAX_MODEL_CHARS} characters")
        if not 0 <= self.temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")


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
    error: str | None = None
