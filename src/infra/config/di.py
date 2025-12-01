from dependency_injector import containers, providers
from sentence_transformers import SentenceTransformer
from src.infra.config.settings import Settings
from src.infra.config.logger import LoggerConfig
from src.infra.services import (
    MinIORepository,
    ElasticsearchRepository,
    SentenceTransformerService,
)
from src.application.use_cases import (
    UploadDocumentUseCase,
    QueryDocumentsUseCase,
)
from docling.document_converter import DocumentConverter
from src.infra.services.file_parser import FileParser
from elasticsearch import AsyncElasticsearch


class Container(containers.DeclarativeContainer):
    """Container for dependency injection."""

    config = providers.Singleton(Settings)

    logger = providers.Singleton(LoggerConfig, settings=config)

    embedding_model = providers.Singleton(
        SentenceTransformer,
        model_name_or_path=config.provided.embedding_model_name,
    )

    # Services
    document_converter = providers.Singleton(DocumentConverter)
    file_parser = providers.Singleton(
        FileParser,
        settings=config,
        logger=logger,
        document_converter=document_converter,
    )

    # Infrastructure services
    minio_repository = providers.Singleton(
        MinIORepository,
        endpoint=config.provided.minio_endpoint,
        access_key=config.provided.minio_access_key,
        secret_key=config.provided.minio_secret_key,
        bucket_name=config.provided.minio_bucket_name,
        secure=config.provided.minio_secure,
        settings=config,
    )

    # Elasticsearch client
    @staticmethod
    def get_elasticsearch_client(config: Settings) -> AsyncElasticsearch:
        return AsyncElasticsearch(
            hosts=[
                "".join(
                    (
                        f"{config.elasticsearch_scheme}",
                        "://",
                        f"{config.elasticsearch_host}",
                        ":",
                        f"{config.elasticsearch_port}",
                    )
                )
            ],
        )
    
    elasticsearch_client = providers.Singleton(get_elasticsearch_client, config=config)

    elasticsearch_repository = providers.Singleton(
        ElasticsearchRepository,
        index_name=config.provided.elasticsearch_index_name,
        vector_size=config.provided.embedding_dimension,
        scheme=config.provided.elasticsearch_scheme,
        client=elasticsearch_client,
        logger=logger,
    )
    embedding_service = providers.Singleton(
        SentenceTransformerService,
        embedding_model=embedding_model,
        logger=logger,
    )

    # Application use cases
    upload_document_use_case = providers.Factory(
        UploadDocumentUseCase,
        document_repository=minio_repository,
        vector_repository=elasticsearch_repository,
        embedding_service=embedding_service,
        file_parser=file_parser,
        logger=logger,
    )

    query_documents_use_case = providers.Factory(
        QueryDocumentsUseCase,
        document_repository=minio_repository,
        vector_repository=elasticsearch_repository,
        embedding_service=embedding_service,
        logger=logger,
    )


container = Container()
