#handles how data is stored
from sqlalchemy import create_engine, String, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from datetime import datetime
import os

DATABASE_URL = os.environ.get ( "DATABASE_URL", "postgresql://postgres:example@localhost:5432/postgres") 

engine = create_engine(DATABASE_URL)

class Base(DeclarativeBase):
    pass

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    status: Mapped[str] = mapped_column(String)
    worker_id: Mapped[str] = mapped_column(String, nullable=True)
    task: Mapped[str] =  mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    retries: Mapped[int] = mapped_column(default=0)

class DeadJob(Base):
    __tablename__ = "deadjobs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    status: Mapped[str] = mapped_column(String)
    worker_id: Mapped[str] = mapped_column(String, nullable=True)
    task: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    retries: Mapped[int] = mapped_column(default=0)
    failure_reason: Mapped[str] = mapped_column(String)
    

def create_table():
    Base.metadata.create_all(engine)