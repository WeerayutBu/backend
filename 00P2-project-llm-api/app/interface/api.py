"""HTTP adapter translating requests into application use-case calls."""

from fastapi import APIRouter, Depends, status

from app.interface.dependencies import (
    ChatServiceDep,
    JobServiceDep,
    require_service_api_key,
)
from app.interface.schemas import ChatRequest, ChatResponse, JobCreated, JobStatus

router = APIRouter()
v1 = APIRouter(prefix="/v1", dependencies=[Depends(require_service_api_key)])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@v1.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, service: ChatServiceDep) -> ChatResponse:
    result = await service.chat(body.to_command())
    return ChatResponse.from_result(result)


@v1.post("/jobs", response_model=JobCreated, status_code=status.HTTP_202_ACCEPTED)
async def create_job(body: ChatRequest, service: JobServiceDep) -> JobCreated:
    job_id = await service.create_job(body.to_command())
    return JobCreated(job_id=job_id)


@v1.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job(job_id: str, service: JobServiceDep) -> JobStatus:
    result = await service.get_job(job_id)
    return JobStatus.from_result(result)


router.include_router(v1)
