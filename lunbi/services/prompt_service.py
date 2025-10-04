from __future__ import annotations

import json
import logging
from typing import Any, Iterable

from lunbi.models import Prompt, PromptStatus
from lunbi.repositories.prompt_repository import PromptRepository
from lunbi.services.assistant_service import AssistantService

logger = logging.getLogger("lunbi.prompt_service")


class PromptService:
    """Handles prompt answering and persistence."""

    def __init__(self, prompt_repository: PromptRepository, assistant_service: AssistantService) -> None:
        self._prompt_repository = prompt_repository
        self._assistant_service = assistant_service

    def process_prompt(self, query: str) -> dict[str, Any]:
        result = self.answer_prompt(query)
        status_enum = self._normalize_status(result.get("status"))

        record = Prompt(
            query=query,
            answer=result.get("answer"),
            status=status_enum,
        )
        saved = self._prompt_repository.add(record)

        logger.info("Prompt processed", extra={"prompt_id": saved.id, "status": saved.status.value})
        return {
            "prompt_id": saved.id,
            "answer": result.get("answer"),
            "sources": result.get("sources", []),
            "status": status_enum.value,
        }

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
        sources = final_event.get("sources", [])
        status_enum = self._normalize_status(final_event.get("status", PromptStatus.SUCCESS))

        record = Prompt(query=query, answer=answer_text, status=status_enum)
        saved = self._prompt_repository.add(record)

        payload = {
            "type": "final",
            "prompt_id": saved.id,
            "answer": answer_text,
            "sources": sources,
            "status": status_enum.value,
        }
        yield json.dumps(payload) + "\n"

    def answer_prompt(self, query: str) -> dict[str, Any]:
        return self._assistant_service.generate_response(query)

    def get_sample_prompts(self) -> list[str]:
        return self._assistant_service.get_scope_hints()

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
