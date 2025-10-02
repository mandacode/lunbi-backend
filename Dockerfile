FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system lunbi && useradd --system --gid lunbi --create-home --home-dir /home/lunbi lunbi

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY lunbi ./lunbi
COPY data ./data
COPY chroma ./chroma

RUN chown -R lunbi:lunbi /app

USER lunbi

EXPOSE 8808

CMD ["uvicorn", "lunbi.main:app", "--host", "0.0.0.0", "--port", "8808", "--reload"]
