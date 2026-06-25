from mwis_api.common.models import ForecastMessage
from mwis_api.scraper.publisher import RabbitMQPublisher
import json
import pika


def test_publish(rabbitmq):
    publisher = RabbitMQPublisher(connection_params=rabbitmq, queue="testing")

    consumer = pika.BlockingConnection(rabbitmq)
    channel = consumer.channel()

    channel.queue_declare(queue="testing", durable=True)

    forecast = ForecastMessage(
        version=1,
        region="Cairngorms",
        country="scottish",
        scraped_at="2026-06-25T12:00:00Z",
        forecast={
            "2026-06-25": {
                "Weather": "Sunny",
            }
        },
    )

    publisher.publish(forecast)

    method, properties, body = channel.basic_get(queue="testing", auto_ack=True)

    assert method is not None

    message = json.loads(body)

    assert message["region"] == "Cairngorms"
    assert message["country"] == "scottish"

    consumer.close()
    publisher.close()
