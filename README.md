# Task Queue Learning Log 🚀

*A personal scratchpad and developer diary for learning how to build a background task queue with FastAPI, Redis, and SQLAlchemy.*

---

## 🎯 Current Focus
Trying to successfully decouple background job processing from the main web server. Right now, I've got the basic API up, and I'm messing around with Redis Streams to get a worker thread to pick up the jobs.

## 🧠 Concepts I'm Learning / Exploring
- **FastAPI Lifespans:** Using `@asynccontextmanager` to spin up the background worker when the server starts. (Is this the best way? Still figuring it out).
- **Redis Streams (Pub/Sub on steroids):**
  - Using `xreadgroup` and `xack`.
  - Understanding Consumer Groups so multiple workers don't process the same job twice.
- **SQLAlchemy Sessions:** Managing DB state (pending -> running -> success).

## 🚧 What's Broken / Current Blockers
- *[Add current blocker here, e.g., Worker thread crashes silently]*
- Need to verify if the Redis consumer group is actually acknowledging messages (`xack`) correctly.
- The worker is currently just a thread inside the FastAPI app. Eventually, I need to rip it out into its own standalone process.

## 📝 Next Steps / To-Do
- [ ] Stabilize the Redis consumer logic in `worker.py`.
- [ ] Add better error handling (what happens if a job fails?).
- [ ] Figure out Docker Compose so I don't have to manually start Redis and Postgres every time.
- [ ] Separate the worker from `api/main.py` so they can scale independently.

## 📚 Helpful Links & Resources
*(Paste good tutorials, docs, or StackOverflow answers here)*
- [FastAPI Lifespan Docs](https://fastapi.tiangolo.com/advanced/events/)
- [Redis Streams Intro](https://redis.io/docs/data-types/streams-tutorial/)
-

---
**Note to self:** To run this locally right now:
```bash
# Make sure redis and postgres are up!
uv sync
uv run uvicorn api.main:app --reload
```
