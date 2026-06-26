from pydantic import BaseModel
from datetime import date, datetime


class ForecastResponse(BaseModel):
    forecast_date: date
    scraped_at: datetime
    country: str
    region: str
    forecast: dict

    model_config = {"from_attributes": True}
