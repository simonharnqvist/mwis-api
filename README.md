# mwis-api

Unofficial and unsanctioned REST API for the Mountain Weather Information Service website. This application scrapes the MWIS website at regular intervals (60 mins by default), formats the scraped HTML to JSON, and saves it in a relational database (currently in-memory DuckDB). FastAPI then serves a simple API that allows programmatic querying of the forecasts.

In scope/requirements:
* Web scraper for WMIS
* API
* Alembic schema management
* Monitoring/observability
* CI/CD
* Docker image
* AWS ECS/Fargate deployment

Not in scope:
* GUI (MWIS provides this)
