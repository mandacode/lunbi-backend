from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from lunbi.models import Prompt


class PromptRepository:

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, prompt: Prompt) -> Prompt:
        self._session.add(prompt)
        self._session.flush()
        return prompt

    def list_latest(self, limit: int = 20) -> Sequence[Prompt]:
        stmt = (
            select(Prompt)
            .order_by(Prompt.created_at.desc())
            .limit(limit)
        )
        return self._session.execute(stmt).scalars().all()
