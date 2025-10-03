# Repository Guidelines

## Project Structure & Module Organization
Application code lives in `lunbi/`. Entry point `lunbi/main.py` wires the FastAPI app and logging. HTTP surface area is under `lunbi/api/routes/`, with dependencies in `lunbi/api/deps.py` and shared schemas in `lunbi/api/schemas.py`. Database setup sits in `lunbi/database.py` and `lunbi/config.py`, while domain logic is split across `lunbi/services/` and persistence code in `lunbi/repositories/`. Automation scripts (data ingestion, indexing) are in `lunbi/scripts/`. Runtime assets such as Chroma indexes live in `chroma/`; sample data is under `data/`. Keep new tests in a dedicated `tests/` tree that mirrors the package layout.

## Build, Test, and Development Commands
Set up dependencies with `python -m venv .venv && source .venv/bin/activate` followed by `pip install -r requirements.txt`. Run the API locally via `uvicorn lunbi.main:app --reload`. Start the full stack, including PostgreSQL, with `docker-compose up --build`. Apply migrations using `alembic upgrade head`. Execute test suites using `pytest -q`; add `-k <pattern>` for focused runs.

## Coding Style & Naming Conventions
Use 4-space indentation and type hints with builtin containers (`list`, `dict`, `tuple`). Group imports by origin: standard library modules first, third-party (if needed), then absolute imports from `lunbi.*`. Service and repository names follow `EntityService` and `EntityRepository`; files use snake_case (`prompt_repository.py`). Prefer small, pure functions, and add brief comments only when intent would otherwise be unclear.

## Testing Guidelines
Write tests with pytest. Place unit tests alongside mirrored packages (`tests/services/`, `tests/api/`) and name files `test_<feature>.py`. Use descriptive test function names that read as behavior statements. When introducing new data access logic, add integration coverage that exercises SQLAlchemy sessions via temporary databases or docker-compose. Aim to keep pytest output clean; respond to any warnings before merging.

## Commit & Pull Request Guidelines
Commits should be concise and imperative (e.g., `Add prompt ingestion pipeline`). Group related changes together and avoid mixing refactors with feature work. PRs must include a summary, testing notes (`pytest`, `uvicorn` smoke runs), and links to any tracking issues. Request review from owners of touched modules and ensure CI (when available) is green before merging.

## Security & Configuration Tips
Load secrets via environment variables; never commit `.env` or credentials. Review `lunbi/config.py` before changing model or database defaults. If you modify external service access, document new env vars and update docker-compose accordingly.

## EXTRA TIPS

- Use builtin collection types for typing, e.g. `list` or `dict`. Not Optional -> use str | None (pipe)
- In imports:
  - builtin modules first: import full module: e.g. `import os`, `import datetime`, `import dataclasses`
  - then local modules: import an absolute path: e.g. `from lunbi.utils import ...`

- in dependency injection functions, use full name of services and repositories when injecting them. build them like: 
```

def get_prompt_service(session: Session = Depends(get_db_session)) -> PromptService:
    return PromptService(prompt_repository=PromptRepository(session), assistant_service=AssistantService())

```

Follow sturcture:
project_root/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration management
│   ├── dependencies.py      # Shared dependencies
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── users.py
│   │   │   │   ├── items.py
│   │   │   │   └── auth.py
│   │   │   └── router.py    # Aggregates all v1 endpoints
│   │   └── deps.py          # API-specific dependencies
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py      # Auth, hashing, JWT
│   │   └── config.py        # Core settings
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # SQLAlchemy models
│   │   └── item.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user_schema.py             # Pydantic schemas
│   │   └── item_schema.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py                     # Base CRUD operations
│   │   ├── user_repository.py          # User-specific CRUD
│   │   └── item_repository.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py          # Import all models for Alembic
│   │   └── session.py       # Database session management
│   │
│   └── services/
│       ├── __init__.py
│       ├── user_service.py
│       └── email_service.py         # Business logic services
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   └── test_services/
│
├── alembic/                 # Database migrations
│   ├── versions/
│   └── env.py
│
├── .env.example
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── README.md
└── alembic.ini

- When you name things, use snake_case. When it's entity related, it should be EntityService, EntityRepository, EntitySchema. Or filename: entity_repository.py

- use poetry to manage dependencies
- use docker and docker compose 
- use pytest
- use fastapi
- use sqlalchemy
- use pydantic
- use uvicorn
- use alembic
- use docker
- use github actions
