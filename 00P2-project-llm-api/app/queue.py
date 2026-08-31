"""ARQ/Redis adapter implementing the job-queue port."""

from arq.connections import ArqRedis
from arq.jobs import Job

from app.domain import ChatCommand, ChatResult, JobResult


class ArqJobQueue:
    def __init__(self, redis: ArqRedis) -> None:
        self.redis = redis

    async def enqueue(self, command: ChatCommand) -> str:
        payload = {
            "messages": [
                {"role": message.role, "content": message.content}
                for message in command.messages
            ],
            "model": command.model,
            "temperature": command.temperature,
        }
        job = await self.redis.enqueue_job("generate", payload)
        if job is None:
            raise RuntimeError("Unable to enqueue job")
        return job.job_id

    async def status(self, job_id: str) -> JobResult:
        job = Job(job_id, self.redis)
        status = await job.status()
        result = await job.result_info()
        response = ChatResult(**result.result) if result and result.success else None
        return JobResult(job_id=job_id, status=status.value, result=response)
