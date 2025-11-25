from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
import pandas as pd
from datetime import date
import json

from constants import MWIS_URL
from database.database import DB_CON


@dataclass
class Region:
    country: str
    region: str


def get_regions(path: str) -> list[Region]:
    df = pd.read_csv(path)
    return [Region(row.country, row.region) for row in df.itertuples()]


def get_forecast_html(country: str, region: str):
    """Parse forecast page as HTML"""

    if country not in ["scottish", "english-and-welsh"]:
        raise ValueError(
            "Invalid country specification, must be 'scottish' or 'english-and-welsh'"
        )

    url = MWIS_URL + f"/{country}/{region}"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    return soup


def get_forecast_date(soup: BeautifulSoup, forecast_day: str) -> date:
    """NOT TESTED"""
    headers = soup.find("div", id=forecast_day).find_all("h4")
    date_str = {header.text: header.find_next("p").text for header in headers}[
        "Viewing Forecast For"
    ].splitlines()[2]
    clean_date = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date_str)
    return date.strptime(clean_date, "%A %d %B %Y")


def clean_string(s: str) -> str:
    return " ".join(s.split()).strip()


def scrape_region(country: str, region: str) -> dict[str, dict]:
    """Scrape MWIS for forecast"""
    soup = get_forecast_html(country, region)

    forecast = {}
    forecast[region] = {}

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


def scrape_mwis() -> dict:
    regions: list[Region] = get_regions("regions.csv")

    forecasts = {
        region: scrape_region(country=region.country, region=region.region)
        for region in regions
    }

    return forecasts


# this should run on a schedule
def main():
    mwis_forecasts = scrape_mwis()

    json_string = json.dumps(mwis_forecasts)

    DB_CON.execute(
        f"""
        DROP TABLE forecasts;
        
        CREATE TABLE forecasts (j JSON);
            INSERT INTO forecasts VALUES ({json_string})
        """
    )


if __name__ == "__main__":
    main()
