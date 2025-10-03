# Lunbi Backend

A FastAPI backend that powers Lunbi's knowledge services. It ingests research data, indexes it with ChromaDB, and exposes conversational and retrieval APIs backed by OpenAI models.

## Overview
- **FastAPI application** wired through `lunbi/main.py`, with modular routes, services, and repositories.
- **Vector search** using ChromaDB and OpenAI embeddings for semantic document retrieval.
- **PostgreSQL persistence** managed via SQLAlchemy and Alembic migrations.
- **Automation scripts** for data ingestion, index management, and S3-based artifact syncing.

## Getting Started

### Local Environment
1. Create a virtualenv and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Configure environment variables in `.env` (see `.env.example`):
   - Database connection (`POSTGRES_*`)
   - OpenAI credentials (`OPENAI_API_KEY`)
   - AWS credentials for artifact downloads (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
3. Run the API:
   ```bash
   uvicorn lunbi.main:app --reload
   ```

### Docker Compose
1. Build and start the stack:
   ```bash
   docker compose up --build
   ```
2. The app container entrypoint will:
   - Download the latest Chroma index from `s3://lunbi/chroma.zip` if `chroma/chroma.sqlite3` is missing
   - Apply Alembic migrations
   - Launch Uvicorn on port `8808`

## Project Layout
```
lunbi/
  api/            # FastAPI routers, dependencies, schemas
  config.py       # Application configuration and paths
  repositories/   # Database access layer
  services/       # Domain logic
  scripts/        # Automation helpers (S3 download, indexing, ingestion)
alembic/          # Database migrations
data/             # Local data assets
chroma/           # ChromaDB index (synced from S3)
```

## Key Scripts
- `python -m lunbi.scripts.download_s3_file`
  - Ensures the Chroma index is present locally by fetching `chroma.zip` from S3 and extracting it.
- `python -m lunbi.scripts.create_index_db`
  - Rebuilds the Chroma index from local data sources.
- `python -m lunbi.scripts.download_sb_publications`
  - Downloads Space Biology publications, converts them to Markdown, and stores them under `data/articles`.

## Tests
Run the unit test suite with:
```bash
pytest -q
```

## Deployment Notes
- Use Alembic to manage schema changes: `alembic upgrade head`
- Keep secrets out of version control; rely on environment variables for configuration.
- The Docker image is based on `python:3.11-slim` and installs build tooling for `psycopg2`.

## Contributing
1. Follow the repository coding standards (type hints, import ordering, snake_case filenames).
2. Add or update tests alongside code changes.
3. Run `pytest` and relevant smoke checks before opening a pull request.
