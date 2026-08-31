"""HTTP adapter translating requests into application use-case calls."""

from fastapi import APIRouter, HTTPException, status

from app.interface.dependencies import ChatServiceDep, JobServiceDep
from app.interface.schemas import ChatRequest, ChatResponse, JobCreated, JobStatus

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/v1/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, service: ChatServiceDep) -> ChatResponse:
    try:
        result = await service.chat(body.to_command())
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Model provider request failed") from exc
    return ChatResponse.from_result(result)


@router.post("/v1/jobs", response_model=JobCreated, status_code=status.HTTP_202_ACCEPTED)
async def create_job(body: ChatRequest, service: JobServiceDep) -> JobCreated:
    job_id = await service.create_job(body.to_command())
    return JobCreated(job_id=job_id)


@router.get("/v1/jobs/{job_id}", response_model=JobStatus)
async def get_job(job_id: str, service: JobServiceDep) -> JobStatus:
    result = await service.get_job(job_id)
    return JobStatus.from_result(result)
