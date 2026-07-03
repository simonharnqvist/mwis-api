from fastapi import FastAPI, Query, Depends
from fastapi.exceptions import HTTPException
from typing import Optional, List
from sqlmodel import select, Session
from sqlalchemy import create_engine
from datetime import date
from contextlib import asynccontextmanager
from mwis_api.api.response_models import ForecastResponse
from mwis_api.common.models import Forecast
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DB URL not provided")

app = FastAPI()


def get_db_session():
    try:
        engine = create_engine(DATABASE_URL)
        with Session(engine) as session:
            yield session
    except Exception as e:
        raise ConnectionError(
            f"DB connection to {DATABASE_URL} refused or failed. Error : {e}"
        )


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
