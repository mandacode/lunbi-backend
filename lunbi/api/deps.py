from collections.abc import Iterator

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from lunbi.config import LUNBI_API_TOKEN
from lunbi.database import get_session
from lunbi.repositories.prompt_repository import PromptRepository
from lunbi.services.prompt_service import PromptService
from lunbi.services.assistant_service import AssistantService


def require_api_token(lunbi_token: str | None = Header(default=None, alias="X-Lunbi-Token")) -> None:
    if LUNBI_API_TOKEN is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="API token not configured")
    if not lunbi_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API token")
    if lunbi_token != LUNBI_API_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API token")


def get_db_session() -> Iterator[Session]:
    yield from get_session()


def get_prompt_service(session: Session = Depends(get_db_session)) -> PromptService:
    return PromptService(prompt_repository=PromptRepository(session), assistant_service=AssistantService())
