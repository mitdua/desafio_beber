"""Test de entidades"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import ValidationError

from src.domain.entities.document import Document, QueryResult


class TestDocument:
    """Tests for Document entity."""

    def test_create_document_with_all_fields(self, sample_uuid, sample_datetime, sample_metadata):
        """Test creating a Document with all fields explicitly provided."""
        content = b"Test document content"
        doc = Document(
            id=sample_uuid,
            content=content,
            filename="test.pdf",
            metadata=sample_metadata,
            created_at=sample_datetime
        )
        
        assert doc.id == sample_uuid
        assert doc.content == content
        assert doc.filename == "test.pdf"
        assert doc.metadata == sample_metadata
        assert doc.created_at == sample_datetime

    def test_create_document_with_defaults(self):
        """Test creating a Document with default values for id, metadata, and created_at."""
        content = b"Test document content"
        doc = Document(
            content=content,
            filename="test.pdf"
        )
        
        assert doc.id is not None
        assert isinstance(doc.id, type(uuid4()))
        assert doc.content == content
        assert doc.filename == "test.pdf"
        assert doc.metadata == {}
        assert doc.created_at is not None
        assert isinstance(doc.created_at, datetime)

    def test_create_document_with_default_id_only(self, sample_datetime, sample_metadata):
        """Test creating a Document with default id but explicit metadata and created_at."""
        content = b"Test document content"
        doc = Document(
            content=content,
            filename="test.pdf",
            metadata=sample_metadata,
            created_at=sample_datetime
        )
        
        assert doc.id is not None
        assert doc.metadata == sample_metadata
        assert doc.created_at == sample_datetime

    def test_create_document_with_empty_metadata(self):
        """Test creating a Document with empty metadata."""
        content = b"Test document content"
        doc = Document(
            content=content,
            filename="test.pdf",
            metadata={}
        )
        
        assert doc.metadata == {}

    def test_create_document_with_complex_metadata(self):
        """Test creating a Document with complex nested metadata."""
        content = b"Test document content"
        complex_metadata = {
            "author": "John Doe",
            "tags": ["important", "draft"],
            "nested": {
                "level1": {
                    "level2": "value"
                }
            },
            "numbers": [1, 2, 3],
            "boolean": True
        }
        doc = Document(
            content=content,
            filename="test.pdf",
            metadata=complex_metadata
        )
        
        assert doc.metadata == complex_metadata
        assert doc.metadata["nested"]["level1"]["level2"] == "value"

    def test_create_document_with_empty_content(self):
        """Test creating a Document with empty bytes content."""
        doc = Document(
            content=b"",
            filename="test.pdf"
        )
        
        assert doc.content == b""

    def test_create_document_with_large_content(self):
        """Test creating a Document with large content."""
        large_content = b"x" * 10000
        doc = Document(
            content=large_content,
            filename="test.pdf"
        )
        
        assert len(doc.content) == 10000
        assert doc.content == large_content

    def test_document_missing_required_fields(self):
        """Test Document validation with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            Document()
        
        errors = exc_info.value.errors()
        # content and filename are required
        assert len(errors) == 2
        error_fields = [error["loc"][0] for error in errors]
        assert "content" in error_fields
        assert "filename" in error_fields

    def test_document_missing_content(self):
        """Test Document validation with missing content."""
        with pytest.raises(ValidationError) as exc_info:
            Document(filename="test.pdf")
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("content",) for error in errors)

    def test_document_missing_filename(self):
        """Test Document validation with missing filename."""
        with pytest.raises(ValidationError) as exc_info:
            Document(content=b"test")
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("filename",) for error in errors)

    def test_document_invalid_filename_type(self):
        """Test Document validation with invalid filename type."""
        with pytest.raises(ValidationError) as exc_info:
            Document(
                content=b"test",
                filename=123  # Should be str
            )
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "string_type" for error in errors)

    def test_document_invalid_uuid(self):
        """Test Document validation with invalid UUID."""
        with pytest.raises(ValidationError) as exc_info:
            Document(
                id="not-a-uuid",
                content=b"test",
                filename="test.pdf"
            )
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "uuid_parsing" for error in errors)

    def test_document_invalid_datetime(self):
        """Test Document validation with invalid datetime."""
        with pytest.raises(ValidationError) as exc_info:
            Document(
                content=b"test",
                filename="test.pdf",
                created_at="not-a-datetime"
            )
        
        errors = exc_info.value.errors()
        assert any("datetime" in error["type"] for error in errors)

    def test_document_default_id_is_unique(self):
        """Test that default factory generates unique IDs."""
        doc1 = Document(content=b"test1", filename="test1.pdf")
        doc2 = Document(content=b"test2", filename="test2.pdf")
        
        assert doc1.id != doc2.id

    def test_document_default_created_at_is_recent(self):
        """Test that default created_at is recent (within last minute)."""
        before = datetime.now(timezone.utc)
        doc = Document(content=b"test", filename="test.pdf")
        after = datetime.now(timezone.utc)
        
        assert before <= doc.created_at <= after

    def test_document_with_different_file_types(self):
        """Test creating Documents with different file types."""
        file_types = ["test.pdf", "test.docx", "test.txt", "document.xlsx"]
        
        for filename in file_types:
            doc = Document(
                content=b"content",
                filename=filename
            )
            assert doc.filename == filename

    def test_document_metadata_preserves_types(self):
        """Test that Document metadata preserves different data types."""
        content = b"test"
        metadata = {
            "string": "value",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "none": None
        }
        
        doc = Document(
            content=content,
            filename="test.pdf",
            metadata=metadata
        )
        
        assert doc.metadata["string"] == "value"
        assert doc.metadata["int"] == 42
        assert doc.metadata["float"] == 3.14
        assert doc.metadata["bool"] is True
        assert doc.metadata["list"] == [1, 2, 3]
        assert doc.metadata["dict"] == {"nested": "value"}
        assert doc.metadata["none"] is None


class TestQueryResult:
    """Tests for QueryResult entity."""

    def test_create_query_result_with_valid_document(self):
        """Test creating a QueryResult with a valid Document."""
        doc = Document(
            content=b"test content",
            filename="test.pdf"
        )
        result = QueryResult(
            document=doc,
            score=0.95,
            rank=1
        )
        
        assert result.document.id == doc.id
        assert result.document.filename == "test.pdf"
        assert result.score == 0.95
        assert result.rank == 1

    def test_create_query_result_with_zero_score(self):
        """Test QueryResult accepts zero score."""
        doc = Document(content=b"test", filename="test.pdf")
        result = QueryResult(
            document=doc,
            score=0.0,
            rank=1
        )
        
        assert result.score == 0.0

    def test_create_query_result_with_negative_score(self):
        """Test QueryResult accepts negative score."""
        doc = Document(content=b"test", filename="test.pdf")
        result = QueryResult(
            document=doc,
            score=-0.5,
            rank=1
        )
        
        assert result.score == -0.5

    def test_create_query_result_with_high_score(self):
        """Test QueryResult accepts high score values."""
        doc = Document(content=b"test", filename="test.pdf")
        result = QueryResult(
            document=doc,
            score=1.0,
            rank=1
        )
        
        assert result.score == 1.0

    def test_create_query_result_with_different_ranks(self):
        """Test QueryResult with different rank values."""
        doc = Document(content=b"test", filename="test.pdf")
        
        for rank in [1, 5, 10, 100]:
            result = QueryResult(
                document=doc,
                score=0.9,
                rank=rank
            )
            assert result.rank == rank

    def test_query_result_missing_required_fields(self):
        """Test QueryResult validation with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            QueryResult()
        
        errors = exc_info.value.errors()
        assert len(errors) == 3  # document, score, rank

    def test_query_result_missing_document(self):
        """Test QueryResult validation with missing document."""
        with pytest.raises(ValidationError) as exc_info:
            QueryResult(
                score=0.95,
                rank=1
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("document",) for error in errors)

    def test_query_result_missing_score(self):
        """Test QueryResult validation with missing score."""
        doc = Document(content=b"test", filename="test.pdf")
        with pytest.raises(ValidationError) as exc_info:
            QueryResult(
                document=doc,
                rank=1
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("score",) for error in errors)

    def test_query_result_missing_rank(self):
        """Test QueryResult validation with missing rank."""
        doc = Document(content=b"test", filename="test.pdf")
        with pytest.raises(ValidationError) as exc_info:
            QueryResult(
                document=doc,
                score=0.95
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("rank",) for error in errors)

    def test_query_result_invalid_score_type(self):
        """Test QueryResult validation with invalid score type."""
        doc = Document(content=b"test", filename="test.pdf")
        with pytest.raises(ValidationError) as exc_info:
            QueryResult(
                document=doc,
                score="not a float",  # Should be float
                rank=1
            )
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "float_parsing" for error in errors)

    def test_query_result_invalid_rank_type(self):
        """Test QueryResult validation with invalid rank type."""
        doc = Document(content=b"test", filename="test.pdf")
        with pytest.raises(ValidationError) as exc_info:
            QueryResult(
                document=doc,
                score=0.95,
                rank="not an int"  # Should be int
            )
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "int_parsing" for error in errors)

    def test_query_result_with_document_containing_metadata(self):
        """Test QueryResult with Document that has metadata."""
        doc = Document(
            content=b"test",
            filename="test.pdf",
            metadata={"author": "John Doe", "pages": 10}
        )
        result = QueryResult(
            document=doc,
            score=0.95,
            rank=1
        )
        
        assert result.document.metadata == {"author": "John Doe", "pages": 10}

    def test_query_result_float_score_precision(self):
        """Test QueryResult preserves float score precision."""
        doc = Document(content=b"test", filename="test.pdf")
        result = QueryResult(
            document=doc,
            score=0.123456789,
            rank=1
        )
        
        assert result.score == 0.123456789

    def test_query_result_zero_rank(self):
        """Test QueryResult accepts zero rank (edge case)."""
        doc = Document(content=b"test", filename="test.pdf")
        result = QueryResult(
            document=doc,
            score=0.95,
            rank=0
        )
        
        assert result.rank == 0

    def test_query_result_negative_rank(self):
        """Test QueryResult accepts negative rank (edge case)."""
        doc = Document(content=b"test", filename="test.pdf")
        result = QueryResult(
            document=doc,
            score=0.95,
            rank=-1
        )
        
        assert result.rank == -1
