import pytest

from fastapi.testclient import TestClient
from sqlmodel import Session

from testcontainers.postgres import PostgresContainer

from mwis_api.api.api import app, get_db_session
from mwis_api.db.models import Forecast
from mwis_api.db.db import Database


@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:16") as p:
        yield p.get_connection_url()


@pytest.fixture
def client(postgres):
    db = Database(postgres)
    db.create_tables()

    def override_db():
        with Session(db.engine) as session:
            yield session

    app.dependency_overrides[get_db_session] = override_db

    yield TestClient(app)

    app.dependency_overrides.clear()


def test_get_forecast(client, postgres):
    db = Database(postgres)

    with Session(db.engine) as session:
        session.add(
            Forecast(
                forecast_date="2026-06-25",
                scraped_at="2026-06-25T12:00:00Z",
                country="Scottish",
                region="Cairngorms",
                forecast={
                    "Weather": "Sunny",
                    "Wind": "Light",
                },
            )
        )
        session.commit()

    response = client.get("/forecasts/Cairngorms")

    assert response.status_code == 200
    assert response.json()["Weather"] == "Sunny"


def test_region_not_found(client):
    response = client.get("/forecasts/Nowhere")

    assert response.status_code == 404


def test_get_forecast_for_date(client):
    response = client.get(
        "/forecasts/Cairngorms",
        params={"forecast_date": "2026-06-25"},
    )

    assert response.status_code == 200
