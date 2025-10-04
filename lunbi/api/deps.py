from __future__ import annotations

import os
from collections.abc import Iterator

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from lunbi.config import API_TOKEN
from lunbi.database import get_session
from lunbi.repositories.prompt_repository import PromptRepository
from lunbi.repositories.source_repository import SourceRepository
from lunbi.services.article_metadata_service import ArticleMetadataService
from lunbi.services.prompt_service import PromptService
from lunbi.services.assistant_service import AssistantService


def require_api_token(x_lunbi_token: str | None = Header(default=None, alias="X-Lunbi-Token")) -> None:
    token = API_TOKEN or os.getenv("LUNBI_API_TOKEN")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API token not configured",
        )
    if not x_lunbi_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API token",
        )
    if x_lunbi_token != token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API token",
        )


def get_db_session() -> Iterator[Session]:
    yield from get_session()


def get_prompt_service(session: Session = Depends(get_db_session)) -> PromptService:
    prompt_repository = PromptRepository(session)
    source_repository = SourceRepository(session)
    return PromptService(
        prompt_repository=prompt_repository,
        assistant_service=AssistantService(),
        source_repository=source_repository,
        metadata_service=ArticleMetadataService(repository=source_repository),
    )
