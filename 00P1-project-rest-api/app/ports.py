"""Interfaces required by the application services."""

from collections.abc import Mapping
from typing import Protocol

from app.domain import Task, User


class UserRepository(Protocol):
    async def find_by_email(self, email: str) -> User | None: ...

    async def find_by_id(self, user_id: int) -> User | None: ...

    async def add(self, email: str, password_hash: str) -> User: ...


class TaskRepository(Protocol):
    async def list_by_owner(self, owner_id: int) -> list[Task]: ...

    async def find_owned(self, task_id: int, owner_id: int) -> Task | None: ...

    async def add(self, owner_id: int, title: str, description: str | None) -> Task: ...

    async def update_owned(
        self,
        task_id: int,
        owner_id: int,
        changes: Mapping[str, object],
    ) -> Task | None: ...

    async def delete_owned(self, task_id: int, owner_id: int) -> bool: ...


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...

    def verify(self, password: str, password_hash: str) -> bool: ...


class TokenService(Protocol):
    def create(self, user_id: int) -> str: ...

    def read_user_id(self, token: str) -> int: ...
