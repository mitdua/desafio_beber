"""Vector-related exceptions."""

from src.domain.exceptions.base import DomainException


class VectorStorageException(DomainException):
    """Exception raised when vector storage fails."""

    def __init__(self, message: str):
        super().__init__(f"Vector storage error: {message}")


class VectorSearchException(DomainException):
    """Exception raised when vector search fails."""

    def __init__(self, message: str):
        super().__init__(f"Vector search error: {message}")

