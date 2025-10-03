import datetime
import enum

from sqlalchemy import Column, DateTime, Enum, Integer, Text

from lunbi.database import Base


class PromptStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    OUT_OF_CONTEXT = "outofcontext"


class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    status = Column(Enum(PromptStatus, name="prompt_status"), nullable=False, default=PromptStatus.SUCCESS)

    def __repr__(self) -> str:
        return f"<Prompt id={self.id} status={self.status}>"
