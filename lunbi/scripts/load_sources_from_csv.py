"""Load sources from a CSV file."""

import argparse
import csv
import logging
from pathlib import Path

from lunbi.database import session_scope
from lunbi.repositories.source_repository import SourceRepository
from lunbi.services.article_metadata_service import to_snake_case

logger = logging.getLogger("lunbi.load_sources")


def load_sources(csv_path: Path) -> None:
    csv_path = csv_path.expanduser().resolve()
    logger.info("Loading sources", extra={"csv_path": str(csv_path)})

    created = 0
    updated = 0
    skipped = 0

    with csv_path.open(encoding="utf-8-sig", newline="") as handle, session_scope() as session:
        reader = csv.DictReader(handle)
        title_key = None
        url_key = None
        for field in reader.fieldnames or []:
            lowered = field.lower().lstrip("﻿")
            if lowered == "title":
                title_key = field
            elif lowered in {"link", "url"}:
                url_key = field
        if title_key is None or url_key is None:
            raise ValueError("CSV must contain Title and Link columns")

        repository = SourceRepository(session)

        for row in reader:
            title = (row.get(title_key) or "").strip()
            url = (row.get(url_key) or "").strip()
            if not title or not url:
                skipped += 1
                continue

            md_filename = f"{to_snake_case(title)}.md"

            existing = repository.get_by_md_filename(md_filename)
            snapshot = None
            if existing:
                snapshot = (existing.title, existing.url)

            source = repository.upsert(title=title, url=url, md_filename=md_filename)
            if existing is None:
                created += 1
            elif snapshot != (source.title, source.url):
                updated += 1

    logger.info(f"Source import finished -> created: {created}, updated: {updated}, skipped: {skipped}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Load sources into the database")
    parser.add_argument("csv_path", type=Path)
    args = parser.parse_args()
    load_sources(args.csv_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
    main()
