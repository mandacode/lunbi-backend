from datetime import datetime, timezone
import enum

from sqlalchemy import Column, DateTime, Enum, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base


class PromptStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    OUT_OF_CONTEXT = "outofcontext"


class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    best_answer = Column(Text, nullable=True)
    answers = Column(JSONB, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    status = Column(Enum(PromptStatus, name="prompt_status"), nullable=False, default=PromptStatus.SUCCESS)

    def __repr__(self) -> str:
        return f"<Prompt id={self.id} status={self.status}>"
