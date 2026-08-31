"""Application use cases independent of HTTP and database frameworks."""

from collections.abc import Mapping

from app.application.errors import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    InvalidInput,
    InvalidTaskUpdate,
    InvalidToken,
    TaskNotFound,
)
from app.application.ports import PasswordHasher, TaskRepository, TokenService, UserRepository
from app.domain.entities import Task, User

MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 5_000
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128


def validate_title(title: object) -> str:
    if not isinstance(title, str):
        raise InvalidInput("Title is required")
    normalized = title.strip()
    if not normalized:
        raise InvalidInput("Title is required")
    if len(normalized) > MAX_TITLE_LENGTH:
        raise InvalidInput(f"Title must contain at most {MAX_TITLE_LENGTH} characters")
    return normalized


def validate_description(description: object) -> str | None:
    if description is not None and not isinstance(description, str):
        raise InvalidInput("Description must be text or null")
    if isinstance(description, str) and len(description) > MAX_DESCRIPTION_LENGTH:
        raise InvalidInput(
            f"Description must contain at most {MAX_DESCRIPTION_LENGTH} characters"
        )
    return description


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
        email = email.strip().lower()
        if not MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH:
            raise InvalidInput(
                f"Password must contain {MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH} characters"
            )
        if await self.users.find_by_email(email):
            raise EmailAlreadyRegistered

        password_hash = await self.passwords.hash(password)
        return await self.users.add(email, password_hash)

    async def login(self, email: str, password: str) -> str:
        user = await self.users.find_by_email(email.strip().lower())
        if user is None or not await self.passwords.verify(password, user.password_hash):
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

    async def list_tasks(self, owner_id: int, limit: int = 50, offset: int = 0) -> list[Task]:
        if not 1 <= limit <= 100 or offset < 0:
            raise InvalidInput("Invalid pagination")
        return await self.tasks.list_by_owner(owner_id, limit, offset)

    async def create_task(
        self,
        owner_id: int,
        title: str,
        description: str | None,
    ) -> Task:
        return await self.tasks.add(
            owner_id,
            validate_title(title),
            validate_description(description),
        )

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
        validated = dict(changes)
        if "title" in validated:
            try:
                validated["title"] = validate_title(validated["title"])
            except InvalidInput as exc:
                raise InvalidTaskUpdate(str(exc)) from exc
        if "description" in validated:
            try:
                validated["description"] = validate_description(validated["description"])
            except InvalidInput as exc:
                raise InvalidTaskUpdate(str(exc)) from exc
        if "completed" in validated and not isinstance(validated["completed"], bool):
            raise InvalidTaskUpdate("Completed must be true or false")

        task = await self.tasks.update_owned(task_id, owner_id, validated)
        if task is None:
            raise TaskNotFound
        return task

    async def delete_task(self, task_id: int, owner_id: int) -> None:
        if not await self.tasks.delete_owned(task_id, owner_id):
            raise TaskNotFound
