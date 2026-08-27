#handles how data is stored
from sqlalchemy import create_engine, String, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from datetime import datetime

DATABASE_URL = "postgresql://postgres:example@localhost:5432/postgres"

engine = create_engine(DATABASE_URL)

class Base(DeclarativeBase):
    pass

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String,primary_key=True)
    status: Mapped[str] = mapped_column(String)
    task: Mapped[str] =  mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime)

def create_table():
    Base.metadata.create_all(engine)