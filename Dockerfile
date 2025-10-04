FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ARG UID=1000
ARG GID=1000

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid ${GID:-1000} lunbi || true \n    && useradd --uid ${UID:-1000} --gid ${GID:-1000} --create-home --home-dir /home/lunbi --shell /bin/bash lunbi

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY docker-entrypoint.sh ./docker-entrypoint.sh
COPY lunbi ./lunbi
COPY data ./data

RUN mkdir -p chroma
RUN chmod +x docker-entrypoint.sh
RUN chown -R lunbi:lunbi /app

EXPOSE 8808

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["uvicorn", "lunbi.main:app", "--host", "0.0.0.0", "--port", "8808", "--reload"]
