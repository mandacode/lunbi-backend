import logging
from logging.config import dictConfig

from fastapi import FastAPI
from pydantic import BaseModel

from ask_question import ask_question


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


@app.get("/")
def read_root():
    return {"status": "ok"}


@app.post("/prompt")
def prompt_model(payload: PromptRequest):
    logger.info("Received prompt", extra={"query": payload.query})
    result = ask_question(payload.query)

    if not result.get("sources"):
        logger.warning("Responding without sources", extra={"query": payload.query})
    else:
        logger.info("Returning answer", extra={"sources": result.get("sources", [])})

    return result
