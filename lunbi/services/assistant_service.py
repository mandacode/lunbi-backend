from __future__ import annotations

import logging
from typing import Any, Dict

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from lunbi.config import CHROMA_PATH
from lunbi.models import PromptStatus

load_dotenv()

logger = logging.getLogger("lunbi.assistant")

PROMPT_TEMPLATE = """
You are Lunbi, a cheerful AI assistant inspired by Mooncake from the series Final Space.
Speak English in a warm, friendly tone and treat the user like a teammate.
Only rely on the context below, which covers NASA and Space Biology topics.
If the context lacks the needed details or the question falls outside Space Biology, politely explain that you can only help with Space Biology and invite the user to ask another question from that field.
Never invent or speculate beyond the given context.

Context:
{context}

User question: {question}

Answer (in English, in Lunbi's style):
"""

SCOPE_HINTS = [
    "How does microgravity affect the human cardiovascular system?",
    "What changes occur in astronaut bone density during long missions?",
    "Explain plant root growth in reduced gravity environments.",
    "How do circadian rhythms shift aboard the International Space Station?",
    "Describe immune system adaptations to spaceflight.",
    "What are the impacts of space radiation on cellular DNA?",
    "How do astronauts maintain muscle mass in orbit?",
    "Explain fluid redistribution in microgravity.",
    "What nutrition strategies support astronaut health?",
    "How is microbiome balance studied during missions?",
    "Describe vestibular system responses to microgravity.",
    "What countermeasures help prevent space anemia?",
    "How does prolonged spaceflight influence vision?",
    "Explain cardiovascular deconditioning in microgravity.",
    "What experiments explore plant photosynthesis in space?",
    "How do stress hormones change during missions?",
    "What rehabilitation is required after returning to Earth?",
    "Describe the effects of partial gravity on bone remodeling.",
    "How are organoids used for space biology research?",
    "What are current NASA priorities in space biology?",
]
FRIENDLY_RESPONSE = (
    "Loo-loo! That question doesn't seem to orbit NASA or Space Biology. "
    "Could you ask me something from the space biology mission log instead?"
)


class AssistantService:
    """Handles retrieval-augmented generation for Lunbi persona."""

    def __init__(self) -> None:
        self._embedding_function = OpenAIEmbeddings(model="text-embedding-3-small")
        self._model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, streaming=False)

    def generate_response(self, query: str) -> dict[str, Any]:
        logger.info("Assistant generating response", extra={"query": query})

        db = Chroma(persist_directory=str(CHROMA_PATH), embedding_function=self._embedding_function)
        results = db.similarity_search_with_relevance_scores(query, k=3)

        query_lower = query.lower()
        wants_examples = any(keyword in query_lower for keyword in ["example", "prompt", "topic"])

        if len(results) == 0 or results[0][1] < 0.5:
            if wants_examples:
                logger.info("Providing example prompts", extra={"query": query})
                examples = "\n".join(f"- {item}" for item in SCOPE_HINTS)
                friendly_examples = (
                    "Loo-loo! Here are some mission-ready questions you can ask me:\n"
                    f"{examples}"
                )
                return {"answer": friendly_examples, "sources": [], "status": PromptStatus.SUCCESS}

            logger.warning("No relevant documents", extra={"query": query})

            return {"answer": FRIENDLY_RESPONSE, "sources": [], "status": PromptStatus.OUT_OF_CONTEXT}

        context = "\n\n---\n\n".join([doc.page_content for doc, _ in results])
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context, question=query)

        try:
            response = self._model.invoke(prompt)
        except Exception:  # pragma: no cover - network failure path
            logger.exception("Model invocation failed", extra={"query": query})
            failure_message = (
                "Loo-loo! I hit a cosmic glitch while generating the answer. "
                "Please try again in a moment."
            )
            return {"answer": failure_message, "sources": [], "status": PromptStatus.FAILED}

        answer_text = getattr(response, "content", str(response))
        sources = [doc.metadata.get("source") for doc, _ in results if doc.metadata.get("source")]

        logger.info("Answer generated", extra={"sources": sources})
        return {"answer": answer_text, "sources": sources, "status": PromptStatus.SUCCESS}

    def get_scope_hints(self) -> list[str]:
        return SCOPE_HINTS
