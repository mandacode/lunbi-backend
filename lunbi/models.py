import datetime
import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from lunbi.database import Base


class PromptStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    OUT_OF_CONTEXT = "outofcontext"


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    url = Column(Text, nullable=False, unique=True)

    prompts = relationship("Prompt", back_populates="source")

    def __repr__(self) -> str:
        return f"<Source id={self.id} url={self.url}>"


class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    status = Column(Enum(PromptStatus, name="prompt_status"), nullable=False, default=PromptStatus.SUCCESS)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="SET NULL"), nullable=True)

    source = relationship("Source", back_populates="prompts")

    def __repr__(self) -> str:
        return f"<Prompt id={self.id} status={self.status}>"
