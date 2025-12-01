"""Health check API routes."""

from fastapi import APIRouter
from http import HTTPStatus


router = APIRouter(tags=["health"])


@router.get(
    "/health",
    status_code=HTTPStatus.OK,
    summary="Health check",
    description="Check if the API is running",
)
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "RAG API"}

