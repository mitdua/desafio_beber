"""Embeddings-related exceptions."""

from src.domain.exceptions.base import DomainException


class EmbeddingGenerationException(DomainException):
    """Exception raised when embedding generation fails."""

    def __init__(self, message: str):
        super().__init__(f"Embedding generation error: {message}")