"""HTTP adapter translating task requests into use-case calls."""

from fastapi import APIRouter, HTTPException, Response, status

from app.application.errors import InvalidTaskUpdate, TaskNotFound
from app.domain.entities import Task
from app.interface.dependencies import CurrentUser, TaskServiceDep
from app.interface.schemas import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/v1/tasks", tags=["tasks"])


def task_not_found() -> HTTPException:
    return HTTPException(status_code=404, detail="Task not found")


@router.get("", response_model=list[TaskResponse])
async def list_tasks(user: CurrentUser, service: TaskServiceDep) -> list[Task]:
    return await service.list_tasks(user.id)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(body: TaskCreate, user: CurrentUser, service: TaskServiceDep) -> Task:
    return await service.create_task(user.id, body.title, body.description)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, user: CurrentUser, service: TaskServiceDep) -> Task:
    try:
        return await service.get_task(task_id, user.id)
    except TaskNotFound as exc:
        raise task_not_found() from exc


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    body: TaskUpdate,
    user: CurrentUser,
    service: TaskServiceDep,
) -> Task:
    try:
        return await service.update_task(
            task_id,
            user.id,
            body.model_dump(exclude_unset=True),
        )
    except TaskNotFound as exc:
        raise task_not_found() from exc
    except InvalidTaskUpdate as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user: CurrentUser,
    service: TaskServiceDep,
) -> Response:
    try:
        await service.delete_task(task_id, user.id)
    except TaskNotFound as exc:
        raise task_not_found() from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
