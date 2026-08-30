from typing import Protocol

from arq.connections import ArqRedis
from arq.jobs import Job

from app.models import ChatRequest, ChatResponse, JobStatus


class JobQueue(Protocol):
    async def enqueue(self, request: ChatRequest) -> str: ...

    async def status(self, job_id: str) -> JobStatus: ...


class ArqJobQueue:
    def __init__(self, redis: ArqRedis) -> None:
        self.redis = redis

    async def enqueue(self, request: ChatRequest) -> str:
        job = await self.redis.enqueue_job("generate", request.model_dump(mode="json"))
        if job is None:
            raise RuntimeError("Unable to enqueue job")
        return job.job_id

    async def status(self, job_id: str) -> JobStatus:
        job = Job(job_id, self.redis)
        status = await job.status()
        result = await job.result_info()
        response = ChatResponse.model_validate(result.result) if result and result.success else None
        return JobStatus(job_id=job_id, status=status.value, result=response)

