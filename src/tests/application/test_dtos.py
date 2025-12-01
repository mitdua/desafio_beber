"""Test de DTOs"""

import pytest
from pydantic import ValidationError

from src.application.dtos.document_dtos import (
    DocumentResponse,
    DocumentUploadResponse,
    QueryRequest,
    QueryResultResponse,
    QueryResponse
)

class TestDocumentResponse:
    """Tests for DocumentResponse DTO."""

    def test_create_valid_document_response(self, sample_document_data):
        """Test creating a valid DocumentResponse."""
        doc = DocumentResponse(**sample_document_data)
        
        assert doc.id == sample_document_data["id"]
        assert doc.filename == sample_document_data["filename"]
        assert doc.metadata == sample_document_data["metadata"]
        assert doc.created_at == sample_document_data["created_at"]

    def test_document_response_with_empty_metadata(self, sample_uuid, sample_datetime):
        """Test DocumentResponse with empty metadata."""
        doc = DocumentResponse(
            id=sample_uuid,
            filename="test.pdf",
            metadata={},
            created_at=sample_datetime
        )
        assert doc.metadata == {}

    def test_document_response_with_complex_metadata(self, sample_uuid, sample_datetime):
        """Test DocumentResponse with complex nested metadata."""
        complex_metadata = {
            "author": "John Doe",
            "tags": ["important", "draft"],
            "nested": {
                "level1": {
                    "level2": "value"
                }
            },
            "numbers": [1, 2, 3]
        }
        doc = DocumentResponse(
            id=sample_uuid,
            filename="test.pdf",
            metadata=complex_metadata,
            created_at=sample_datetime
        )
        assert doc.metadata == complex_metadata

    def test_document_response_missing_required_fields(self):
        """Test DocumentResponse validation with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            DocumentResponse()
        
        errors = exc_info.value.errors()
        assert len(errors) == 4  # id, filename, metadata, created_at

    def test_document_response_invalid_uuid(self, sample_datetime):
        """Test DocumentResponse with invalid UUID."""
        with pytest.raises(ValidationError) as exc_info:
            DocumentResponse(
                id="not-a-uuid",
                filename="test.pdf",
                metadata={},
                created_at=sample_datetime
            )
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "uuid_parsing" for error in errors)

    def test_document_response_invalid_datetime(self, sample_uuid):
        """Test DocumentResponse with invalid datetime."""
        with pytest.raises(ValidationError) as exc_info:
            DocumentResponse(
                id=sample_uuid,
                filename="test.pdf",
                metadata={},
                created_at="not-a-datetime"
            )
        
        errors = exc_info.value.errors()
        assert any("datetime" in error["type"] for error in errors)


class TestDocumentUploadResponse:
    """Tests for DocumentUploadResponse DTO."""

    def test_create_valid_document_upload_response(self, sample_document_data):
        """Test creating a valid DocumentUploadResponse."""
        doc_response = DocumentResponse(**sample_document_data)
        upload_response = DocumentUploadResponse(
            success=True,
            documents=[doc_response],
            message="Upload successful"
        )
        
        assert upload_response.success is True
        assert len(upload_response.documents) == 1
        assert upload_response.documents[0].id == sample_document_data["id"]
        assert upload_response.message == "Upload successful"

    def test_document_upload_response_with_multiple_documents(self, sample_uuid, sample_datetime):
        """Test DocumentUploadResponse with multiple documents."""
        docs = [
            DocumentResponse(
                id=sample_uuid,
                filename=f"doc_{i}.pdf",
                metadata={"index": i},
                created_at=sample_datetime
            )
            for i in range(3)
        ]
        
        upload_response = DocumentUploadResponse(
            success=True,
            documents=docs,
            message="Multiple uploads successful"
        )
        
        assert len(upload_response.documents) == 3
        assert upload_response.documents[0].filename == "doc_0.pdf"
        assert upload_response.documents[2].filename == "doc_2.pdf"

    def test_document_upload_response_with_empty_documents_list(self):
        """Test DocumentUploadResponse with empty documents list."""
        upload_response = DocumentUploadResponse(
            success=False,
            documents=[],
            message="No documents uploaded"
        )
        
        assert upload_response.success is False
        assert len(upload_response.documents) == 0

    def test_document_upload_response_missing_required_fields(self):
        """Test DocumentUploadResponse validation with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            DocumentUploadResponse()
        
        errors = exc_info.value.errors()
        assert len(errors) == 3  # success, documents, message


class TestQueryRequest:
    """Tests for QueryRequest DTO."""

    def test_create_valid_query_request(self):
        """Test creating a valid QueryRequest."""
        query = QueryRequest(query="test query", top_k=10)
        
        assert query.query == "test query"
        assert query.top_k == 10

    def test_query_request_with_default_top_k(self):
        """Test QueryRequest uses default top_k value."""
        query = QueryRequest(query="test query")
        
        assert query.query == "test query"
        assert query.top_k == 5  # Default value

    def test_query_request_min_length_validation(self):
        """Test QueryRequest validates minimum query length."""
        with pytest.raises(ValidationError) as exc_info:
            QueryRequest(query="")
        
        errors = exc_info.value.errors()
        assert any(
            error["type"] == "string_too_short" and 
            error["loc"] == ("query",)
            for error in errors
        )

    def test_query_request_top_k_minimum_validation(self):
        """Test QueryRequest validates top_k minimum value."""
        with pytest.raises(ValidationError) as exc_info:
            QueryRequest(query="test", top_k=0)
        
        errors = exc_info.value.errors()
        assert any(
            error["type"] == "greater_than_equal" and 
            error["loc"] == ("top_k",)
            for error in errors
        )

    def test_query_request_top_k_maximum_validation(self):
        """Test QueryRequest validates top_k maximum value."""
        with pytest.raises(ValidationError) as exc_info:
            QueryRequest(query="test", top_k=51)
        
        errors = exc_info.value.errors()
        assert any(
            error["type"] == "less_than_equal" and 
            error["loc"] == ("top_k",)
            for error in errors
        )

    def test_query_request_top_k_boundary_values(self):
        """Test QueryRequest accepts boundary values for top_k."""
        query_min = QueryRequest(query="test", top_k=1)
        query_max = QueryRequest(query="test", top_k=50)
        
        assert query_min.top_k == 1
        assert query_max.top_k == 50

    def test_query_request_missing_query_field(self):
        """Test QueryRequest validation with missing query field."""
        with pytest.raises(ValidationError) as exc_info:
            QueryRequest(top_k=10)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("query",) for error in errors)


class TestQueryResultResponse:
    """Tests for QueryResultResponse DTO."""

    def test_create_valid_query_result_response(self, sample_document_data):
        """Test creating a valid QueryResultResponse."""
        doc = DocumentResponse(**sample_document_data)
        result = QueryResultResponse(
            document=doc,
            score=0.95,
            rank=1
        )
        
        assert result.document.id == sample_document_data["id"]
        assert result.score == 0.95
        assert result.rank == 1

    def test_query_result_response_with_zero_score(self, sample_document_data):
        """Test QueryResultResponse accepts zero score."""
        doc = DocumentResponse(**sample_document_data)
        result = QueryResultResponse(
            document=doc,
            score=0.0,
            rank=1
        )
        
        assert result.score == 0.0

    def test_query_result_response_with_negative_score(self, sample_document_data):
        """Test QueryResultResponse accepts negative score."""
        doc = DocumentResponse(**sample_document_data)
        result = QueryResultResponse(
            document=doc,
            score=-0.5,
            rank=1
        )
        
        assert result.score == -0.5

    def test_query_result_response_missing_required_fields(self):
        """Test QueryResultResponse validation with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            QueryResultResponse()
        
        errors = exc_info.value.errors()
        assert len(errors) == 3  # document, score, rank

    def test_query_result_response_invalid_score_type(self, sample_document_data):
        """Test QueryResultResponse with invalid score type."""
        doc = DocumentResponse(**sample_document_data)
        with pytest.raises(ValidationError) as exc_info:
            QueryResultResponse(
                document=doc,
                score="not a float",
                rank=1
            )
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "float_parsing" for error in errors)


class TestQueryResponse:
    """Tests for QueryResponse DTO."""

    def test_create_valid_query_response(self, sample_document_data):
        """Test creating a valid QueryResponse."""
        doc = DocumentResponse(**sample_document_data)
        result = QueryResultResponse(
            document=doc,
            score=0.95,
            rank=1
        )
        
        query_response = QueryResponse(
            query="test query",
            results=[result],
            total_results=1
        )
        
        assert query_response.query == "test query"
        assert len(query_response.results) == 1
        assert query_response.results[0].score == 0.95
        assert query_response.total_results == 1

    def test_query_response_with_multiple_results(self, sample_uuid, sample_datetime):
        """Test QueryResponse with multiple results."""
        results = [
            QueryResultResponse(
                document=DocumentResponse(
                    id=sample_uuid,
                    filename=f"doc_{i}.pdf",
                    metadata={"rank": i},
                    created_at=sample_datetime
                ),
                score=0.9 - (i * 0.1),
                rank=i + 1
            )
            for i in range(3)
        ]
        
        query_response = QueryResponse(
            query="test query",
            results=results,
            total_results=3
        )
        
        assert len(query_response.results) == 3
        assert query_response.results[0].rank == 1
        assert query_response.results[2].rank == 3
        assert query_response.total_results == 3

    def test_query_response_with_empty_results(self):
        """Test QueryResponse with empty results list."""
        query_response = QueryResponse(
            query="test query",
            results=[],
            total_results=0
        )
        
        assert len(query_response.results) == 0
        assert query_response.total_results == 0

    def test_query_response_missing_required_fields(self):
        """Test QueryResponse validation with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            QueryResponse()
        
        errors = exc_info.value.errors()
        assert len(errors) == 3  # query, results, total_results

    def test_query_response_invalid_total_results_type(self, sample_document_data):
        """Test QueryResponse with invalid total_results type."""
        doc = DocumentResponse(**sample_document_data)
        result = QueryResultResponse(
            document=doc,
            score=0.95,
            rank=1
        )
        
        with pytest.raises(ValidationError) as exc_info:
            QueryResponse(
                query="test",
                results=[result],
                total_results="not an int"
            )
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "int_parsing" for error in errors)

    def test_query_response_negative_total_results(self, sample_document_data):
        """Test QueryResponse accepts negative total_results (edge case)."""
        doc = DocumentResponse(**sample_document_data)
        result = QueryResultResponse(
            document=doc,
            score=0.95,
            rank=1
        )
        
        # Pydantic doesn't validate int range by default, so this should work
        query_response = QueryResponse(
            query="test",
            results=[result],
            total_results=-1
        )
        
        assert query_response.total_results == -1
