"""Documents API routes."""

from typing import List
from io import BytesIO
from http import HTTPStatus
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from src.infra.config.logger import ILogger

from src.application.use_cases import UploadDocumentUseCase
from src.application.dtos import DocumentUploadResponse, DocumentResponse
from src.domain.exceptions import InvalidDocumentException, DocumentStorageException
from src.infra.config.dependencies import upload_document_use_case, logger_config


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=HTTPStatus.CREATED,
    summary="Upload documents",
    description=(
        "Upload one or more documents for semantic search. "
        "Supports .pdf, .txt, .doc, .docx, .xls, .xlsx, .json files."
    ),
)

async def upload_documents(
    files: List[UploadFile] = File(..., description="Document files to upload"),
    upload_use_case: UploadDocumentUseCase = Depends(upload_document_use_case),
    logger: ILogger = Depends(logger_config),
) -> DocumentUploadResponse:
    """
    Uploads multiple documents for semantic search.

    This endpoint accepts multiple files, reads each one, and processes them as follows:
    1. Reads the file content.
    2. Passes the file and its metadata to the upload use case for processing.
       (This may include extraction, storage, embedding generation, and vector storage,
        depending on business logic.)
    3. Collects the upload results or errors for each file.

    Args:
        files: List of files to upload.
        upload_use_case: Injected use case to handle the upload logic.
        logger: Injected logger for recording info and errors.

    Returns:
        A response containing the successfully uploaded document details.
        If no files succeed, returns an HTTP 400 error with specific messages.
    """
    
    if not files:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="No files provided",
        )

    uploaded_documents = []
    errors = []

    for upload_file in files:
        try:
            logger.info(f"Processing upload: {upload_file.filename}")

            # Read file content
            content = await upload_file.read()
            file_stream = BytesIO(content)

            # Process document
            document = await upload_use_case.execute(
                file=file_stream,
                filename=upload_file.filename,
                metadata={
                    "content_type": upload_file.content_type or "unknown",
                    "size": str(len(content)),
                },
            )

            # Build response
            doc_response = DocumentResponse(
                id=document.id,
                filename=document.filename,
                metadata=document.metadata,
                created_at=document.created_at,
            )
            uploaded_documents.append(doc_response)

        except InvalidDocumentException as e:
            logger.error(f"Invalid document {upload_file.filename}: {e}")
            errors.append(f"{upload_file.filename}: {e.message}")
        except DocumentStorageException as e:
            logger.error(f"Storage error for {upload_file.filename}: {e}")
            errors.append(f"{upload_file.filename}: {e.message}")
        except Exception as e:
            logger.error(f"Unexpected error processing {upload_file.filename}: {e}")
            errors.append(f"{upload_file.filename}: Unexpected error")

    # If all files failed, return error
    if not uploaded_documents and errors:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Failed to process files: {'; '.join(errors)}",
        )

    # Build success message
    message = f"Successfully uploaded {len(uploaded_documents)} document(s)"
    if errors:
        message += f". Failed: {len(errors)} document(s)"

    return DocumentUploadResponse(
        success=True,
        documents=uploaded_documents,
        message=message,
    )
