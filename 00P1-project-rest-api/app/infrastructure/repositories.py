"""SQLAlchemy adapters implementing the repository ports."""

from collections.abc import Mapping

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.errors import EmailAlreadyRegistered
from app.domain.entities import Task, User
from app.infrastructure.models import Task as TaskRecord
from app.infrastructure.models import User as UserRecord


def to_user(record: UserRecord) -> User:
    return User(
        id=record.id,
        email=record.email,
        password_hash=record.password_hash,
        created_at=record.created_at,
    )


def to_task(record: TaskRecord) -> Task:
    return Task(
        id=record.id,
        owner_id=record.owner_id,
        title=record.title,
        description=record.description,
        completed=record.completed,
        created_at=record.created_at,
    )


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_by_email(self, email: str) -> User | None:
        record = await self.session.scalar(select(UserRecord).where(UserRecord.email == email))
        return to_user(record) if record else None

    async def find_by_id(self, user_id: int) -> User | None:
        record = await self.session.get(UserRecord, user_id)
        return to_user(record) if record else None

    async def add(self, email: str, password_hash: str) -> User:
        record = UserRecord(email=email, password_hash=password_hash)
        self.session.add(record)
        try:
            await self.session.flush()
        except IntegrityError as exc:
            raise EmailAlreadyRegistered from exc
        await self.session.refresh(record)
        return to_user(record)


class SqlAlchemyTaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_owner(self, owner_id: int, limit: int, offset: int) -> list[Task]:
        records = await self.session.scalars(
            select(TaskRecord)
            .where(TaskRecord.owner_id == owner_id)
            .order_by(TaskRecord.created_at.desc(), TaskRecord.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return [to_task(record) for record in records]

    async def find_owned(self, task_id: int, owner_id: int) -> Task | None:
        record = await self._find_record(task_id, owner_id)
        return to_task(record) if record else None

    async def add(self, owner_id: int, title: str, description: str | None) -> Task:
        record = TaskRecord(owner_id=owner_id, title=title, description=description)
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return to_task(record)

    async def update_owned(
        self,
        task_id: int,
        owner_id: int,
        changes: Mapping[str, object],
    ) -> Task | None:
        record = await self._find_record(task_id, owner_id)
        if record is None:
            return None
        for field, value in changes.items():
            setattr(record, field, value)
        await self.session.flush()
        await self.session.refresh(record)
        return to_task(record)

    async def delete_owned(self, task_id: int, owner_id: int) -> bool:
        record = await self._find_record(task_id, owner_id)
        if record is None:
            return False
        await self.session.delete(record)
        return True

    async def _find_record(self, task_id: int, owner_id: int) -> TaskRecord | None:
        return await self.session.scalar(
            select(TaskRecord).where(
                TaskRecord.id == task_id,
                TaskRecord.owner_id == owner_id,
            )
        )
