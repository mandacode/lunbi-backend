import logging

from fastapi import APIRouter, Depends

from lunbi.api.schemas import PromptRequest, PromptResponse
from lunbi.api.deps import get_prompt_service
from lunbi.services.prompt_service import PromptService

router = APIRouter(prefix="/prompts", tags=["Prompts"])

logger = logging.getLogger("lunbi.api.prompts")

@router.post("", response_model=PromptResponse)
def create_prompt(
    payload: PromptRequest,
    service: PromptService = Depends(get_prompt_service),
) -> PromptResponse:
    result = service.process_prompt(payload.query)
    logger.info(f"Processed prompt: {result}")
    return PromptResponse(**result)


@router.get("/samples", response_model=list[str])
def get_sample_prompts(service: PromptService = Depends(get_prompt_service)):
    logger.info("Getting sample prompts")
    return service.get_sample_prompts()
