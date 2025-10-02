from collections.abc import Iterator

from fastapi import Depends
from sqlalchemy.orm import Session

from lunbi.database import get_session
from lunbi.repositories.prompt_repository import PromptRepository
from lunbi.services.prompt_service import PromptService


def get_db_session() -> Iterator[Session]:
    yield from get_session()


def get_prompt_service(session: Session = Depends(get_db_session)) -> PromptService:
    return PromptService(prompt_repository=PromptRepository(session=session))
