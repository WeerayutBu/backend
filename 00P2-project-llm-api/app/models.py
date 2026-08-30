from typing import Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    messages: list[Message] = Field(min_length=1)
    model: str | None = None
    temperature: float = Field(default=0.2, ge=0, le=2)


class ChatResponse(BaseModel):
    content: str
    model: str
    cached: bool = False


class JobCreated(BaseModel):
    job_id: str
    status: Literal["queued"] = "queued"


class JobStatus(BaseModel):
    job_id: str
    status: str
    result: ChatResponse | None = None

