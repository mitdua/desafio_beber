"""Embedding service interface."""

from abc import ABC, abstractmethod
from typing import List


class IEmbeddingService(ABC):
    """Abstract interface for embedding generation."""

    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding vector for the given text."""
        raise NotImplementedError
    
    @abstractmethod
    async def generate_embedding_from_query(self, query: str) -> List[float]:
        """Generate an embedding vector for the given query."""
        raise NotImplementedError

    @abstractmethod
    def get_dimension(self) -> int:
        """Get the dimension of the embeddings."""
        raise NotImplementedError

