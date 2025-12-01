from src.infra.config.di import container


async def upload_document_use_case():
    """Dependency for upload document use case."""
    return container.upload_document_use_case()

async def logger_config():
    """Dependency for logger configuration."""
    return container.logger().get_logger()

async def settings_config():
    """Dependency for settings configuration."""
    return container.config()

async def query_documents_use_case():
    """Dependency for query documents use case."""
    return container.query_documents_use_case()