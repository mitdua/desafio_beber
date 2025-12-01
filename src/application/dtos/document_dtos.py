"""Document DTOs for API requests and responses."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, List, Any
from uuid import UUID

class DocumentResponse(BaseModel):
    """Response model for a single document."""
    id: UUID
    filename: str
    metadata: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""

    success: bool
    documents: List[DocumentResponse]
    message: str


class QueryRequest(BaseModel):
    """Request model for semantic search query."""

    query: str = Field(..., min_length=1, description="The search query text")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of results to return")


class QueryResultResponse(BaseModel):
    """Response model for a single query result."""

    document: DocumentResponse
    score: float
    rank: int


class QueryResponse(BaseModel):
    """Response model for query results."""

    query: str
    results: List[QueryResultResponse]
    total_results: int

