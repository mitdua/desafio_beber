"""Elasticsearch repository implementation."""

from typing import List, Tuple
from uuid import UUID
from elasticsearch import AsyncElasticsearch
from src.infra.config.logger import ILogger
from src.domain.repositories import IVectorRepository
from src.domain.exceptions import VectorStorageException, VectorSearchException


class ElasticsearchRepository(IVectorRepository):
    """Elasticsearch implementation of vector repository."""

    def __init__(
        self,
        logger: ILogger,
        client: AsyncElasticsearch,
        index_name: str = "documents",
        vector_size: int = 384,
        scheme: str = "http",
    ):
        """Initialize Elasticsearch client."""
        self.client = client
        self.index_name = index_name
        self.vector_size = vector_size
        self.logger = logger.get_logger()

        
    async def initialize_collection(self) -> None:
        """Initialize the Elasticsearch index with dense_vector mapping.
        
        Args:
            index_name: Name of the Elasticsearch index
            vector_size: Size of the vector
            scheme: Scheme of the Elasticsearch client

        Returns:
            None
        """
        try:
            # Check if the index exists
            exists = await self.client.indices.exists(index=self.index_name)
            if not exists:
                mapping = {
                    "properties": {
                        "embedding": {
                            "type": "dense_vector",
                            "dims": self.vector_size,
                            "index": True,
                            "similarity": "cosine"
                        },
                        "metadata": {
                            "type": "object",
                            "enabled": True
                        }
                    }
                }
               
                await self.client.indices.create(index=self.index_name, mappings=mapping)
                self.logger.info(f"Created Elasticsearch index: {self.index_name}")
            else:
                self.logger.info(f"Elasticsearch index {self.index_name} already exists")
        except Exception as e:
            self.logger.error(f"Error initializing Elasticsearch index: {e}")
            raise VectorStorageException(f"Failed to initialize index: {e}")

    async def store_vector(
        self, document_id: UUID, vector: List[float], metadata: dict
    ) -> None:
        """Store a vector with associated metadata.
        
        Args:
            document_id: ID of the document
            vector: List of floats representing the vector
            metadata: Dictionary of metadata

        Returns:
            None
        """
        try:
            document = {
                "embedding": vector,
                "metadata": metadata
            }
            
            await self.client.index(
                index=self.index_name,
                id=str(document_id),
                document=document,
                refresh=True
            )
            
            self.logger.info(f"Stored vector for document {document_id}")
        except Exception as e:
            self.logger.error(f"Error storing vector in Elasticsearch: {e}")
            raise VectorStorageException(f"Failed to store vector: {e}")

    async def search(
        self, query_vector: List[float], top_k: int = 5
    ) -> List[Tuple[UUID, float]]:
        """Search for similar vectors using kNN.
        
        Args:
            query_vector: List of floats representing the query vector
            top_k: Number of similar vectors to return

        Returns:
            List of tuples containing the document ID and score
        """
        try:            
            knn_query = {
                "field": "embedding",
                "query_vector": query_vector,
                "k": top_k,
                "num_candidates": top_k * 10
            }
            
            response = await self.client.search(
                index=self.index_name,
                knn=knn_query,
                size=top_k
            )
            
            results = [
                {
                    "id": hit["_id"],
                    "score": hit["_score"],
                    "metadata": hit["_source"].get("metadata", {}),
                }
                for hit in response["hits"]["hits"]
            ]
            
            self.logger.info(f"Found {len(results)} similar documents")
            return results
        except Exception as e:
            self.logger.error(f"Error searching vectors in Elasticsearch: {e}")
            raise VectorSearchException(f"Failed to search vectors: {e}")

    async def delete_vector(self, document_id: UUID) -> None:
        """Delete a vector by document ID.
        
        Args:
            document_id: ID of the document

        Returns:
            None
        """
        try:
            await self.client.delete(
                index=self.index_name,
                id=str(document_id),
                refresh=True
            )
            self.logger.info(f"Deleted vector for document {document_id}")
        except Exception as e:
            self.logger.error(f"Error deleting vector from Elasticsearch: {e}")
            raise VectorStorageException(f"Failed to delete vector: {e}")

    async def close(self) -> None:
        """Close the Elasticsearch client connection.
        
        Returns:
            None
        """
        await self.client.close()
