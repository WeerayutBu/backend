"""ARQ/Redis adapter implementing the job-queue port."""

from arq.connections import ArqRedis
from arq.jobs import Job
from redis.exceptions import RedisError

from app.application.errors import JobNotFound, QueueUnavailable
from app.domain.models import ChatCommand, ChatResult, JobResult


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
        try:
            job = await self.redis.enqueue_job("generate", payload)
            if job is None:
                raise QueueUnavailable
            return job.job_id
        except (RedisError, OSError) as exc:
            raise QueueUnavailable from exc

    async def status(self, job_id: str) -> JobResult:
        try:
            job = Job(job_id, self.redis)
            status = await job.status()
            if status.value == "not_found":
                raise JobNotFound
            result = await job.result_info()
            if result and not result.success:
                return JobResult(job_id=job_id, status="failed", error="Job failed")
            response = ChatResult(**result.result) if result else None
            return JobResult(job_id=job_id, status=status.value, result=response)
        except (RedisError, OSError, TypeError, ValueError) as exc:
            raise QueueUnavailable from exc
