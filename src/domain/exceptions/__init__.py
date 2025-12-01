"""Domain exceptions module."""

from src.domain.exceptions.base import DomainException
from src.domain.exceptions.document_exceptions import (
    DocumentNotFoundException,
    DocumentStorageException,
    InvalidDocumentException,
)
from src.domain.exceptions.vector_exceptions import (
    VectorStorageException,
    VectorSearchException,
)
from src.domain.exceptions.embeddings_exceptions import EmbeddingGenerationException

__all__ = [
    "DomainException",
    "DocumentNotFoundException",
    "DocumentStorageException",
    "InvalidDocumentException",
    "VectorStorageException",
    "VectorSearchException",
    "EmbeddingGenerationException",
]
