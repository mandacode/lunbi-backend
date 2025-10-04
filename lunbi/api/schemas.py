from __future__ import annotations

from typing import List, Optional
from enum import Enum


from pydantic import BaseModel, Field


class Language(str, Enum):
    EN = "en"
    PL = "pl"


class SourceSchema(BaseModel):
    title: str
    url: str


class PromptRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User question for Lunbi")
    language: Language = Field(Language.EN, description="Response language")


class PromptResponse(BaseModel):
    answer: str
    status: str
    prompt_id: Optional[int] = None
    source: Optional[SourceSchema] = None
    language: Language = Field(Language.EN, description="Language of the answer")


class SamplePromptsResponse(BaseModel):
    prompts: List[str]
