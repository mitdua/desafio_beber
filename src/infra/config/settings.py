from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Settings for the application."""

    debug: bool = Field(default=True)
    environment: str = Field(
        default="development",
        description="Environment of the application, development, production, etc.",
    )
    # API Settings
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_title: str = "RAG Search API"
    api_description: str = "API for document search using embeddings"
    api_version: str = "0.1.0"

    # MinIO Settings
    minio_endpoint: str = Field(default="localhost:9000")
    minio_access_key: str = Field(default="admin")
    minio_secret_key: str = Field(default="admin123")
    minio_bucket_name: str = Field(default="documents")
    minio_secure: bool = Field(default=False)

    # Embedding Model Settings
    embedding_model_name: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    embedding_dimension: int = Field(default=384)

    # supported file extensions
    supported_file_extensions_str: str = Field(
        alias="SUPPORTED_FILE_EXTENSIONS",
        default=["pdf", "txt", "doc", "docx", "xls", "xlsx", "json"],
    )

    @property
    def supported_file_extensions(self) -> List[str]:
        return self.supported_file_extensions_str.split(",")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Elasticsearch Settings
    elasticsearch_host: str = Field(default="localhost")
    elasticsearch_port: int = Field(default=9200)
    elasticsearch_index_name: str = Field(default="documents")
    elasticsearch_scheme: str = Field(default="http") 
