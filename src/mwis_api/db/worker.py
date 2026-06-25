import json
import pika
import logging

from mwis_api.db.repository import ForecastRepository
from mwis_api.db.db import Database

logger = logging.getLogger(__name__)


class ForecastWorker:
    def __init__(self, rabbitmq_params, db_url: str, queue="forecast"):
        self.queue = queue

        self.db = Database(db_url)
        self.db.create_tables()

        self.repo = ForecastRepository(self.db.Session)

        self.connection = pika.BlockingConnection(rabbitmq_params)
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=queue, durable=True)

    def handle_message(self, ch, method, properties, body):
        try:
            message = json.loads(body)

            self.repo.insert(message)

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception:
            logger.exception("Failed processing message")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def run(self):
        self.channel.basic_consume(
            queue=self.queue,
            on_message_callback=self.handle_message,
        )

        self.channel.start_consuming()
