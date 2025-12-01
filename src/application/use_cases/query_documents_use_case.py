"""Query documents use case."""

from typing import List
from src.domain.entities import Document, QueryResult
from src.domain.repositories import (
    IDocumentRepository,
    IVectorRepository,
    IEmbeddingService,
)
from src.infra.config.logger import ILogger
from datetime import datetime

class QueryDocumentsUseCase:
    """Use case for querying documents using semantic search."""

    def __init__(
        self,
        document_repository: IDocumentRepository,
        vector_repository: IVectorRepository,
        embedding_service: IEmbeddingService,
        logger: ILogger,
    ):
        """Initialize the use case with required repositories."""
        self.document_repository = document_repository
        self.vector_repository = vector_repository
        self.embedding_service = embedding_service
        self.logger = logger.get_logger()


    async def execute(self, query: str, top_k: int = 5) -> List[QueryResult]:
        """
        Execute semantic search query.
        
        Steps:
        1. Generate embedding for query
        2. Search for similar vectors in Qdrant
        3. Retrieve documents from MinIO
        4. Build and return query results
        
        Args:
            query: Search query text
            top_k: Number of results to return
            
        Returns:
            List of QueryResult entities ordered by relevance
        """
        self.logger.info(f"Processing query: '{query}' (top_k={top_k})")
        
        # Step 1: Generate query embedding
        query_embedding = await self.embedding_service.generate_embedding_from_query(query)
        self.logger.info("Generated query embedding")
        
        # Step 2: Search for similar vectors
        search_results = await self.vector_repository.search(query_embedding, top_k)
        self.logger.info(f"Found {len(search_results)} similar documents")
        
        # Step 3 & 4: Retrieve documents and build results
        results = []
        for rank, search_result in enumerate(search_results, start=1):
            
            document = Document(
                id=search_result["id"],
                filename=search_result["metadata"]["filename"],
                content=search_result["metadata"]["chunk"],
                metadata=search_result["metadata"],
                created_at=datetime.fromisoformat(search_result["metadata"]["created_at"]),
            )            
            # Create query result
            result = QueryResult(
                document=document,
                score=search_result["score"],
                rank=rank,
            )
            results.append(result)
        
        self.logger.info(f"Returning {len(results)} query results")
        return results

