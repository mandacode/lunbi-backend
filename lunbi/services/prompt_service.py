from __future__ import annotations

import json
import logging
from pathlib import Path
from time import perf_counter
from typing import Any, Iterable

from lunbi.models import Prompt, PromptStatus, Source
from lunbi.repositories.prompt_repository import PromptRepository
from lunbi.repositories.source_repository import SourceRepository
from lunbi.services.article_metadata_service import ArticleMetadataService
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
        if metadata_service is not None:
            self._metadata_service = metadata_service
        else:
            if source_repository is None:
                raise ValueError("Source repository is required when metadata_service is not provided")
            self._metadata_service = ArticleMetadataService(repository=source_repository)

    def process_prompt(self, query: str) -> dict[str, Any]:
        overall_start = perf_counter()

        generation_start = perf_counter()
        result = self.answer_prompt(query)
        generation_elapsed = perf_counter() - generation_start
        status_enum = self._normalize_status(result.get("status"))
        logger.info(
            "Prompt generation completed",
            extra={"query": query, "duration_s": round(generation_elapsed, 3)},
        )

        metadata_start = perf_counter()
        source_record, source_payload = self._prepare_source(result.get("sources", []))
        metadata_elapsed = perf_counter() - metadata_start
        logger.info(
            "Source preparation finished",
            extra={
                "query": query,
                "duration_s": round(metadata_elapsed, 3),
                "resolved": bool(source_payload),
            },
        )

        persistence_start = perf_counter()
        record = Prompt(
            query=query,
            answer=result.get("answer"),
            status=status_enum,
            source_id=source_record.id if isinstance(source_record, Source) else None,
        )
        saved = self._prompt_repository.add(record)
        persistence_elapsed = perf_counter() - persistence_start
        logger.info(
            "Prompt persisted",
            extra={
                "prompt_id": saved.id,
                "status": saved.status.value,
                "duration_s": round(persistence_elapsed, 3),
            },
        )

        total_elapsed = perf_counter() - overall_start
        logger.info(
            "Prompt processed",
            extra={"prompt_id": saved.id, "duration_s": round(total_elapsed, 3)},
        )

        response: dict[str, Any] = {
            "prompt_id": saved.id,
            "answer": result.get("answer"),
            "status": status_enum.value,
        }
        if source_payload:
            response["source"] = source_payload
        return response

    def stream_prompt(self, query: str) -> Iterable[str]:
        overall_start = perf_counter()

        answer_chunks: list[str] = []
        final_event: dict[str, Any] | None = None

        stream_start = perf_counter()
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
            logger.warning("Stream finished without final event", extra={"query": query})
            final_event = {
                "type": "final",
                "answer": "".join(answer_chunks),
                "sources": [],
                "status": PromptStatus.FAILED,
            }

        stream_elapsed = perf_counter() - stream_start
        logger.info(
            "Stream consumption completed",
            extra={"query": query, "duration_s": round(stream_elapsed, 3)},
        )

        answer_text = final_event.get("answer", "".join(answer_chunks))
        raw_sources = final_event.get("sources", [])
        status_enum = self._normalize_status(final_event.get("status", PromptStatus.SUCCESS))

        metadata_start = perf_counter()
        source_record, source_payload = self._prepare_source(raw_sources)
        metadata_elapsed = perf_counter() - metadata_start
        logger.info(
            "Stream source preparation finished",
            extra={
                "query": query,
                "duration_s": round(metadata_elapsed, 3),
                "resolved": bool(source_payload),
            },
        )

        persistence_start = perf_counter()
        record = Prompt(
            query=query,
            answer=answer_text,
            status=status_enum,
            source_id=source_record.id if isinstance(source_record, Source) else None,
        )
        saved = self._prompt_repository.add(record)
        persistence_elapsed = perf_counter() - persistence_start
        logger.info(
            "Stream prompt persisted",
            extra={"prompt_id": saved.id, "duration_s": round(persistence_elapsed, 3)},
        )

        total_elapsed = perf_counter() - overall_start
        logger.info(
            "Stream prompt completed",
            extra={"prompt_id": saved.id, "duration_s": round(total_elapsed, 3)},
        )

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

        # Try repository lookup first for each candidate
        for raw in candidates:
            md_filename = Path(raw).name
            if self._source_repository is None:
                break
            lookup_start = perf_counter()
            record = self._source_repository.get_by_md_filename(md_filename)
            lookup_elapsed = perf_counter() - lookup_start
            if record:
                logger.info(
                    "Source lookup succeeded",
                    extra={"md_filename": md_filename, "duration_s": round(lookup_elapsed, 3)},
                )
                return record, {"title": record.title, "url": record.url}
            logger.debug(
                "Source lookup missed",
                extra={"md_filename": md_filename, "duration_s": round(lookup_elapsed, 3)},
            )

        # Fallback to metadata cache
        fallback_start = perf_counter()
        metadata = self._metadata_service.get_metadata_for_path(candidates[0])
        fallback_elapsed = perf_counter() - fallback_start
        if not metadata:
            logger.debug(
                "Unable to resolve source",
                extra={"candidates": candidates, "duration_s": round(fallback_elapsed, 3)},
            )
            return None, None

        logger.info(
            "Metadata resolved",
            extra={"md_filename": candidates[0], "duration_s": round(fallback_elapsed, 3)},
        )
        record = None
        if self._source_repository is not None:
            repo_start = perf_counter()
            record = self._source_repository.upsert(
                title=metadata.title,
                url=metadata.url,
                md_filename=candidates[0],
            )
            repo_elapsed = perf_counter() - repo_start
            logger.info(
                "Source upserted",
                extra={"md_filename": candidates[0], "duration_s": round(repo_elapsed, 3)},
            )
        return record, {"title": metadata.title, "url": metadata.url}

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
