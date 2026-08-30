<<<<<<< HEAD
g
=======
# Task Queue (Work in Progress)

**Note:** This is a personal Work in Progress (WIP) project. Features, architecture, and setup instructions are subject to change.

## Overview
A lightweight, asynchronous task queue system built with FastAPI, Redis, and SQLAlchemy. It is designed to demonstrate decoupling background job processing from the main API web server.

## Current Architecture
- **API Server:** Built with FastAPI, handling job creation and status retrieval.
- **Message Broker:** Redis Streams to pass messages from the API to the worker.
- **Worker:** A background Python worker thread that consumes jobs from the Redis Stream, processes them, and updates their status in the database.
- **Database:** PostgreSQL (via SQLAlchemy) to persist job metadata and state (e.g., pending, running, success).
- **Package Management:** `uv` is used for managing dependencies and the Python environment.

## Current Status & WIP
- [x] API endpoint to submit a job (`POST /postjob`)
- [x] API endpoint to check job status (`GET /jobs/{job_id}`)
- [x] Redis stream integration for reliable queueing
- [x] Basic worker consuming tasks from the stream
- [ ] Docker compose setup for easy local deployment
- [ ] Improved error handling and job retries
- [ ] Separation of worker process from the main FastAPI server

## Local Setup (WIP)

1. Ensure you have Python 3.12+ and `uv` installed.
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Ensure Redis and PostgreSQL are running locally and accessible.
4. Run the API (which also starts the background worker thread):
   ```bash
   uv run uvicorn api.main:app --reload
   ```

## Personal Roadmap
*Currently focusing on stabilizing the Redis consumer group logic and setting up Docker for easier local testing.*
>>>>>>> af7ac800a714961c6be0dce4b31a21262649e0d9
