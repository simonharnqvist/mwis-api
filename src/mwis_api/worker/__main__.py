import logging
import os

from sqlmodel import create_engine

from mwis_api.worker.worker import ForecastWorker

logging.basicConfig(level=logging.INFO)


def main() -> None:
    engine = create_engine(os.environ["DATABASE_URL"])

    worker = ForecastWorker(
        engine=engine,
        rabbitmq_url=os.environ["RABBITMQ_URL"],
    )

    worker.run()


if __name__ == "__main__":
    main()
