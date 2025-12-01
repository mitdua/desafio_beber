"""Main module for the application."""

import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.infra.config.di import container
from src.infra.routes import documents_router, query_router
from src.infra.routes.health import router as health_router

# Initialize DI container
logger = container.logger().get_logger()
settings = container.config()



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting RAG API...")
    
    # Initialize Elasticsearch index
    es_repo = container.elasticsearch_repository()
    await es_repo.initialize_collection()
    logger.info("Elasticsearch index initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down RAG API...")
    await es_repo.close()
    logger.info("Elasticsearch client closed")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wire dependencies
container.wire(modules=[
    "src.infra.routes.documents",
    "src.infra.routes.query",
])

# Include routers
app.include_router(health_router)
app.include_router(documents_router)
app.include_router(query_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.api_title,
        "version": settings.api_version,
        "endpoints": {
            "health": "/health",
            "upload": "/documents",
            "query": "/query",
            "docs": "/docs",
        },
    }


if __name__ == "__main__":
    settings = container.config()    
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development",
    )