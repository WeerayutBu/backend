"""Business entities with no FastAPI or SQLAlchemy dependencies."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class User:
    id: int
    email: str
    password_hash: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class Task:
    id: int
    owner_id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime
