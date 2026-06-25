from dataclasses import dataclass


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
