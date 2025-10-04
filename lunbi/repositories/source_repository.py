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

    def get_by_md_filename(self, md_filename: str) -> Optional[Source]:
        stmt = select(Source).where(Source.md_filename == md_filename)
        return self._session.execute(stmt).scalar_one_or_none()

    def upsert(self, title: str, url: str, md_filename: str) -> Source:
        source = self.get_by_md_filename(md_filename)
        if source is None:
            source = self.get_by_url(url)
        if source:
            updated = False
            if source.title != title:
                source.title = title
                updated = True
            if source.url != url:
                source.url = url
                updated = True
            if source.md_filename != md_filename:
                source.md_filename = md_filename
                updated = True
            if updated:
                self._session.flush()
            return source

        source = Source(title=title, url=url, md_filename=md_filename)
        self._session.add(source)
        self._session.flush()
        return source
