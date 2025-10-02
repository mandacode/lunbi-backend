import logging
from logging.config import dictConfig

from fastapi import FastAPI
from pydantic import BaseModel

from .ask_question import SCOPE_HINTS, ask_question
from .database import get_session, init_db
from .models import Prompt, PromptStatus


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s %(name)s - %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    },
    "loggers": {
        "lunbi": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("lunbi.api")

app = FastAPI()


class PromptRequest(BaseModel):
    query: str


@app.on_event("startup")
def startup_event() -> None:
    logger.info("Initializing database")
    init_db()


@app.get("/")
def read_root():
    return {"status": "ok"}


@app.post("/prompt")
def prompt_model(payload: PromptRequest):
    logger.info("Received prompt", extra={"query": payload.query})
    result = ask_question(payload.query)

    prompt_id = persist_prompt(payload.query, result)

    if not result.get("sources"):
        logger.warning("Responding without sources", extra={"query": payload.query})
    else:
        logger.info("Returning answer", extra={"sources": result.get("sources", [])})
    response_payload = {
        "answer": result.get("answer"),
        "sources": result.get("sources", []),
        "status": _status_to_value(result.get("status")),
    }
    if prompt_id is not None:
        response_payload["prompt_id"] = prompt_id
    return response_payload


@app.get("/sample-prompts")
def sample_prompts():
    logger.info("Serving sample prompts")
    return {"prompts": SCOPE_HINTS}


def _status_to_value(status):
    if isinstance(status, PromptStatus):
        return status.value
    if isinstance(status, str):
        return status
    return PromptStatus.SUCCESS.value


def persist_prompt(query: str, result: dict) -> int | None:
    status = result.get("status", PromptStatus.SUCCESS)
    if isinstance(status, str):
        try:
            status_enum = PromptStatus(status)
        except ValueError:
            status_enum = PromptStatus.SUCCESS
    else:
        status_enum = status

    record = Prompt(
        query=query,
        best_answer=result.get("answer"),
        answers=[
            {
                "answer": result.get("answer"),
                "sources": result.get("sources", []),
            }
        ],
        status=status_enum,
    )

    try:
        with get_session() as session:
            session.add(record)
            session.flush()
            logger.info("Prompt persisted", extra={"prompt_id": record.id, "status": record.status.value})
            return record.id
    except Exception:
        logger.exception("Failed to persist prompt", extra={"query": query})
        return None
