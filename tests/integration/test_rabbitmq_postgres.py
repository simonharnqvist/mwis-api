import json
import pika
import pytest
from sqlalchemy import create_engine, text

from testcontainers.rabbitmq import RabbitMqContainer
from testcontainers.postgres import PostgresContainer

from mwis_api.db.worker import ForecastWorker


@pytest.fixture(scope="session")
def rabbitmq():
    with RabbitMqContainer("rabbitmq:3.13-management") as c:
        yield c.get_connection_params()


@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:16") as p:
        yield p.get_connection_url()


def test_rabbit_to_postgres(rabbitmq, postgres):
    worker = ForecastWorker(rabbitmq, postgres)

    publisher = pika.BlockingConnection(rabbitmq)
    channel = publisher.channel()
    channel.queue_declare(queue="forecast", durable=True)

    message = {
        "version": 1,
        "region": "Cairngorms",
        "country": "scottish",
        "scraped_at": "2026-06-25T12:00:00Z",
        "forecast": {"2026-06-25": {"Weather": "Sunny"}},
    }

    channel.basic_publish(
        exchange="",
        routing_key="forecast",
        body=json.dumps(message),
    )

    # process one message manually (for test control)
    method, props, body = channel.basic_get("forecast", auto_ack=True)
    assert method is not None

    worker.handle_message(channel, method, props, body)

    engine = create_engine(postgres)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT region FROM forecasts")).fetchall()

    assert result[0][0] == "Cairngorms"
