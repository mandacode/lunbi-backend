import logging

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from lunbi.api.deps import get_prompt_service, require_api_token
from lunbi.api.schemas import PromptRequest, PromptResponse, SamplePromptsResponse
from lunbi.services.prompt_service import PromptService

router = APIRouter(prefix="/prompts", tags=["Prompts"], dependencies=[Depends(require_api_token)])

logger = logging.getLogger("lunbi.api.prompts")


@router.post("", response_model=PromptResponse)
def create_prompt(
    payload: PromptRequest,
    service: PromptService = Depends(get_prompt_service),
) -> PromptResponse:
    result = service.process_prompt(payload.query, payload.language.value)
    logger.info("Processed prompt", extra={"prompt_id": result.get("prompt_id")})
    return PromptResponse(**result)


@router.post("/stream")
def stream_prompt(
    payload: PromptRequest,
    service: PromptService = Depends(get_prompt_service),
) -> StreamingResponse:
    logger.info(f"Streaming prompt response: query={payload.query}, language={payload.language.value},")
    stream = service.stream_prompt(payload.query, payload.language.value)
    headers = {"Cache-Control": "no-cache", "Connection": "keep-alive"}
    return StreamingResponse(stream, media_type="plain/text")
    # return StreamingResponse(stream, media_type="text/event-stream", headers=headers)


@router.get("/samples", response_model=SamplePromptsResponse)
def get_sample_prompts(
    service: PromptService = Depends(get_prompt_service),
) -> SamplePromptsResponse:
    prompts = service.get_sample_prompts()
    logger.info("Serving sample prompts", extra={"count": len(prompts)})
    return SamplePromptsResponse(prompts=prompts)
