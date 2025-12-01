"""MinIO repository implementation."""

import json
from io import BytesIO
from result import Result, Ok
import mimetypes

from minio import Minio
from minio.error import S3Error
from loguru import logger

from src.domain.entities import Document
from src.domain.repositories import IDocumentRepository
from src.domain.exceptions import (
    DocumentStorageException,
    InvalidDocumentException,
)
from src.infra.config.settings import Settings


class MinIORepository(IDocumentRepository):
    """MinIO implementation of document repository."""

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        settings: Settings,
        bucket_name: str = "documents",
        secure: bool = False,
    ):
        """Initialize MinIO client."""
        self.settings = settings
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self.bucket_name = bucket_name
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        """Ensure the bucket exists, create if not."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise DocumentStorageException(f"Failed to ensure bucket exists: {e}")

    def _get_content_type(self, filename: str) -> str:
        """Determine content type based on filename extension."""
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or "application/octet-stream"

    def _get_extension(self, filename: str) -> str:
        """Extract file extension from filename."""
        if "." in filename:
            return filename.rsplit(".", 1)[1].lower()
        return ""

    def _is_valid_extension(self, extension: str) -> bool:
        """Check if the extension is valid."""
        return extension in self.settings.supported_file_extensions

    async def save(self, document: Document) -> Result:
        """Save a document to MinIO preserving the original file."""
        try:
            # Determine content type and extension from original filename
            extension = self._get_extension(document.filename)
            content_type = self._get_content_type(document.filename)

            if not self._is_valid_extension(extension):
                raise InvalidDocumentException(
                    (
                        f"Unsupported file format: {extension}. ",
                        f"Supported formats: {', '.join(self.settings.supported_file_extensions)}",
                    )
                )

            file_object_name = f"{document.filename}.{extension}"
            # Save the original file
            file_stream = BytesIO(document.content)
            self.client.put_object(
                self.bucket_name,
                file_object_name,
                data=file_stream,
                length=len(document.content),
                content_type=content_type,
            )
            logger.info(f"Saved original file {file_object_name} to MinIO")

            # Also save metadata as a separate JSON file
            metadata_object_name = f"{document.filename}_metadata.json"
            metadata = {
                "id": str(document.id),
                "filename": document.filename,
                "original_extension": extension,
                "content_type": content_type,
                "file_size": len(document.content),
                "metadata": document.metadata,
                "created_at": document.created_at.isoformat(),
            }
            metadata_bytes = json.dumps(metadata, ensure_ascii=False).encode("utf-8")
            self.client.put_object(
                self.bucket_name,
                metadata_object_name,
                data=BytesIO(metadata_bytes),
                length=len(metadata_bytes),
                content_type="application/json",
            )
            logger.info(f"Saved metadata {metadata_object_name} to MinIO")

            return Ok(document)

        except S3Error as e:
            logger.error(f"Error saving document to MinIO: {e}")
            raise DocumentStorageException(f"Failed to save document: {e}")

        except Exception as e:
            logger.error(f"Unexpected error saving document to MinIO: {e}")
            return DocumentStorageException(f"Failed to save document: {e}")