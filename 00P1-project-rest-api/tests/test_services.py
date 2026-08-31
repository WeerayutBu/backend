from collections.abc import Mapping
from dataclasses import replace
from datetime import UTC, datetime

import pytest

from app.application.errors import InvalidInput, TaskNotFound
from app.application.services import TaskService
from app.domain.entities import Task

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class InMemoryTaskRepository:
    """A test adapter: same port as SQLAlchemy, but no database is required."""

    def __init__(self) -> None:
        self.tasks: dict[int, Task] = {}

    async def list_by_owner(self, owner_id: int, limit: int, offset: int) -> list[Task]:
        owned = [task for task in self.tasks.values() if task.owner_id == owner_id]
        return owned[offset : offset + limit]

    async def find_owned(self, task_id: int, owner_id: int) -> Task | None:
        task = self.tasks.get(task_id)
        return task if task and task.owner_id == owner_id else None

    async def add(self, owner_id: int, title: str, description: str | None) -> Task:
        task = Task(
            id=len(self.tasks) + 1,
            owner_id=owner_id,
            title=title,
            description=description,
            completed=False,
            created_at=datetime.now(UTC),
        )
        self.tasks[task.id] = task
        return task

    async def update_owned(
        self,
        task_id: int,
        owner_id: int,
        changes: Mapping[str, object],
    ) -> Task | None:
        task = await self.find_owned(task_id, owner_id)
        if task is None:
            return None
        updated = replace(task, **changes)
        self.tasks[task_id] = updated
        return updated

    async def delete_owned(self, task_id: int, owner_id: int) -> bool:
        if await self.find_owned(task_id, owner_id) is None:
            return False
        del self.tasks[task_id]
        return True


async def test_task_use_case_without_fastapi_or_sqlalchemy() -> None:
    service = TaskService(InMemoryTaskRepository())

    created = await service.create_task(7, "Learn ports", None)
    updated = await service.update_task(created.id, 7, {"completed": True})
    await service.delete_task(created.id, 7)

    assert updated.completed is True
    with pytest.raises(TaskNotFound):
        await service.get_task(created.id, 7)


async def test_task_use_case_enforces_business_rules() -> None:
    service = TaskService(InMemoryTaskRepository())

    with pytest.raises(InvalidInput, match="Title is required"):
        await service.create_task(7, "   ", None)
