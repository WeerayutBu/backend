# LLM API

A FastAPI service for direct LLM chat requests and queued background jobs, built to demonstrate essential backend techniques.

## What it includes

- Synchronous and queued chat requests
- OpenAI-compatible model provider
- Async HTTP calls with timeouts and retries
- Redis caching, queues, and workers
- Structured logging and integration tests

## Architecture

FastAPI validates the request, then the router selects the direct or queued path. Direct requests enter the chat service immediately; queued requests wait in Redis until the worker processes them, up to **N concurrently** (`max_jobs`, default: 10). The shared chat service checks the cache before calling the configured provider with timeouts and retries.

```mermaid
flowchart LR
    Client --> API[FastAPI]
    API --> Router[API router]

    Router -->|POST /v1/chat| Service[Chat service]
    Router -->|POST /v1/jobs| Queue[(Redis queue)]

    Queue --> Worker[Worker: N concurrent]
    Worker --> Service

    Service -->|check and store| Cache[(Redis cache)]
    Service -->|cache miss| Gateway[Provider client]
    Gateway -->|response| Service

    Gateway -. choose one .-> OpenAI[OpenAI]
    Gateway -. choose one .-> DeepInfra[DeepInfra]
    Gateway -. choose one .-> vLLM[Local vLLM]
    Gateway -. choose one .-> Ollama[Ollama]
```

## How it works

**Direct chat:** The API checks Redis first. A cache hit returns immediately; a cache miss calls the LLM provider, stores the response, and returns it to the client.

**Background job:** The API queues the request and immediately returns a job ID. A worker runs the same cache-first chat service, stores the job result in Redis, and the client retrieves it through the job-status endpoint.

```mermaid
sequenceDiagram
    participant C as Client
    participant A as FastAPI router
    participant Q as Redis queue
    participant W as Worker
    participant S as Chat service
    participant R as Redis cache
    participant L as Configured provider

    alt Direct chat
        C->>A: POST /v1/chat
        A->>S: Generate response
        S->>R: Check cache
        alt Cache hit
            R-->>S: Cached response
        else Cache miss
            S->>L: Send model request
            L-->>S: Model response
            S->>R: Cache response
        end
        S-->>A: Chat response
        A-->>C: Chat response + request ID
    else Background job
        C->>A: POST /v1/jobs
        A->>Q: Enqueue job
        A-->>C: Job ID
        Q->>W: Deliver job
        W->>S: Generate response
        S->>R: Check cache
        alt Cache hit
            R-->>S: Cached response
        else Cache miss
            S->>L: Send model request
            L-->>S: Model response
            S->>R: Cache response
        end
        S-->>W: Chat response
        W->>Q: Store job result
        C->>A: GET /v1/jobs/{job_id}
        A->>Q: Read status and result
        A-->>C: Job status and result
    end
```

## Run locally

```bash
cp .env.example .env
make sync
make services
make run
```

Start the worker in another terminal:

```bash
make worker
```

## API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/health` | Check whether the API is running. |
| `POST` | `/v1/chat` | Process a chat request and wait for the response. |
| `POST` | `/v1/jobs` | Queue a chat request and return a job ID immediately. |
| `GET` | `/v1/jobs/{job_id}` | Retrieve a queued job's status and result. |

Example request:

```bash
curl http://localhost:8000/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Explain async I/O briefly."}]}'
```

## Test

```bash
make check
```
