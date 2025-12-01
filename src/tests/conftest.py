"""Pytest fixtures for testing DTOs and entities."""

import pytest
from uuid import uuid4
from datetime import datetime
from typing import Dict, Any


@pytest.fixture
def sample_uuid():
    """Generate a sample UUID for testing."""
    return uuid4()


@pytest.fixture
def sample_datetime():
    """Generate a sample datetime for testing."""
    return datetime(2024, 1, 15, 10, 30, 0)


@pytest.fixture
def sample_metadata():
    """Generate sample metadata dictionary."""
    return {
        "author": "Test Author",
        "pages": 10,
        "type": "pdf"
    }


@pytest.fixture
def sample_document_data(sample_uuid, sample_datetime, sample_metadata):
    """Generate sample document data for DocumentResponse."""
    return {
        "id": sample_uuid,
        "filename": "test_document.pdf",
        "metadata": sample_metadata,
        "created_at": sample_datetime
    }
