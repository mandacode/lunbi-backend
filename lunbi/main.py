import logging
from logging.config import dictConfig

from fastapi import FastAPI

from .api.routes import prompts
from .database import init_db

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "%(asctime)s %(levelname)s %(name)s - %(message)s"}
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
    "root": {"level": "INFO", "handlers": ["console"]},
}


def configure_logging() -> None:
    dictConfig(LOGGING_CONFIG)


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI()

    app.include_router(prompts.router)

    logger = logging.getLogger("lunbi.api")

    @app.on_event("startup")
    def startup_event() -> None:  # pragma: no cover - framework hook
        logger.info("Initializing database")
        init_db()

    @app.get("/")
    def read_root():
        return {"status": "ok"}

    return app


app = create_app()
