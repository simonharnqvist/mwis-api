import os
import pika

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", 5672)
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
RABBITMQ_QUEUE = os.getenv(
    "RABBITMQ_QUEUE",
    "forecast_updates",
)

RABBITMQ_PARAMS = pika.ConnectionParameters(
    host=RABBITMQ_HOST,
    port=RABBITMQ_PORT,
    credentials=pika.PlainCredentials(
        username=RABBITMQ_USER, password=RABBITMQ_PASSWORD
    ),
)

MWIS_URL = "https://www.mwis.org.uk/forecasts"
