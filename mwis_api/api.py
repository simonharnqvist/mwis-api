from fastapi import FastAPI, Query, Depends
from fastapi.exceptions import HTTPException
from typing import Optional, List
from sqlmodel import select, Session

from mwis_api.database import get_db_session, init_db
from mwis_api.models import Forecast, ForecastRead


async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/forecasts", response_model=List[ForecastRead])
def retrieve_all_forecasts(session: Session = Depends(get_db_session)):

    forecasts = session.exec(select(Forecast)).all()
    return forecasts


@app.get("/forecasts/{region_name}")
def retrieve_region_forecast(
    region_name: str,
    date: Optional[str] = Query(None, description="Filter by date"),
    session: Session = Depends(get_db_session),
):
    if date is None:
        stmt = select(Forecast).where(Forecast.region == region_name)
        forecast = session.exec(stmt).first()

        if not forecast:
            raise HTTPException(
                status_code=404, detail=f"Region '{region_name}' not found"
            )

        return forecast.data if forecast else {}
    else:
        stmt = select(Forecast.data[date].label("day_data")).where(
            Forecast.region == region_name
        )
        day_data = session.exec(stmt).scalar()

        if day_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Data for date {date} not found for region '{region_name}'",
            )

        return {date: day_data} if day_data else {}
