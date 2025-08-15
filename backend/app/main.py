"""
File: main.py

Overview:
FastAPI application entry point for AI Hub AI/ML Wrangler backend

Purpose:
Initialize and configure the FastAPI application with middleware, CORS, and routing

Dependencies:
- FastAPI: Web framework
- uvicorn: ASGI server

Last Modified: 2025-08-15
Author: Claude
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

# Add app directory to Python path
sys.path.append(str(Path(__file__).parent))

from api.router import api_router
from core.config import settings
from core.logging import setup_logging, get_logger
from core.exceptions import (
    MLWranglerException,
    ml_wrangler_exception_handler,
    general_exception_handler
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    setup_logging("DEBUG" if settings.DEBUG else "INFO")
    logger = get_logger(__name__)
    logger.info("Starting AI Hub AI/ML Wrangler backend...")
    yield
    # Shutdown
    logger.info("Shutting down AI Hub AI/ML Wrangler backend...")


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="AI Hub AI/ML Wrangler API",
        description="Statistical data imputation and analysis tool with AI-powered recommendations",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add exception handlers
    app.add_exception_handler(MLWranglerException, ml_wrangler_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    # Include API router
    app.include_router(api_router, prefix="/api")
    
    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )