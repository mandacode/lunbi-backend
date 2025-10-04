from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Iterable

from lunbi.models import Prompt, PromptStatus, Source
from lunbi.repositories.prompt_repository import PromptRepository
from lunbi.repositories.source_repository import SourceRepository
from lunbi.services.article_metadata_service import ArticleMetadata, ArticleMetadataService
from lunbi.services.assistant_service import AssistantService

logger = logging.getLogger("lunbi.prompt_service")


class PromptService:
    """Handles prompt answering and persistence."""

    def __init__(
        self,
        prompt_repository: PromptRepository,
        assistant_service: AssistantService,
        source_repository: SourceRepository | None = None,
        metadata_service: ArticleMetadataService | None = None,
    ) -> None:
        self._prompt_repository = prompt_repository
        self._assistant_service = assistant_service
        self._source_repository = source_repository
        self._metadata_service = metadata_service or ArticleMetadataService()

    def process_prompt(self, query: str) -> dict[str, Any]:
        result = self.answer_prompt(query)
        status_enum = self._normalize_status(result.get("status"))

        source_record, source_payload = self._prepare_source(result.get("sources", []))

        record = Prompt(
            query=query,
            answer=result.get("answer"),
            status=status_enum,
            source_id=source_record.id if source_record else None,
        )
        saved = self._prompt_repository.add(record)

        logger.info("Prompt processed", extra={"prompt_id": saved.id, "status": saved.status.value})
        response: dict[str, Any] = {
            "prompt_id": saved.id,
            "answer": result.get("answer"),
            "status": status_enum.value,
        }
        if source_payload:
            response["source"] = source_payload
        return response

    def stream_prompt(self, query: str) -> Iterable[str]:
        answer_chunks: list[str] = []
        final_event: dict[str, Any] | None = None

        for event in self._assistant_service.stream_response(query):
            if event.get("type") == "chunk":
                chunk = event.get("content", "")
                if not chunk:
                    continue
                answer_chunks.append(chunk)
                yield json.dumps({"type": "chunk", "content": chunk}) + "\n"
            else:
                final_event = event

        if final_event is None:
            final_event = {
                "type": "final",
                "answer": "".join(answer_chunks),
                "sources": [],
                "status": PromptStatus.FAILED,
            }

        answer_text = final_event.get("answer", "".join(answer_chunks))
        raw_sources = final_event.get("sources", [])
        status_enum = self._normalize_status(final_event.get("status", PromptStatus.SUCCESS))

        source_record, source_payload = self._prepare_source(raw_sources)

        record = Prompt(
            query=query,
            answer=answer_text,
            status=status_enum,
            source_id=source_record.id if source_record else None,
        )
        saved = self._prompt_repository.add(record)

        payload: dict[str, Any] = {
            "type": "final",
            "prompt_id": saved.id,
            "answer": answer_text,
            "status": status_enum.value,
        }
        if source_payload:
            payload["source"] = source_payload
        yield json.dumps(payload) + "\n"

    def answer_prompt(self, query: str) -> dict[str, Any]:
        return self._assistant_service.generate_response(query)

    def get_sample_prompts(self) -> list[str]:
        return self._assistant_service.get_scope_hints()

    def _prepare_source(self, sources: list[str] | str | None) -> tuple[Source | None, dict[str, str] | None]:
        if not sources:
            return None, None
        if isinstance(sources, str):
            candidates = [sources]
        else:
            candidates = [item for item in sources if item]
        if not candidates:
            return None, None
        try:
            metadata = self._resolve_metadata(candidates)
        except FileNotFoundError:
            logger.warning("Metadata CSV not found when resolving sources")
            return None, None
        if metadata is None:
            logger.debug("No metadata match for sources", extra={"sources": candidates})
            return None, None
        source_record = None
        if self._source_repository is not None:
            source_record = self._source_repository.upsert(title=metadata.title, url=metadata.url)
        payload = {"title": metadata.title, "url": metadata.url}
        return source_record, payload

    def _resolve_metadata(self, sources: list[str]) -> ArticleMetadata | None:
        for raw in sources:
            path = Path(raw)
            candidates = [path, Path(path.name)]
            for candidate in candidates:
                metadata = self._metadata_service.get_metadata_for_path(candidate)
                if metadata:
                    return metadata
        return None

    @staticmethod
    def _normalize_status(raw_status: str | PromptStatus) -> PromptStatus:
        if isinstance(raw_status, PromptStatus):
            return raw_status
        if isinstance(raw_status, str):
            try:
                return PromptStatus(raw_status)
            except ValueError:
                logger.warning("Unknown status", extra={"status": raw_status})
        return PromptStatus.SUCCESS
