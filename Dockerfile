FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY mwis_api ./mwis_api
COPY regions.csv ./mwis_api/

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    sqlmodel \
    psycopg2-binary \
    beautifulsoup4 \
    requests \
    pandas

EXPOSE 8000

CMD ["uvicorn", "mwis_api.api:app", "--host", "0.0.0.0", "--port", "8000"]
