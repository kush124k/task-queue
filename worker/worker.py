from api.routes.jobs import r, STREAM_NAME,  GROUP_NAME
from api.database import engine, Job
from sqlalchemy.orm import Session
import time
import redis
import threading
import random
import sys


CONSUMER_NAME = sys.argv[1] if(len(sys.argv)) > 1 else "worker-1"
MAX_RETRIES = 3
RECLAIM_INTERVAL = 30  #seconds


def process_job(job_id, entry_id):
    with Session(engine) as session:
        job = session.get(Job, job_id)
        if job is None:
            print(f"job {job_id} not found in db- skipping and acking stale entry")
            r.xack(STREAM_NAME, GROUP_NAME,entry_id)
            return
        job.status = "running"
        job.worker_id = CONSUMER_NAME
        print(f"processing: {job.id} - task - {job.task}....")
        session.commit()
        
    

    try:
        time.sleep(2)
        if(random.random()<0.2):
            raise Exception("simulated failure")

        with Session(engine) as session:
            job = session.get(Job, job_id)
            job.status = "success"
            session.commit()

        r.xack(STREAM_NAME, GROUP_NAME, entry_id)

    except Exception as e:
        with Session(engine) as session:
            job = session.get(Job, job_id)
            job.retries += 1

            if(job.retries >= MAX_RETRIES):
                dead = DeadJob(
                    id=job.id,
                    status="failed",
                    task = job.task,
                    created_at = job.created_at,
                    retries = job.retries,
                    failure_reason = str(e)
                )
                session.add(dead)
                job.status = "failed"
                session.commit()
                r.xack(STREAM_NAME, GROUP_NAME, entry_id)
                print(f"job {job_id} moved to dead-letter after {job.retries} retries")
            else:
                job.status = "pending"
                session.commit()
                print(f"job {job_id} failed, retry{job.retries}/{MAX_RETRIES}")

def reclaim_abandoned_jobs():
    result = r.xautoclaim(STREAM_NAME, GROUP_NAME, CONSUMER_NAME, min_idle_time=30000, start_id="0")
    claimed_entries = result[1]
    for entry_id, fields in claimed_entries:
        job_id = fields["job_id"]
        print(f"reclaimed abandoned job: {job_id}")
        process_job(job_id, entry_id)




def workjob():
    reclaim_abandoned_jobs()
    last_reclaim = time.time()

    while True:
        if time.time() - last_reclaim> RECLAIM_INTERVAL:
            reclaim_abandoned_jobs()
            last_reclaim = time.time()
        try:
            entries = r.xreadgroup(GROUP_NAME, CONSUMER_NAME, {STREAM_NAME : ">"}, count=1, block=0)
        except redis.exceptions.TimeoutError:
            continue

        stream_name, messages = entries[0]
        entry_id, fields = messages[0]
        job_id = fields["job_id"]
        process_job(job_id, entry_id)
        
        

    
if __name__ == "__main__":
    print(f"Starting worker : {CONSUMER_NAME}")
    workjob()