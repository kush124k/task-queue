from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import json
from pydantic import BaseModel
from contextlib import asynccontextmanager
from api.routes.jobs import rjob, jobs_db, r, STREAM_NAME, GROUP_NAME
from fastapi import FastAPI, HTTPException
from api.database import engine, Job as JobModel, DeadJob, create_table
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": items[item_id]}

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    print("shutting down")


class Job(BaseModel):
    task : str 

app = FastAPI(lifespan = lifespan)

@app.get("/")
async def root():
    return{"message" : "Hello World"}


@app.post("/postjob")
async def postjob(job : Job):

    job_id = rjob(job.task);
    return {"job_id" : job_id}


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    with  Session(engine) as session:
        job = session.get(JobModel, job_id)
        if job is None:
            raise HTTPException(status_code=404, detail = "job not found")
        return {"id": job.id, "status": job.status, "task": job.task, "Created at": job.created_at}

@app.post("/admin/reset")
async def reset_all():
    create_table()
    
    with Session(engine) as session:
        session.query(JobModel).delete()
        session.query(DeadJob).delete()
        session.commit()

    r.delete("job_stream")

    return {"message": "all jobs and stream data cleared"}

@app.get("/stats")
async def get_stats():
    with  Session(engine) as session:
        status_counts = dict(
            session.query(JobModel.status, func.count(JobModel.id))
            .group_by(JobModel.status)
            .all()
        )
        worker_counts = dict(
            session.query(JobModel.worker_id, func.count(JobModel.id))
            .filter(JobModel.worker_id.isnot(None))
            .group_by(JobModel.worker_id)
            .all()
        )
        dead_count = session.query(func.count(DeadJob.id)).scalar()
    queue_depth = r.xlen(STREAM_NAME)
    pending_info = r.xpending(STREAM_NAME,  GROUP_NAME)
    
    return {
        "status_counts":status_counts,
        "worker_counts": worker_counts,
        "dead_letter_count": dead_count,
        "queue_depth": queue_depth,
        "pending_unacked": pending_info["pending"] if  pending_info else 0
    }

@app.websocket("/ws/stats")
async def websocket_stats(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            stats = await get_stats()
            await websocket.send_text(json.dumps(stats))
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)