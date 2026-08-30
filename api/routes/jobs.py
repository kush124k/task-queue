#handles business logic
from api.database import engine, Job
from sqlalchemy.orm import Session
import redis
import uuid
from datetime import datetime

jobs_db = {}

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

STREAM_NAME = "jobs_stream"
GROUP_NAME = "workers_group"
try:
    r.xgroup_create("job_stream", "workers_group" , id="0", mkstream=True)
except redis.exceptions.ResponseError:
    pass


def rjob(task):
    job_id =str(uuid.uuid4())
    with Session(engine) as session:
        new_job = Job(id=job_id, status="pending", task = task, created_at=datetime.now())
        session.add(new_job)
        session.commit()
    r.xadd(STREAM_NAME , {"job_id" : job_id})
    print(f"putting : {job_id}")
    return job_id
        

