import json
import os
import logging
from dataclasses import asdict
import pika
from tenacity import retry, stop_after_attempt, wait_exponential
from .models import ForecastMessage

logger = logging.getLogger(__name__)


class RabbitMQPublisher:
    def __init__(
        self,
        amqp_url: str | None = None,
        queue: str = "forecast_updates",
    ):
        self.queue = queue
        self.amqp_url = amqp_url or os.getenv(
            "RABBITMQ_URL", "amqp://guest:guest@localhost:5672/"
        )
        self._connect()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def _connect(self):
        self.connection = pika.BlockingConnection(pika.URLParameters(self.amqp_url))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue, durable=True)
        self.channel.confirm_delivery()
        logger.info("Connected to RabbitMQ")

    def _ensure_connected(self):
        if self.connection.is_closed or self.channel.is_closed:
            logger.warning("RabbitMQ connection lost, reconnecting...")
            self._connect()

    def publish(self, message: ForecastMessage):
        self._ensure_connected()
        try:
            self.channel.basic_publish(
                exchange="",
                routing_key=self.queue,
                body=json.dumps(asdict(message), default=str),
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent,
                ),
            )
        except (pika.exceptions.UnroutableError, pika.exceptions.NackError) as e:
            raise RuntimeError("RabbitMQ did not confirm message") from e
        logger.info("Published forecast for %s", message.region)

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
