# Distributed Task Queue

A backend task queue system built from scratch in Python — a simplified Celery/Sidekiq — supporting asynchronous job execution, at-least-once delivery, automatic retries with exponential backoff-style reclaim, dead-letter handling, and horizontal worker scaling. Built to understand distributed systems fundamentals: message brokers, consumer groups, idempotency, and failure recovery.

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Client    │─────▶│   FastAPI    │─────▶│  Redis Streams   │
│ (POST job)  │      │   (api/)     │      │ (Consumer Group) │
└─────────────┘      └──────┬───────┘      └────────┬─────────┘
                             │                        │
                             ▼                        ▼
                      ┌──────────────┐      ┌──────────────────┐
                      │  PostgreSQL  │◀─────│  Worker(s)       │
                      │ (job state)  │      │  (worker/)       │
                      └──────────────┘      │  scales to N     │
                                             └──────────────────┘
```

- **API (FastAPI)** — accepts job submissions, writes job state to Postgres, pushes the job id onto a Redis Stream, and serves status/stats queries.
- **Redis Streams + Consumer Groups** — the message broker. Provides at-least-once delivery: a job is only removed from the pending list once a worker explicitly acknowledges (`XACK`) it, so a worker crash mid-job doesn't lose the job.
- **PostgreSQL** — the durable source of truth for job state (`pending` → `running` → `success`/`failed`), survives restarts unlike an in-memory store.
- **Worker(s)** — independent processes that pull jobs from the shared consumer group, execute them, and update status. Multiple workers can run concurrently, each with a unique consumer name, and Redis handles distributing work across them without any custom coordination code.

## Features

- **Async job submission & status polling** — `POST /postjob`, `GET /jobs/{id}`
- **At-least-once delivery** via Redis Streams consumer groups
- **Automatic retries** — failed jobs are retried up to a configurable limit
- **Dead-letter queue** — jobs that exceed max retries move to a separate `deadjobs` table with a failure reason, instead of retrying forever
- **Crash recovery** — periodic reclaim of jobs abandoned by a crashed worker (via `XAUTOCLAIM`), so failed workers don't silently lose in-flight jobs
- **Horizontal scaling** — run any number of worker processes/containers against the same queue
- **Per-worker attribution** — every job records which worker processed it, enabling throughput analysis per worker
- **Live dashboard** — WebSocket-pushed real-time view of queue depth, job status breakdown, and per-worker throughput
- **Fully containerized** — API, workers (3 replicas by default), Redis, and Postgres all run via Docker Compose

## Tech Stack

- **Python 3.12**, **FastAPI**, **uv** (dependency management)
- **Redis** (Streams, Consumer Groups)
- **PostgreSQL** + **SQLAlchemy** (ORM)
- **Docker Compose**
- **httpx** (load testing)

## Running Locally

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

This starts Postgres, Redis, Adminer (DB admin UI on `:8080`), the API (`:8000`), and 3 worker replicas.

Submit a job:
```bash
curl -X POST http://localhost:8000/postjob -H "Content-Type: application/json" -d '{"task": "example"}'
```

Check status:
```bash
curl http://localhost:8000/jobs/<job_id>
```

View live stats:
```bash
curl http://localhost:8000/stats
```

Dashboard: open `http://localhost:8000/static/dashboard.html` in a browser.

## Load Testing

```bash
uv run python scripts/loadtest.py
```

Submits a batch of jobs concurrently and reports total throughput (jobs/sec), useful for comparing performance across different worker counts.

## Load Test Findings

Running 50 concurrent jobs (with a ~20% simulated failure rate per job) across 3 workers took ~109s to fully complete, well above the theoretical best case of ~33s (50 jobs / 3 workers × 2s each). The gap comes almost entirely from failure recovery: a failed job returns to Redis's pending list unacknowledged, and is only picked up again once it's been idle past `min_idle_time` (30s) *and* a worker's periodic reclaim cycle (every 30s) happens to run. Under this simulated failure rate, a meaningful share of jobs pay a 30-90s recovery tax before their retry is even attempted — meaning failure recovery, not job execution, is the dominant cost in this system as currently tuned.

In a real system, this would be addressed by tuning `min_idle_time` and the reclaim interval down, or by pushing failed jobs back onto the stream immediately with exponential backoff instead of relying solely on periodic reclaim — trading a bit more constant Redis polling load for meaningfully lower recovery latency.

## Key Design Decisions

- **Redis Streams over a plain list/queue** — chosen specifically for consumer group semantics: multiple workers can share one stream safely, and unacknowledged messages are automatically recoverable, which a simple `LPUSH`/`RPOP` queue can't provide.
- **Separate Postgres table from the Redis stream** — Redis holds only "this job needs attention"; Postgres holds the actual state and history. This keeps the queue and the source of truth decoupled, and means job history survives even if Redis data is cleared.
- **Idempotency-aware retries** — reclaimed jobs check current DB status before re-executing, so a job already marked `success` isn't redundantly reprocessed if a delivery race occurs.

## What I'd Add Next

- Alembic migrations (schema changes currently require manual table drop/recreate)
- Authentication on the `/admin/reset` endpoint
- Priority queues / scheduled job execution
- Persistent storage for Redis (currently in-memory only within its container)