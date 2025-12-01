"""File parser service using Docling for document processing."""

import tempfile
from pathlib import Path
from abc import ABC, abstractmethod
from docling.document_converter import DocumentConverter
from src.domain.exceptions import InvalidDocumentException
from src.domain.entities import Document
from result import Result, Ok
from src.infra.config.settings import Settings
from src.infra.config.logger import ILogger


class IFileParser(ABC):
    """Interface for file parser."""

    @abstractmethod
    def parse_file(self, document: Document) -> Result:
        """Parse a document and return the result."""
        raise NotImplementedError


class FileParser(IFileParser):
    """Utility class for parsing different file formats using Docling.

    Args:
        settings: Settings for the application.
        logger: Logger for the application.

    Returns:
        Result: Result of the parsing operation.
            Ok: Result of the parsing operation.
            Err: Error of the parsing operation.

    Raises:
        InvalidDocumentException: If the document is invalid.
        Exception: If an error occurs while parsing the document.
    """

    def __init__(
        self,
        settings: Settings,
        logger: ILogger,
        document_converter: DocumentConverter,
    ):
        self.document_converter = document_converter
        self.logger = logger.get_logger()
        self.settings = settings

    def _get_extension(self, filename: str) -> str:
        """Extract file extension from filename.

        Args:
            filename: The filename to extract the extension from.

        Returns:
            The extension of the filename.
        """
        if "." in filename:
            return filename.rsplit(".", 1)[1].lower()
        return ""

    def _is_valid_extension(self, extension: str) -> bool:
        """Check if the extension is valid.

        Args:
            extension: The extension to check.

        Returns:
            True if the extension is valid, False otherwise.
        """
        return extension in self.settings.supported_file_extensions

    def _get_temporary_file(self, document: Document) -> Path:
        """Get a temporary file for the document.

        Args:
            document: The document to get the temporary file for.

        Returns:
            The temporary file.
        """
        with tempfile.NamedTemporaryFile(
            suffix=Path(document.filename).suffix.lower(), delete=False
        ) as tmp_file:
            tmp_file.write(document.content)
            return Path(tmp_file.name)

    async def parse_file(self, document: Document) -> Result:
        """Parse a document and return the result.

        Args:
            document: The document to parse.

        Returns:
            Ok: The result of the parsing operation.
            Err: The error of the parsing operation.

        Raises:
            InvalidDocumentException: If the document is invalid.
            Exception: If an error occurs while parsing the document.
        """
        extension = self._get_extension(document.filename)

        if not self._is_valid_extension(extension):
            raise InvalidDocumentException(
                f"Unsupported file format: {document.filename}. "
                f"Supported formats: {', '.join(sorted(self.settings.supported_file_extensions))}"
            )
        try:
            tmp_path = self._get_temporary_file(document)

            try:
                result = self.document_converter.convert(tmp_path)
                result_document = result.document

                if not result_document:
                    raise InvalidDocumentException(
                        f"Failed to convert document: {document.filename}"
                    )

                return Ok(result_document)

            finally:
                tmp_path.unlink(missing_ok=True)

        except InvalidDocumentException as e:
            self.logger.error(f"Error parsing file {document.filename}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error parsing file {document.filename}: {e}")
            raise InvalidDocumentException(f"Failed to parse file: {e}")
