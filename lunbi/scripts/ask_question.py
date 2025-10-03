import argparse
import logging
from typing import Any

from lunbi.services.prompt_service import PromptService

logger = logging.getLogger("lunbi.ask")
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def ask_question(query: str) -> dict[str, Any]:
    logger.info("Answering prompt via PromptService", extra={"query": query})
    service = PromptService()
    return service.answer_prompt(query)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("query", type=str)
    args = parser.parse_args()

    result = ask_question(query=args.query)

    sources = ", ".join(result.get("sources", [])) or "none"
    status = result.get("status")
    status_text = getattr(status, "value", status)
    print(f"Answer: {result['answer']}\nStatus: {status_text}\nSources: {sources}")


if __name__ == "__main__":
    main()
