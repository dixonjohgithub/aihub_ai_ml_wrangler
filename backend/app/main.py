"""
File: main.py

Overview:
FastAPI application entry point for the AI Hub AI/ML Wrangler backend.

Purpose:
Configures and initializes the FastAPI application with database connections,
middleware, routing, and background task integration.

Dependencies:
- fastapi: Web framework
- app.database: Database connections
- app.config: Configuration settings
- app.services: Service layer

Last Modified: 2025-08-15
Author: Claude
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .database import check_database_connection_async, create_tables_async
from .services.cache_service import cache_service
from .services.database_service import database_service

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.app.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting AI Hub AI/ML Wrangler backend...")
    
    # Initialize Redis connection
    try:
        await cache_service.connect()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        # Continue without Redis for now
    
    # Check database connection
    try:
        db_connected = await check_database_connection_async()
        if db_connected:
            logger.info("Database connection verified")
        else:
            logger.error("Database connection failed")
    except Exception as e:
        logger.error(f"Database connection error: {e}")
    
    # Initialize database tables
    try:
        await create_tables_async()
        logger.info("Database tables initialized")
    except Exception as e:
        logger.warning(f"Database table initialization error: {e}")
    
    logger.info("Backend startup completed")
    
    yield
    
    # Cleanup
    logger.info("Shutting down backend...")
    
    try:
        await cache_service.disconnect()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.error(f"Error closing Redis connection: {e}")
    
    logger.info("Backend shutdown completed")


# Create FastAPI application
app = FastAPI(
    title=settings.app.title,
    description=settings.app.description,
    version=settings.app.version,
    docs_url=settings.app.docs_url,
    redoc_url=settings.app.redoc_url,
    lifespan=lifespan,
    debug=settings.app.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    try:
        # Check database
        db_health = await database_service.health_check()
        
        # Check Redis
        redis_health = await cache_service.ping()
        
        # Overall status
        status = "healthy"
        if not db_health.get("sync_connection") or not db_health.get("async_connection"):
            status = "unhealthy"
        if not redis_health:
            status = "degraded" if status == "healthy" else "unhealthy"
        
        return {
            "status": status,
            "timestamp": "2025-08-15T17:45:00Z",
            "version": settings.app.version,
            "database": {
                "status": "healthy" if db_health.get("sync_connection") and db_health.get("async_connection") else "unhealthy",
                "tables_exist": db_health.get("tables_exist", False)
            },
            "redis": {
                "status": "healthy" if redis_health else "unhealthy"
            },
            "environment": {
                "debug": settings.app.debug,
                "api_prefix": settings.app.api_prefix
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


# Database management endpoints
@app.get("/admin/database/info")
async def get_database_info() -> Dict[str, Any]:
    """Get database information."""
    try:
        db_health = await database_service.health_check()
        table_info = await database_service.get_table_info()
        size_info = await database_service.get_database_size()
        
        return {
            "health": db_health,
            "tables": table_info,
            "size": size_info
        }
        
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get database info")


@app.post("/admin/database/initialize")
async def initialize_database() -> Dict[str, Any]:
    """Initialize database tables."""
    try:
        result = await database_service.initialize_database()
        
        if result["success"]:
            return {"message": "Database initialized successfully", "result": result}
        else:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise HTTPException(status_code=500, detail="Database initialization failed")


@app.post("/admin/database/reset")
async def reset_database() -> Dict[str, Any]:
    """Reset database (drop and recreate all tables)."""
    try:
        result = await database_service.reset_database()
        
        if result["success"]:
            return {"message": "Database reset successfully", "result": result}
        else:
            raise HTTPException(status_code=500, detail=f"Database reset failed: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        raise HTTPException(status_code=500, detail="Database reset failed")


# Redis management endpoints
@app.get("/admin/redis/info")
async def get_redis_info() -> Dict[str, Any]:
    """Get Redis information."""
    try:
        redis_info = await cache_service.get_info()
        ping_result = await cache_service.ping()
        
        return {
            "status": "healthy" if ping_result else "unhealthy",
            "info": redis_info
        }
        
    except Exception as e:
        logger.error(f"Failed to get Redis info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Redis info")


# Root endpoint
@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {
        "message": "AI Hub AI/ML Wrangler Backend API",
        "version": settings.app.version,
        "docs": settings.app.docs_url,
        "health": "/health"
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.app.debug,
        log_level="debug" if settings.app.debug else "info"
    )