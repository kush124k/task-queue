from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager
from api.routes.jobs import rjob, jobs_db
from worker.worker import start_worker
from fastapi import FastAPI, HTTPException
from api.database import engine, Job
from sqlalchemy.orm import Session

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": items[item_id]}

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_worker()
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
        job = session.get(Job, job_id)
        if job is None:
            raise HTTPException(status_code=404, detail = "job not found")
        return {"id": job.id, "status": job.status, "task": job.task, "Created at": job.created_at}
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)