from fastapi import FastAPI, Query, Depends
from fastapi.exceptions import HTTPException
from typing import Optional, List
from sqlmodel import select, Session
from datetime import date
from mwis_api.api.response_models import ForecastResponse
from mwis_api.db.models import Forecast
from mwis_api.db.db import Database, get_db_url
from contextlib import asynccontextmanager

db: Database | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db
    db = Database(get_db_url())
    db.create_tables()
    yield


app = FastAPI(lifespan=lifespan)


def get_db_session():
    with Session(db.engine) as session:
        yield session


@app.get("/forecasts", response_model=List[ForecastResponse])
def retrieve_all_forecasts(session: Session = Depends(get_db_session)):

    forecasts = session.exec(select(Forecast)).all()
    return forecasts


@app.get("/forecasts/{region_name}")
def retrieve_region_forecast(
    region_name: str,
    forecast_date: date | None = Query(None),
    session: Session = Depends(get_db_session),
):
    stmt = select(Forecast).where(Forecast.region == region_name)

    if forecast_date is None:
        stmt = stmt.order_by(Forecast.forecast_date.desc())
    else:
        stmt = stmt.where(Forecast.forecast_date == forecast_date)

    forecast = session.exec(stmt).first()

    if forecast is None:
        raise HTTPException(status_code=404, detail="Forecast not found")

    return forecast.forecast
