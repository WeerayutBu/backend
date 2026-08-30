from fastapi import APIRouter, HTTPException, Request, status

from app.models import ChatRequest, ChatResponse, JobCreated, JobStatus

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/v1/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, request: Request) -> ChatResponse:
    try:
        return await request.app.state.chat_service.chat(body)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Model provider request failed") from exc


@router.post("/v1/jobs", response_model=JobCreated, status_code=status.HTTP_202_ACCEPTED)
async def create_job(body: ChatRequest, request: Request) -> JobCreated:
    job_id = await request.app.state.job_queue.enqueue(body)
    return JobCreated(job_id=job_id)


@router.get("/v1/jobs/{job_id}", response_model=JobStatus)
async def get_job(job_id: str, request: Request) -> JobStatus:
    return await request.app.state.job_queue.status(job_id)

