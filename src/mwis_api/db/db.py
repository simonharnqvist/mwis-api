from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mwis_api.db.models import Base, Forecast
import os


def get_db_url():
    return os.getenv("DB_URL", "postgresql+psycopg2://localhost:5432/mwis")


class Database:
    def __init__(self, db_url: str):
        try:
            self.engine = create_engine(db_url, pool_pre_ping=True)
            self.Session = sessionmaker(bind=self.engine, autoflush=False)
        except Exception as e:
            raise RuntimeError(f"DB connection to {db_url} failed. Error: {e}")

    def create_tables(self):
        Base.metadata.create_all(self.engine)
