from __future__ import annotations

import logging
from typing import Any, Dict, List

from lunbi.ask_question import SCOPE_HINTS, ask_question
from lunbi.models import Prompt, PromptStatus
from lunbi.repositories.prompt_repository import PromptRepository

logger = logging.getLogger("lunbi.prompt_service")


class PromptService:
    """Business logic layer orchestrating question answering and persistence."""

    def __init__(self, prompt_repository: PromptRepository) -> None:
        self._repository = prompt_repository

    def process_prompt(self, query: str) -> Dict[str, Any]:
        result = ask_question(query)
        status_enum = self._normalize_status(result.get("status"))

        record = Prompt(
            query=query,
            best_answer=result.get("answer"),
            answers=[
                {
                    "answer": result.get("answer"),
                    "sources": result.get("sources", []),
                }
            ],
            status=status_enum,
        )

        saved = self._repository.add(record)
        logger.info("Prompt processed", extra={"prompt_id": saved.id, "status": saved.status.value})
        return {
            "prompt_id": saved.id,
            "answer": result.get("answer"),
            "sources": result.get("sources", []),
            "status": status_enum.value,
        }

    def get_sample_prompts(self) -> List[str]:
        return SCOPE_HINTS

    @staticmethod
    def _normalize_status(raw_status: Any) -> PromptStatus:
        if isinstance(raw_status, PromptStatus):
            return raw_status
        if isinstance(raw_status, str):
            try:
                return PromptStatus(raw_status)
            except ValueError:
                logger.warning("Unknown status", extra={"status": raw_status})
        return PromptStatus.SUCCESS
