from dataclasses import dataclass
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Date, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import JSONB
from datetime import date, datetime


@dataclass(frozen=True)
class ForecastMessage:
    version: int
    region: str
    country: str
    scraped_at: str
    forecast: dict[str, dict]


@dataclass(frozen=True)
class Region:
    country: str
    region: str


class Base(DeclarativeBase):
    pass


class Forecast(Base):
    __tablename__ = "forecasts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    version: Mapped[int] = mapped_column(Integer, nullable=False)

    forecast_date: Mapped[date] = mapped_column(Date, nullable=False)
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    country: Mapped[str] = mapped_column(Text, nullable=False)
    region: Mapped[str] = mapped_column(Text, nullable=False)

    forecast: Mapped[dict] = mapped_column(JSONB, nullable=False)
