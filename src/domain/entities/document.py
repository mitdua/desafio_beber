"""Document entity module."""

from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Dict, Any
from uuid import UUID, uuid4


class Document(BaseModel):
    """Document entity representing a stored document."""

    id: UUID = Field(default_factory=uuid4)
    content: bytes
    filename: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        arbitrary_types_allowed = True


class QueryResult(BaseModel):
    """Query result entity representing a search result."""

    document: Document
    score: float
    rank: int
