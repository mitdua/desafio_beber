"""Sentence Transformer service implementation."""

from typing import List
from docling.chunking import HybridChunker
from transformers import AutoTokenizer

from sentence_transformers import SentenceTransformer
from src.infra.config.logger import ILogger
from src.domain.repositories import IEmbeddingService
from src.domain.exceptions.embeddings_exceptions import EmbeddingGenerationException


class SentenceTransformerService(IEmbeddingService):
    """Sentence Transformer implementation of embedding service."""

    def __init__(self, embedding_model: SentenceTransformer, logger: ILogger):
        """Initialize the sentence transformer model.
        
        Args:
            embedding_model: SentenceTransformer model
            logger: Logger instance
        """
        self.logger = logger.get_logger()
        self.embedding_model = embedding_model
        self._dimension = self.embedding_model.get_sentence_embedding_dimension()

    def _split_text_into_chunks(
        self,
        document,
        max_tokens: int = 2000,
    ) -> List[str]:
        """
        Split the document into manageable chunks for processing.

        Args:
            document: Docling document object to split into chunks
            max_tokens: Maximum size of each chunk in tokens

        Returns:
            List of chunks as strings
        """
        try:
            chunker = HybridChunker(
                tokenizer=self.embedding_model.tokenizer,
                max_tokens=max_tokens,
                merge_peers=True,
            )

            chunk_iter = chunker.chunk(dl_doc=document)
            chunks = []
            
            for chunk in chunk_iter:
                contextualized_text = chunker.contextualize(chunk=chunk)
                chunks.append(contextualized_text)

            self.logger.info(
                f"Created {len(chunks)} chunks from document "
                f"(max_tokens={max_tokens})"
            )

            return chunks

        except Exception as e:
            self.logger.error(f"Error creating chunks: {e}")
            raise

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding vector for the given text.
        
        Args:
            text: The text to generate an embedding for.

        Returns:
            List of floats representing the embedding
        """
        try:
            chunks = self._split_text_into_chunks(text)

            embeddings = [
                {
                    "chunk": chunk,
                    "embedding": self.embedding_model.encode_document(
                        chunk, 
                        convert_to_tensor=False,
                    ).tolist(),
                }
                for chunk in chunks
            ]

            self.logger.debug(f"Generated embedding for text")
            return embeddings

        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            raise EmbeddingGenerationException(f"Failed to generate embedding: {e}")

    async def generate_embedding_from_query(self, query: str) -> List[float]:
        """Generate an embedding vector for the given query.
        
        Args:
            query: The query to generate an embedding for.

        Raises:
            EmbeddingGenerationException: If the embedding generation fails.
        """
        try:
            return self.embedding_model.encode_query(query, convert_to_tensor=False).tolist()
        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            raise EmbeddingGenerationException(f"Failed to generate embedding: {e}")

    def get_dimension(self) -> int:
        """Get the dimension of the embeddings."""
        return self._dimension
