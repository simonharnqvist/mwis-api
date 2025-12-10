from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
import pandas as pd
from datetime import date
import json
import re
from pathlib import Path
import os
from sqlmodel import Session, delete, SQLModel

from constants import MWIS_URL
from mwis_api.models import Forecast
from mwis_api.database import engine

from sqlmodel import inspect, select


@dataclass
class Region:
    country: str
    region: str


def get_regions(path: str | Path) -> list[Region]:
    df = pd.read_csv(path)
    return [Region(row.country, row.region) for row in df.itertuples()]


def get_forecast_html(country: str, region: str):
    """Parse forecast page as HTML"""

    if country not in ["scottish", "english-and-welsh"]:
        raise ValueError(
            "Invalid country specification, must be 'scottish' or 'english-and-welsh'"
        )

    url = MWIS_URL + f"/{country}/{region}"
    requests.get(url).raise_for_status()
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    return soup


def get_forecast_date(soup: BeautifulSoup, forecast_day: str) -> str:
    headers = soup.find("div", id=forecast_day).find_all("h4")
    date_str = {header.text: header.find_next("p").text for header in headers}[
        "Viewing Forecast For"
    ].splitlines()[2]
    clean_date = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date_str)
    return str(date.strptime(clean_date, "%A %d %B %Y"))


def clean_string(s: str) -> str:
    return " ".join(s.split()).strip()


def scrape_region(country: str, region: str) -> dict[str, dict]:
    """Scrape MWIS for forecast"""
    soup = get_forecast_html(country, region)

    forecast = {}

    for forecast_day in ["Forecast0", "Forecast1", "Forecast2"]:

        forecast_date = get_forecast_date(soup, forecast_day=forecast_day)

        headers = soup.find("div", id=forecast_day).find_all("h4")
        forecast[forecast_date] = {
            header.text: clean_string(header.find_next("p").text) for header in headers
        }

        forecast[forecast_date]["Last Updated"] = clean_string(
            soup.find("div", id="Forecast0").find("small").text
        ).replace("Last updated ", "")
        forecast[forecast_date]["Forecast Area"] = (
            soup.find("div", class_="forecast-area").find("h1").text
        )

        forecast[forecast_date].pop("Viewing Forecast For")

    return forecast


def scrape_mwis(regions_file: str | Path) -> dict:
    regions: list[Region] = get_regions(regions_file)

    forecasts = {
        region.region: scrape_region(country=region.country, region=region.region)
        for region in regions
    }

    return forecasts


# this should run on a schedule
def main():
    script_path = os.path.abspath(__file__)
    regions_path = Path(script_path).parent.joinpath("regions.csv")

    mwis_forecasts = scrape_mwis(regions_path)
    # print(mwis_forecasts)

    SQLModel.metadata.create_all(engine)
    inspector = inspect(engine)
    print(inspector.get_table_names())

    with Session(engine) as session:
        session.exec(delete(Forecast))

        for region, data in mwis_forecasts.items():
            session.add(Forecast(region=region, data=data))

        session.commit()


if __name__ == "__main__":
    main()
