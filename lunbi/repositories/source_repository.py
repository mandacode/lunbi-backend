from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from lunbi.models import Source


class SourceRepository:
    """Persistence operations for sources."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_url(self, url: str) -> Optional[Source]:
        stmt = select(Source).where(Source.url == url)
        return self._session.execute(stmt).scalar_one_or_none()

    def upsert(self, title: str, url: str) -> Source:
        existing = self.get_by_url(url)
        if existing:
            if existing.title != title:
                existing.title = title
                self._session.flush()
            return existing
        source = Source(title=title, url=url)
        self._session.add(source)
        self._session.flush()
        return source
