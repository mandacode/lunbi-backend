from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

from lunbi.models import Prompt, PromptStatus, Source
from lunbi.repositories.prompt_repository import PromptRepository
from lunbi.repositories.source_repository import SourceRepository
from lunbi.services.article_metadata_service import ArticleMetadataService
from lunbi.services.assistant_service import AssistantService
from lunbi.services.translation_service import TranslationService

logger = logging.getLogger("lunbi.prompt_service")


class PromptService:
    """Handles prompt answering and persistence."""

    def __init__(
        self,
        prompt_repository: PromptRepository,
        assistant_service: AssistantService,
        source_repository: SourceRepository | None = None,
        metadata_service: ArticleMetadataService | None = None,
        translation_service: TranslationService | None = None,
    ) -> None:
        if source_repository is None and metadata_service is None:
            raise ValueError("Source repository is required")

        self._prompt_repository = prompt_repository
        self._assistant_service = assistant_service
        self._source_repository = source_repository
        self._metadata_service = metadata_service or ArticleMetadataService(repository=source_repository)  # type: ignore[arg-type]
        self._translation_service = translation_service or TranslationService()

    def _prepare_query(self, query: str, language: str) -> tuple[str, str]:
        if language == "en":
            return query, language
        try:
            translated = self._translation_service.translate(
                query,
                target_language="en",
                source_language=language,  # type: ignore[arg-type]
            )
            logger.info("Translated query from %s to English", language)
            return translated, language
        except Exception:
            logger.exception("Failed to translate query from %s", language)
            return query, "en"

    def process_prompt(self, query: str, language: str) -> dict[str, Any]:
        effective_query, effective_language = self._prepare_query(query, language)

        message_id = f"msg_{uuid4().hex}"
        result = self._assistant_service.generate_response(effective_query, language=effective_language)
        status_enum = self._normalize_status(result.get("status"))
        raw_sources = result.get("sources", [])
        source_record, source_payload = self._prepare_source(raw_sources)
        logger.info("Prompt generation completed for '%s' (status=%s)", query, status_enum.value)
        if source_payload:
            logger.info("Resolved source for '%s' -> %s", query, source_payload.get("title"))

        saved = self._persist_prompt_record(
            query=query,
            answer=result.get("answer"),
            status=status_enum,
            source_record=source_record,
        )

        response: dict[str, Any] = {
            "id": message_id,
            "role": "assistant",
            "prompt_id": saved.id,
            "answer": result.get("answer"),
            "status": status_enum.value,
            "language": effective_language,
        }
        if source_payload:
            response["source"] = source_payload
        return response

    def stream_prompt(self, query: str, language: str) -> Iterable[str]:
        effective_query, effective_language = self._prepare_query(query, language)

        answer_chunks: list[str] = []
        final_event: dict[str, Any] | None = None
        message_id = f"msg_{uuid4().hex}"

        def _sse(data: dict[str, Any]) -> str:
            return json.dumps(data, ensure_ascii=False) + "\n"

        for event in self._assistant_service.stream_response(effective_query, language=effective_language):
            if event.get("type") == "chunk":
                chunk = event.get("content", "")
                if not chunk:
                    continue
                answer_chunks.append(chunk)
                yield _sse(
                    {
                        "id": message_id,
                        "role": "assistant",
                        "content": chunk,
                    }
                )
            else:
                final_event = event

        if final_event is None:
            logger.warning("Stream finished without final event for query '%s'", query)
            final_event = {
                "type": "final",
                "answer": "".join(answer_chunks),
                "sources": [],
                "status": PromptStatus.FAILED,
            }

        answer_text = final_event.get("answer", "".join(answer_chunks))
        raw_sources = final_event.get("sources", [])
        status_enum = self._normalize_status(final_event.get("status", PromptStatus.SUCCESS))

        if not answer_chunks and answer_text:
            yield _sse(
                {
                    "id": message_id,
                    "role": "assistant",
                    "content": answer_text,
                }
            )

        source_record, source_payload = self._prepare_source(raw_sources)
        if source_payload:
            logger.info("Resolved source for streamed prompt '%s' -> %s", query, source_payload.get("title"))

        saved = self._persist_prompt_record(query, answer_text, status_enum, source_record)

        # Client expects only incremental content frames and a final terminator
        yield "data: [DONE]\n\n"

    def answer_prompt(self, query: str, language: str = "en") -> dict[str, Any]:
        return self._assistant_service.generate_response(query, language=language)

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

        for raw in candidates:
            md_filename = Path(raw).name
            if self._source_repository is None:
                break
            record = self._source_repository.get_by_md_filename(md_filename)
            if record:
                logger.info("Source lookup succeeded for %s", md_filename)
                return record, {"title": record.title, "url": record.url}
            logger.debug("Source lookup missed for %s", md_filename)

        metadata = self._metadata_service.get_metadata_for_path(candidates[0])
        if not metadata:
            logger.debug("Unable to resolve source from candidates: %s", candidates)
            return None, None

        logger.info("Metadata resolved for %s", candidates[0])
        record = None
        if self._source_repository is not None:
            record = self._source_repository.upsert(
                title=metadata.title,
                url=metadata.url,
                md_filename=candidates[0],
            )
            logger.info("Source upserted for %s", candidates[0])
        return record, {"title": metadata.title, "url": metadata.url}

    def _persist_prompt_record(
        self,
        query: str,
        answer: str | None,
        status: PromptStatus,
        source_record: Source | None,
    ) -> Prompt:
        record = Prompt(
            query=query,
            answer=answer,
            status=status,
            source_id=source_record.id if isinstance(source_record, Source) else None,
        )
        saved = self._prompt_repository.add(record)
        logger.info("Prompt persisted with id=%s and status=%s", saved.id, saved.status.value)
        return saved
    @staticmethod
    def _normalize_status(raw_status: str | PromptStatus) -> PromptStatus:
        if isinstance(raw_status, PromptStatus):
            return raw_status
        if isinstance(raw_status, str):
            try:
                return PromptStatus(raw_status)
            except ValueError:
                logger.warning("Unknown status value '%s'", raw_status)
        return PromptStatus.SUCCESS
