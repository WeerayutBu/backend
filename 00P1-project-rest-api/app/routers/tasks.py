from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select

from app.dependencies import CurrentUser, Session
from app.models import Task
from app.schemas import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/v1/tasks", tags=["tasks"])


async def owned_task(task_id: int, user_id: int, session: Session) -> Task:
    task = await session.scalar(
        select(Task).where(Task.id == task_id, Task.owner_id == user_id)
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("", response_model=list[TaskResponse])
async def list_tasks(user: CurrentUser, session: Session) -> list[Task]:
    result = await session.scalars(
        select(Task).where(Task.owner_id == user.id).order_by(Task.created_at.desc())
    )
    return list(result)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(body: TaskCreate, user: CurrentUser, session: Session) -> Task:
    task = Task(owner_id=user.id, **body.model_dump())
    session.add(task)
    await session.flush()
    await session.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, user: CurrentUser, session: Session) -> Task:
    return await owned_task(task_id, user.id, session)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    body: TaskUpdate,
    user: CurrentUser,
    session: Session,
) -> Task:
    task = await owned_task(task_id, user.id, session)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    await session.flush()
    await session.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user: CurrentUser,
    session: Session,
) -> Response:
    task = await owned_task(task_id, user.id, session)
    await session.delete(task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

