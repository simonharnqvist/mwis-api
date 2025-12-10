from mwis_api.scrape import (
    Region,
    get_regions,
    get_forecast_html,
    get_forecast_date,
    clean_string,
)
from datetime import date, timedelta
import pytest
from datetime import datetime


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


def test_get_forecast_html(soup):
    assert soup.find("title").text == "Southern Uplands Forecast"


def test_get_forecast_date(soup):
    # first date should be either today or tomorrow
    forecast_date = datetime.strptime(
        get_forecast_date(soup, forecast_day="Forecast0"), "%Y-%m-%d"
    ).date()
    today = date.today()
    tomorrow = date.today() + timedelta(days=1)
    assert forecast_date == today or forecast_date == tomorrow


def test_clean_string():
    dirty = "\n this is a dirty string      \r\n"
    clean = "this is a dirty string"
    assert clean_string(dirty) == clean
