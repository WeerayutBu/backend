"""Pydantic models that validate and translate HTTP boundary data."""

from typing import Literal

from pydantic import BaseModel, Field

from app.domain import ChatCommand, ChatResult, JobResult, Message


class MessageRequest(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    messages: list[MessageRequest] = Field(min_length=1)
    model: str | None = None
    temperature: float = Field(default=0.2, ge=0, le=2)

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

    @classmethod
    def from_result(cls, job: JobResult) -> "JobStatus":
        result = ChatResponse.from_result(job.result) if job.result else None
        return cls(job_id=job.job_id, status=job.status, result=result)
