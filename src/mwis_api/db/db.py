from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mwis_api.db.models import Base


class Database:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine, autoflush=False)

    def create_tables(self):
        Base.metadata.create_all(self.engine)
