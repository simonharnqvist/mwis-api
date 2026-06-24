from mwis_api.scraping_service.scrape import (
    Region,
    get_regions,
    get_forecast_html,
    get_forecast_date,
    get_region_forecast,
    clean_string,
)
from datetime import date, timedelta
import pytest
from datetime import datetime
import jsonschema


@pytest.fixture
def soup():
    return get_forecast_html("scottish", "southern-uplands")


def test_get_regions():
    assert get_regions("mwis_api/regions.csv") == [
        Region(country="scottish", region="the-northwest-highlands"),
        Region(country="scottish", region="west-highlands"),
        Region(country="scottish", region="cairngorms-np-and-monadhliath"),
        Region(country="scottish", region="southeastern-highlands"),
        Region(country="scottish", region="southern-uplands"),
        Region(country="english-and-welsh", region="lake-district"),
        Region(
            country="english-and-welsh", region="yorkshire-dales-and-north-pennines"
        ),
        Region(country="english-and-welsh", region="peak-district"),
        Region(country="english-and-welsh", region="snowdonia-national-park"),
        Region(country="english-and-welsh", region="brecon-beacons"),
    ]


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
