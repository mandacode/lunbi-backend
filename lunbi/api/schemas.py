from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class SourceSchema(BaseModel):
    title: str
    url: str


class PromptRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User question for Lunbi")


class PromptResponse(BaseModel):
    answer: str
    status: str
    prompt_id: Optional[int] = None
    source: Optional[SourceSchema] = None


class SamplePromptsResponse(BaseModel):
    prompts: List[str]
