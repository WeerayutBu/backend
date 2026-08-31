"""Pydantic models that validate and translate HTTP boundary data."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.models import (
    MAX_MESSAGE_CHARS,
    MAX_MESSAGES,
    MAX_MODEL_CHARS,
    MAX_TOTAL_CHARS,
    ChatCommand,
    ChatResult,
    JobResult,
    Message,
)


class MessageRequest(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)


class ChatRequest(BaseModel):
    messages: list[MessageRequest] = Field(min_length=1, max_length=MAX_MESSAGES)
    model: str | None = Field(default=None, min_length=1, max_length=MAX_MODEL_CHARS)
    temperature: float = Field(default=0.2, ge=0, le=2)

    @model_validator(mode="after")
    def validate_total_size(self) -> "ChatRequest":
        if sum(len(message.content) for message in self.messages) > MAX_TOTAL_CHARS:
            raise ValueError(f"Messages exceed {MAX_TOTAL_CHARS} characters in total")
        return self

    def to_command(self) -> ChatCommand:
        return ChatCommand(
            messages=tuple(Message(message.role, message.content) for message in self.messages),
            model=self.model,
            temperature=self.temperature,
        )


class ChatResponse(BaseModel):
    content: str
    model: str
    cached: bool = False

    @classmethod
    def from_result(cls, result: ChatResult) -> "ChatResponse":
        return cls(content=result.content, model=result.model, cached=result.cached)


class JobCreated(BaseModel):
    job_id: str
    status: Literal["queued"] = "queued"


class JobStatus(BaseModel):
    job_id: str
    status: str
    result: ChatResponse | None = None
    error: str | None = None

    @classmethod
    def from_result(cls, job: JobResult) -> "JobStatus":
        result = ChatResponse.from_result(job.result) if job.result else None
        return cls(job_id=job.job_id, status=job.status, result=result, error=job.error)
