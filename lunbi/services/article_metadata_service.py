from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from lunbi.repositories.source_repository import SourceRepository


@dataclass(frozen=True)
class ArticleMetadata:
    title: str
    url: str
    path: Path


class ArticleMetadataService:
    """Maps markdown filenames to article titles and URLs using the database."""

    def __init__(self, repository: SourceRepository) -> None:
        self._repository = repository
        self._cache: dict[str, ArticleMetadata] = {}

    def refresh(self) -> None:
        self._cache = self._load_mapping()

    def get_metadata_for_path(self, path: Path | str) -> ArticleMetadata | None:
        if not self._cache:
            self.refresh()
        filename = Path(path).name
        return self._cache.get(filename)

    def get_all_metadata(self) -> Iterable[ArticleMetadata]:
        if not self._cache:
            self.refresh()
        return self._cache.values()

    def _load_mapping(self) -> dict[str, ArticleMetadata]:
        mapping: dict[str, ArticleMetadata] = {}
        for source in self._repository.list_all():
            mapping[source.md_filename] = ArticleMetadata(
                title=source.title,
                url=source.url,
                path=Path(source.md_filename),
            )
        return mapping


def to_snake_case(text: str) -> str:
    normalized = text.strip().lower()
    slug = "".join(char if char.isalnum() else "_" for char in normalized)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_")


__all__ = ["ArticleMetadata", "ArticleMetadataService", "to_snake_case"]
