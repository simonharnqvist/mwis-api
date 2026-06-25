# mwis_api/consumer/models.py

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Date, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB


class Base(DeclarativeBase):
    pass


class Forecast(Base):
    __tablename__ = "forecasts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    forecast_date: Mapped[str] = mapped_column(Date, nullable=False)
    scraped_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)

    country: Mapped[str] = mapped_column(Text, nullable=False)
    region: Mapped[str] = mapped_column(Text, nullable=False)

    forecast: Mapped[dict] = mapped_column(JSONB, nullable=False)
