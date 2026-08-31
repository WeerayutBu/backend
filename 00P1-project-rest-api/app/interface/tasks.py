"""HTTP adapter translating task requests into use-case calls."""

from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.domain.entities import Task
from app.interface.dependencies import CurrentUser, TaskServiceDep
from app.interface.schemas import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/v1/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    user: CurrentUser,
    service: TaskServiceDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Task]:
    return await service.list_tasks(user.id, limit, offset)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(body: TaskCreate, user: CurrentUser, service: TaskServiceDep) -> Task:
    return await service.create_task(user.id, body.title, body.description)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, user: CurrentUser, service: TaskServiceDep) -> Task:
    return await service.get_task(task_id, user.id)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    body: TaskUpdate,
    user: CurrentUser,
    service: TaskServiceDep,
) -> Task:
    return await service.update_task(
        task_id,
        user.id,
        body.model_dump(exclude_unset=True),
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user: CurrentUser,
    service: TaskServiceDep,
) -> Response:
    await service.delete_task(task_id, user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
