import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from lunbi.config import DATA_PATH, PROJECT_ROOT

CSV_FILENAME = "SB_publication_PMC.csv"
CSV_PATH = PROJECT_ROOT / "data" / CSV_FILENAME
INDEX_EXTENSION = ".md"


def to_snake_case(text: str) -> str:
    normalized = text.strip().lower()
    slug = "".join(char if char.isalnum() else "_" for char in normalized)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_")


@dataclass(frozen=True)
class ArticleMetadata:
    title: str
    url: str
    path: Path


class ArticleMetadataService:
    """Maps markdown filenames to article titles and URLs."""

    def __init__(self, csv_path: Path | None = None, articles_dir: Path | None = None) -> None:
        self.csv_path = csv_path or CSV_PATH
        self.articles_dir = articles_dir or DATA_PATH
        self._cache: dict[str, ArticleMetadata] = {}

    def refresh(self) -> None:
        self._cache = self._load_mapping()

    def get_metadata_for_path(self, path: Path | str) -> ArticleMetadata | None:
        if not self._cache:
            self.refresh()
        target = Path(path)
        return self._cache.get(target.name)

    def get_all_metadata(self) -> Iterable[ArticleMetadata]:
        if not self._cache:
            self.refresh()
        return self._cache.values()

    def _load_mapping(self) -> dict[str, ArticleMetadata]:
        mapping: dict[str, ArticleMetadata] = {}
        with self.csv_path.open(encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                title = (row.get("Title") or row.get("title") or "").strip()
                url = (row.get("Link") or row.get("link") or "").strip()
                if not title or not url:
                    continue
                filename = f"{to_snake_case(title)}{INDEX_EXTENSION}"
                path = self.articles_dir / filename
                mapping[filename] = ArticleMetadata(title=title, url=url, path=path)
        return mapping


__all__ = ["ArticleMetadata", "ArticleMetadataService"]
