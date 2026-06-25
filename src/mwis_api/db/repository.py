from mwis_api.db.models import Forecast


class ForecastRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def insert(self, message: dict):
        rows = []

        for forecast_date, value in message["forecast"].items():
            rows.append(
                Forecast(
                    forecast_date=forecast_date,
                    scraped_at=message["scraped_at"],
                    country=message["country"],
                    region=message["region"],
                    forecast=value,
                )
            )

        with self.session_factory() as session:
            session.add_all(rows)
            session.commit()
