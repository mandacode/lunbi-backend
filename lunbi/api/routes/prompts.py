import logging

from fastapi import APIRouter, Depends

from lunbi.api.deps import get_prompt_service
from lunbi.api.schemas import PromptRequest, PromptResponse, SamplePromptsResponse
from lunbi.services.prompt_service import PromptService

router = APIRouter(prefix="/prompts", tags=["Prompts"])

logger = logging.getLogger("lunbi.api.prompts")


@router.post("", response_model=PromptResponse)
def create_prompt(
    payload: PromptRequest,
    service: PromptService = Depends(get_prompt_service),
) -> PromptResponse:
    result = service.process_prompt(payload.query)
    logger.info("Processed prompt", extra={"prompt_id": result.get("prompt_id")})
    return PromptResponse(**result)


@router.get("/samples", response_model=SamplePromptsResponse)
def get_sample_prompts(
    service: PromptService = Depends(get_prompt_service),
) -> SamplePromptsResponse:
    prompts = service.get_sample_prompts()
    logger.info("Serving sample prompts", extra={"count": len(prompts)})
    return SamplePromptsResponse(prompts=prompts)
