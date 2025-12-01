"""Document repository interface."""

from abc import ABC, abstractmethod
from src.domain.entities import Document
from result import Result 

class IDocumentRepository(ABC):
    """Abstract interface for document storage operations."""

    @abstractmethod
    async def save(self, document: Document) -> Result:
        """Save a document to storage."""
        raise NotImplementedError

