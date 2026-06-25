import pika
import pytest

from testcontainers.rabbitmq import RabbitMqContainer


@pytest.fixture(scope="session")
def rabbitmq():
    with RabbitMqContainer("rabbitmq:3.13-management") as container:
        params = container.get_connection_params()

        yield params
