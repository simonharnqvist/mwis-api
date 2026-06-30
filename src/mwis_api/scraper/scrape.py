from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
import logging
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup

from .config import MWIS_URL, RABBITMQ_PARAMS
from .publisher import RabbitMQPublisher
from mwis_api.common.models import Region, ForecastMessage
from mwis_api.scraper.regions import mwis_regions

logger = logging.getLogger(__name__)


def get_regions(path: str | Path) -> list[Region]:
    df = pd.read_csv(path)
    return [Region(row.country, row.region) for row in df.itertuples()]


def get_forecast_html(country: str, region: str) -> BeautifulSoup:
    """Fetch and parse a MWIS forecast page."""

    if country not in ("scottish", "english-and-welsh"):
        raise ValueError("country must be either 'scottish' or 'english-and-welsh'")

    url = f"{MWIS_URL}/{country}/{region}/text"
    logger.info(msg=f"URL: {url}")

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    return BeautifulSoup(response.text, "html.parser")


def get_forecast_date(soup: BeautifulSoup, forecast_day: str) -> str:
    headers = soup.find("div", id=forecast_day).find_all("h4")

    date_str = {header.text: header.find_next("p").text for header in headers}[
        "Viewing Forecast For"
    ].splitlines()[2]

    clean_date = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date_str)

    return str(datetime.strptime(clean_date, "%A %d %B %Y").date())


def clean_string(s: str) -> str:
    return " ".join(s.split()).strip()


def get_region_forecast(soup: BeautifulSoup) -> dict[str, dict]:

    forecast: dict[str, dict] = {}

    try:
        soup.find("div", id="Forecast0")
    except Exception as e:
        print(e, soup)

    last_updated = clean_string(
        soup.find("div", id="Forecast0").find("small").text
    ).replace("Last updated ", "")

    forecast_area = soup.find("div", class_="forecast-area").find("h1").text

    for forecast_day in ("Forecast0", "Forecast1", "Forecast2"):

        forecast_date = get_forecast_date(soup, forecast_day)

        headers = soup.find("div", id=forecast_day).find_all("h4")

        day_forecast = {
            header.text: clean_string(header.find_next("p").text) for header in headers
        }

        day_forecast.pop("Viewing Forecast For", None)
        day_forecast["Last Updated"] = last_updated
        day_forecast["Forecast Area"] = forecast_area

        forecast[forecast_date] = day_forecast

    return forecast


def scrape_region(country: str, region: str) -> dict[str, dict]:
    """Scrape the three-day MWIS forecast for a single region."""

    soup = get_forecast_html(country, region)
    forecast = get_region_forecast(soup)

    return forecast


def scrape_mwis(regions: list[Region]) -> list[ForecastMessage]:
    messages: list[ForecastMessage] = []

    for region in regions:
        logger.info("Scraping %s in %s", region.region, region.country)
        # logger.info(get_forecast_html(region.country, region.region))
        # soup = get_forecast_html(region.country, region.region)
        # logger.info(get_region_forecast(soup))

        messages.append(
            ForecastMessage(
                version=1,
                region=region.region,
                country=region.country,
                scraped_at=datetime.now(timezone.utc).isoformat(),
                forecast=scrape_region(
                    country=region.country,
                    region=region.region,
                ),
            )
        )

    return messages


def publish_forecasts(
    forecasts: list[ForecastMessage], publisher: RabbitMQPublisher
) -> None:
    for forecast in forecasts:
        publisher.publish(forecast)
        logger.info("Published forecast for %s", forecast.region)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    forecasts = scrape_mwis(regions=mwis_regions)

    publisher = RabbitMQPublisher(connection_params=RABBITMQ_PARAMS)

    try:
        publish_forecasts(forecasts=forecasts, publisher=publisher)
    finally:
        publisher.close()


if __name__ == "__main__":
    main()
