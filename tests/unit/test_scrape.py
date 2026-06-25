from mwis_api.scraper.scrape import (
    get_forecast_date,
    get_region_forecast,
    clean_string,
    scrape_mwis,
)
from mwis_api.common.models import Region
import pytest
import jsonschema
from bs4 import BeautifulSoup


@pytest.fixture
def soup():
    with open("tests/html_fixtures/Cairngorms NP and Monadhliath Forecast.html") as f:
        html = f.read()

    soup = BeautifulSoup(html, features="html.parser")
    return soup


def test_get_forecast_title(soup):
    assert soup.find("title").text == "Cairngorms NP and Monadhliath Forecast"


def test_get_forecast_date(soup):
    assert get_forecast_date(soup, forecast_day="Forecast0") == "2026-06-24"


def test_forecast_schema(soup):

    forecast = get_region_forecast(soup)

    FORECAST_SCHEMA = {
        "type": "object",
        "required": ["2026-06-24", "2026-06-25", "2026-06-26"],
        "additionalProperties": {
            "type": "object",
            "required": [
                "How windy? (On the Munros)",
                "Effect of the wind on you?",
                "How Wet?",
                "Cloud on the hills?",
                "Chance of cloud free Munros?",
                "Sunshine and air clarity?",
                "How Cold? (at 900m)",
                "Freezing Level",
                "Last Updated",
                "Forecast Area",
            ],
            "additionalProperties": True,
        },
    }

    jsonschema.validate(forecast, FORECAST_SCHEMA)


def test_clean_string():
    dirty = "\n this is a dirty string      \r\n"
    clean = "this is a dirty string"
    assert clean_string(dirty) == clean
