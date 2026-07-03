import json
import logging
from dataclasses import asdict

import pika
from tenacity import retry, stop_after_attempt, wait_exponential

from mwis_api.common.models import ForecastMessage

logger = logging.getLogger(__name__)


class RabbitMQPublisher:
    def __init__(
        self,
        connection_params: pika.ConnectionParameters,
        queue: str = "forecast",
    ):
        self._connection_params = connection_params
        self._queue = queue

        self._connection = None
        self._channel = None

        self._connect()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def _connect(self):

        logger.info(
            "RabbitMQ host=%s port=%s",
            self._connection_params.host,
            self._connection_params.port,
        )

        try:
            self._connection = pika.BlockingConnection(self._connection_params)
            self._channel = self._connection.channel()

            self._channel.queue_declare(
                queue=self._queue,
                durable=True,
            )

            self._channel.confirm_delivery()

            logger.info("Connected to RabbitMQ")

        except Exception as e:
            raise RuntimeError(
                f"❌ Failed to connect to RabbitMQ service at {self._connection_params}. Error: {e}"
            )

    def _ensure_connected(self):
        if (
            self._connection is None
            or self._connection.is_closed
            or self._channel is None
            or self._channel.is_closed
        ):
            logger.warning("RabbitMQ connection lost, reconnecting...")
            self._connect()

    def publish(self, message: ForecastMessage):
        self._ensure_connected()

        try:
            self._channel.basic_publish(
                exchange="",
                routing_key=self._queue,
                body=json.dumps(asdict(message), default=str),
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent,
                ),
                mandatory=True,
            )
        except (
            pika.exceptions.UnroutableError,
            pika.exceptions.NackError,
        ) as e:
            raise RuntimeError("RabbitMQ did not confirm message") from e

        logger.info("Published forecast for %s", message.region)

    def close(self):
        if self._connection and self._connection.is_open:
            self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
