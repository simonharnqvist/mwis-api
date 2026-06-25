import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_QUEUE = os.getenv(
    "RABBITMQ_QUEUE",
    "forecast_updates",
)

MWIS_URL = "https://www.mwis.org.uk/"
