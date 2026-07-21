import pytest

from fastapi.testclient import TestClient
from sqlmodel import Session

from testcontainers.postgres import PostgresContainer

from mwis_api.api.api import app, get_forecast_repository
from mwis_api.common.models import ForecastMessage


@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:16") as p:
        yield p.get_connection_url()


@pytest.fixture
def repository(postgres):
    repo = ForecastRepository(postgres)
    repo.create_tables()
    return repo


@pytest.fixture
def client(repository):
    def override_repository():
        return repository

    app.dependency_overrides[get_forecast_repository] = override_repository

    yield TestClient(app)

    app.dependency_overrides.clear()


def test_get_forecast(client, repository):
    repository.insert(
        ForecastMessage(
            version="1",
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
