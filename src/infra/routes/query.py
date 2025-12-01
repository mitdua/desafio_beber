"""Query API routes."""
from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from src.application.use_cases import QueryDocumentsUseCase
from src.application.dtos import (
    QueryRequest,
    QueryResponse,
    QueryResultResponse,
    DocumentResponse,
)
from src.domain.exceptions import VectorSearchException
from src.infra.config.dependencies import query_documents_use_case, logger_config
from src.infra.config.logger import ILogger


router = APIRouter(prefix="/query", tags=["query"])


@router.post(
    "",
    response_model=QueryResponse,
    status_code=HTTPStatus.OK,
    summary="Semantic search",
    description="Search for documents using semantic similarity.",
)
async def query_documents(
    request: QueryRequest,
    query_use_case: QueryDocumentsUseCase = Depends(query_documents_use_case),
    logger: ILogger = Depends(logger_config),
) -> QueryResponse:
    """
    Search for semantically similar documents.
    
    The endpoint processes the query text:
    1. Generates embedding for the query
    2. Searches Qdrant for similar document embeddings
    3. Retrieves the actual documents from MinIO
    4. Returns ranked results with similarity scores
    
    Args:
        request: Query request with search text and top_k
        query_use_case: Injected use case for document query
        
    Returns:
        Ranked list of similar documents with scores
    """
    try:
        logger.info(f"Processing query: '{request.query}' (top_k={request.top_k})")
        
        # Execute query
        results = await query_use_case.execute(
            query=request.query,
            top_k=request.top_k,
        )
        
        # Build response
        result_responses = [
            QueryResultResponse(
                document=DocumentResponse(
                    id=result.document.id,
                    filename=result.document.filename,
                    content=result.document.content,
                    metadata=result.document.metadata,
                    created_at=result.document.created_at,
                ),
                score=result.score,
                rank=result.rank,
            )
            for result in results
        ]
        
        return QueryResponse(
            query=request.query,
            results=result_responses,
            total_results=len(result_responses),
        )
        
    except VectorSearchException as e:
        logger.error(f"Vector search error: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {e.message}",
        )
    except Exception as e:
        logger.error(f"Unexpected error during query: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

