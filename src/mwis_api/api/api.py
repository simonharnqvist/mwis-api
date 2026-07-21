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

from mwis_api.repository.forecast import ForecastRepository
from mwis_api.api.response_models import ForecastResponse

app = FastAPI()


def get_forecast_repository():
    return ForecastRepository()


@app.get("/forecasts", response_model=List[ForecastResponse])
def retrieve_all_forecasts(repo: ForecastRepository = Depends(get_forecast_repository)):
    return repo.get_all()


@app.get("/forecasts/{region_name}")
def retrieve_region_forecast(
    region_name: str,
    forecast_date: date | None = Query(None),
    repo: ForecastRepository = Depends(get_forecast_repository),
):
    forecast = repo.get_region_forecast(region_name, forecast_date)

    if forecast is None:
        raise HTTPException(
            status_code=404,
            detail="Forecast not found",
        )

    return forecast.forecast
