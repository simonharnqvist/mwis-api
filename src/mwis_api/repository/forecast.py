from sqlmodel import Session

from mwis_api.common.models import Forecast
from mwis_api.common.schemas import ForecastMessage


class ForecastRepository:
    def __init__(self, engine):
        self.engine = engine

    def insert(self, message: ForecastMessage) -> None:

        with Session(self.engine) as session:
            rows = [
                Forecast(
                    version=message.version,
                    forecast_date=forecast_date,
                    scraped_at=message.scraped_at,
                    country=message.country,
                    region=message.region,
                    forecast=forecast,
                )
                for forecast_date, forecast in message.forecast.items()
            ]

            session.add_all(rows)
            session.commit()
