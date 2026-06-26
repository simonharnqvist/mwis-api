from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Date, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from datetime import date, datetime


class Base(DeclarativeBase):
    pass


class Forecast(Base):
    __tablename__ = "forecasts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    forecast_date: Mapped[date] = mapped_column(Date, nullable=False)
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    country: Mapped[str] = mapped_column(Text, nullable=False)
    region: Mapped[str] = mapped_column(Text, nullable=False)

    forecast: Mapped[dict] = mapped_column(JSONB, nullable=False)
