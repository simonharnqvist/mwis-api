from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import JSON
from typing import Dict


# for ORM
class Forecast(SQLModel, table=True):
    region: str = Field(primary_key=True)
    data: dict = Field(sa_column=Column(JSON))


# response schema
class ForecastRead(SQLModel):
    region: str
    data: Dict
