from sqlmodel import SQLModel, Session, create_engine
from contextlib import contextmanager
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mwis.db")

engine = create_engine(DATABASE_URL, echo=True)


# FastAPI dependency
def get_db_session():
    with Session(engine) as session:
        yield session


def init_db():
    SQLModel.metadata.create_all(engine)


# for scripts
@contextmanager
def db_session():
    with Session(engine) as session:
        yield session
