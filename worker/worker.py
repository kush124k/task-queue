from api.routes.jobs import r, STREAM_NAME,  GROUP_NAME
from api.database import engine, Job
from sqlalchemy.orm import Session
import time
import threading

CONSUMER_NAME = "worker-1"

def workjob():
    while True:
        entries = r.xreadgroup(GROUP_NAME, CONSUMER_NAME, {STREAM_NAME : ">"}, count=1, block=0)
        stream_name, messages = extries[0]
        entry_id, fields = messages[0]
        job_id = fields["jobs_id"]

        with Session(engine) as session:
            job = session.get(Job, job_id)
            job.status = "running"
            session.commit()
            print(f"processing: {job.id} - task: {job.task} (printed using db stored info)")
        
        print(f"processing : {job_id} (printed using  redis storage)")
        time.sleep(2)

        with  Session(engine) as session:
            job = session.get(Job, job_id)
            job.status = "success"
            session.commit()

        r.xack(STREAM_NAME, GROUP_NAME, entry_id)

def start_worker():
    thread = threading.Thread(target = workjob, daemon = True)
    thread.start()
    
