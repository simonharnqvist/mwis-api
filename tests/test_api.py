import os

os.environ["DATABASE_URL"] = "sqlite:///./tests/test_mwis.db"

from fastapi.testclient import TestClient
import pytest
import json

from mwis_api.api import app

client = TestClient(app)


def test_get_forecasts():
    response = client.get("/forecasts")
    assert response.status_code == 200
    assert "data" in response.json()[0]

    try:
        json.loads(response.text)
    except json.JSONDecodeError:
        pytest.fail("Not valid json")


def test_get_specific_region_forecast():
    response = client.get("/forecasts/southern-uplands")
    assert response.status_code == 200
    assert response.json()["2025-12-10"]["Forecast Area"] == "Southern Uplands"


def test_get_specific_date_forecast():
    response = client.get("/forecasts/southern-uplands?date=2025-12-10")
    assert response.status_code == 200
    assert response.json()["2025-12-10"]["Forecast Area"] == "Southern Uplands"
    assert list(response.json().keys()) == ["2025-12-10"]


def test_get_nonexistent_region_forecast():
    response = client.get("/forecasts/southern-highlands")
    assert response.status_code == 404


def test_get_nonexistent_date_forecast():
    response = client.get("/forecasts/southern-uplands?date=2066-13-10")
    assert response.status_code == 404
