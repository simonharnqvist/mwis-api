import logging

import pika
from sqlmodel import Session

from mwis_api.common.schemas import ForecastMessage
from mwis_api.repository.forecast import ForecastRepository

logger = logging.getLogger(__name__)


class ForecastWorker:
    def __init__(
        self,
        *,
        engine,
        rabbitmq_url: str,
        queue_name: str = "forecast",
    ) -> None:
        self.engine = engine
        self.queue_name = queue_name

        connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))

        self.channel = connection.channel()

        self.channel.queue_declare(
            queue=self.queue_name,
            durable=True,
        )

        self.channel.basic_qos(prefetch_count=1)

    def handle_message(self, ch, method, _properties, body: bytes) -> None:
        try:
            message = ForecastMessage.model_validate_json(body)

            with Session(self.engine) as session:  # this should move to repository
                ForecastRepository(session).insert(message)

            logger.info(
                "Inserted forecast for region=%s",
                message.region,
            )

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception:
            logger.exception("Failed processing forecast message")

            ch.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=False,
            )

    def run(self) -> None:
        logger.info(
            "Listening on queue '%s'",
            self.queue_name,
        )

        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.handle_message,
        )

        self.channel.start_consuming()
