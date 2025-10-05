from __future__ import annotations

import logging
from typing import Literal

from langchain_openai import ChatOpenAI

logger = logging.getLogger("lunbi.translation")

SUPPORTED_LANGUAGES = {"en", "pl"}
LANGUAGE_NAMES = {"en": "English", "pl": "Polish"}


class TranslationService:
    """Minimal helper that translates text using ChatOpenAI."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self._model = ChatOpenAI(model=model, temperature=0)

    def translate(
        self,
        text: str,
        target_language: Literal["en", "pl"],
        source_language: Literal["en", "pl"] | None = None,
    ) -> str:
        text = text or ""
        if not text.strip():
            return text
        if target_language not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {target_language}")

        source_language = source_language or ("en" if target_language == "pl" else "pl")
        if source_language == target_language:
            return text

        if source_language not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {source_language}")

        prompt = (
            "Translate the following content from "
            f"{LANGUAGE_NAMES[source_language]} to {LANGUAGE_NAMES[target_language]}. "
            "Preserve technical terminology and keep the tone formal.\n\n"
            f"Content:\n{text}"
        )
        logger.debug(
            "Translating content from %s to %s", LANGUAGE_NAMES[source_language], LANGUAGE_NAMES[target_language]
        )
        response = self._model.invoke(prompt)
        return getattr(response, "content", str(response))
