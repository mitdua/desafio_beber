"""Upload document use case."""

from typing import BinaryIO
from src.domain.entities import Document
from src.infra.config.logger import ILogger
from src.domain.repositories import (
    IDocumentRepository,
    IVectorRepository,
    IEmbeddingService,
)
from src.infra.services.file_parser import IFileParser
from uuid import uuid5, NAMESPACE_URL


class UploadDocumentUseCase:
    """Use case for uploading and processing documents."""

    def __init__(
        self,
        document_repository: IDocumentRepository,
        vector_repository: IVectorRepository,
        embedding_service: IEmbeddingService,
        file_parser: IFileParser,
        logger: ILogger,
    ):
        """Initialize the use case with required repositories."""
        self.document_repository = document_repository
        self.vector_repository = vector_repository
        self.embedding_service = embedding_service
        self.file_parser = file_parser
        self.logger = logger.get_logger()

    async def execute(
        self, file: BinaryIO, filename: str, metadata: dict = None
    ) -> Document:
        """
        Execute the document upload process.
        
        Steps:
        1. Parse file content based on file type
        2. Create document entity
        3. Save document to MinIO
        4. Generate embedding
        5. Store embedding in Qdrant
        
        Args:
            file: Binary file content
            filename: Name of the file
            metadata: Optional metadata to store with document
            
        Returns:
            Document entity with generated ID
        """
        self.logger.info(f"Starting document upload: {filename}")

        # Step 1: Save document to MinIO
        document = Document(
            content=file.read(),
            filename=filename,
            metadata=metadata or {},
        )
        await self.document_repository.save(document)
        self.logger.info(f"Saved document {document.id} to storage")

        
        # Step 2: Parse file content
        content = await self.file_parser.parse_file(document)
        
        # Step 3: Generate embedding
        embeddings = await self.embedding_service.generate_embedding(content.ok_value)
        self.logger.info(f"Generated embedding for document {document.id}")
        
        # Step 4: Store embedding in Qdrant
        for index, embedding in enumerate(embeddings):
            vector_metadata = {
                "filename": document.filename,
                "created_at": document.created_at.isoformat(),
                **(document.metadata or {}),
                "chunk": embedding["chunk"],
                "chunk_index": index,
            }
            chunk_id = uuid5(NAMESPACE_URL, f"{document.id}/{index}")
            await self.vector_repository.store_vector(
                chunk_id, 
                embedding["embedding"], 
                vector_metadata
            )

        self.logger.info(f"Stored embedding for document {document.id} in vector database")
        
        return document
