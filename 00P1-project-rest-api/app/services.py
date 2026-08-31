"""Application use cases independent of HTTP and database frameworks."""

from collections.abc import Mapping

from app.domain import Task, User
from app.errors import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    InvalidTaskUpdate,
    InvalidToken,
    TaskNotFound,
)
from app.ports import PasswordHasher, TaskRepository, TokenService, UserRepository


class AuthService:
    def __init__(
        self,
        users: UserRepository,
        passwords: PasswordHasher,
        tokens: TokenService,
    ) -> None:
        self.users = users
        self.passwords = passwords
        self.tokens = tokens

    async def register(self, email: str, password: str) -> User:
        if await self.users.find_by_email(email):
            raise EmailAlreadyRegistered

        password_hash = self.passwords.hash(password)
        return await self.users.add(email, password_hash)

    async def login(self, email: str, password: str) -> str:
        user = await self.users.find_by_email(email)
        if user is None or not self.passwords.verify(password, user.password_hash):
            raise InvalidCredentials
        return self.tokens.create(user.id)

    async def authenticate(self, token: str) -> User:
        user_id = self.tokens.read_user_id(token)
        user = await self.users.find_by_id(user_id)
        if user is None:
            raise InvalidToken
        return user


class TaskService:
    allowed_changes = {"title", "description", "completed"}

    def __init__(self, tasks: TaskRepository) -> None:
        self.tasks = tasks

    async def list_tasks(self, owner_id: int) -> list[Task]:
        return await self.tasks.list_by_owner(owner_id)

    async def create_task(
        self,
        owner_id: int,
        title: str,
        description: str | None,
    ) -> Task:
        return await self.tasks.add(owner_id, title, description)

    async def get_task(self, task_id: int, owner_id: int) -> Task:
        task = await self.tasks.find_owned(task_id, owner_id)
        if task is None:
            raise TaskNotFound
        return task

    async def update_task(
        self,
        task_id: int,
        owner_id: int,
        changes: Mapping[str, object],
    ) -> Task:
        if unknown := set(changes) - self.allowed_changes:
            raise InvalidTaskUpdate(f"Unsupported fields: {', '.join(sorted(unknown))}")
        if "title" in changes and changes["title"] is None:
            raise InvalidTaskUpdate("Title cannot be null")

        task = await self.tasks.update_owned(task_id, owner_id, changes)
        if task is None:
            raise TaskNotFound
        return task

    async def delete_task(self, task_id: int, owner_id: int) -> None:
        if not await self.tasks.delete_owned(task_id, owner_id):
            raise TaskNotFound
