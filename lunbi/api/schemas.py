from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User question for Lunbi")


class PromptResponse(BaseModel):
    answer: str
    sources: List[str]
    status: str
    prompt_id: Optional[int] = None


class SamplePromptsResponse(BaseModel):
    prompts: List[str]
