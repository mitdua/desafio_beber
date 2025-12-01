"""Vector repository interface."""

from abc import ABC, abstractmethod
from typing import List, Tuple
from uuid import UUID


class IVectorRepository(ABC):
    """Abstract interface for vector storage and search operations."""

    @abstractmethod
    async def store_vector(
        self, document_id: UUID, vector: List[float], metadata: dict
    ) -> None:
        """Store a vector with associated metadata."""
        raise NotImplementedError

    @abstractmethod
    async def search(
        self, query_vector: List[float], top_k: int = 5
    ) -> List[Tuple[UUID, float]]:
        """Search for similar vectors and return document IDs with scores."""
        raise NotImplementedError

    @abstractmethod
    async def delete_vector(self, document_id: UUID) -> None:
        """Delete a vector by document ID."""
        raise NotImplementedError

    @abstractmethod
    async def initialize_collection(self) -> None:
        """Initialize the vector collection/index."""
        raise NotImplementedError
