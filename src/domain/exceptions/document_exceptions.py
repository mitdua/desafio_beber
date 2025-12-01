"""Document-related exceptions."""

from src.domain.exceptions.base import DomainException


class DocumentNotFoundException(DomainException):
    """Exception raised when a document is not found."""

    def __init__(self, document_id: str):
        super().__init__(f"Document with ID {document_id} not found")


class DocumentStorageException(DomainException):
    """Exception raised when document storage fails."""

    def __init__(self, message: str):
        super().__init__(f"Document storage error: {message}")


class InvalidDocumentException(DomainException):
    """Exception raised when a document is invalid."""

    def __init__(self, message: str):
        super().__init__(f"Invalid document: {message}")

