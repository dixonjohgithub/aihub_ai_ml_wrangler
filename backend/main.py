"""
File: main.py

Overview:
FastAPI application entry point for the AI Hub ML Wrangler backend

Purpose:
Configures and runs the FastAPI application with database and cache health endpoints

Dependencies:
- fastapi: Web framework
- uvicorn: ASGI server
- backend.config: Configuration modules

Last Modified: 2025-08-15
Author: Claude
"""

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from backend.config.database import get_db, engine
from backend.config.redis import ping_redis
from backend.services.cache_service import CacheService
from backend.services.database_service import DatabaseService
from sqlalchemy.ext.asyncio import AsyncSession
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Hub ML Wrangler Backend",
    description="Backend infrastructure for ML data analysis and processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize services
cache_service = CacheService()
db_service = DatabaseService()

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting AI Hub ML Wrangler Backend...")
    logger.info("Database and Redis services initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down AI Hub ML Wrangler Backend...")
    await engine.dispose()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Hub ML Wrangler Backend",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "services": {
            "database": "unknown",
            "redis": "unknown",
            "celery": "unknown"
        }
    }
    
    try:
        # Check database connection
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Redis connection
    redis_healthy = await ping_redis()
    health_status["services"]["redis"] = "healthy" if redis_healthy else "unhealthy"
    if not redis_healthy:
        health_status["status"] = "degraded"
    
    # Check Celery (simplified check)
    try:
        from backend.config.celery import celery_app
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        if stats:
            health_status["services"]["celery"] = "healthy"
        else:
            health_status["services"]["celery"] = "no workers"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["celery"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)

@app.get("/health/database")
async def database_health(db: AsyncSession = Depends(get_db)):
    """Database-specific health check"""
    try:
        await db.execute("SELECT 1")
        return {"status": "healthy", "message": "Database connection successful"}
    except Exception as e:
        return JSONResponse(
            content={"status": "unhealthy", "error": str(e)},
            status_code=503
        )

@app.get("/health/redis")
async def redis_health():
    """Redis-specific health check"""
    try:
        redis_healthy = await cache_service.ping()
        if redis_healthy:
            return {"status": "healthy", "message": "Redis connection successful"}
        else:
            return JSONResponse(
                content={"status": "unhealthy", "error": "Redis ping failed"},
                status_code=503
            )
    except Exception as e:
        return JSONResponse(
            content={"status": "unhealthy", "error": str(e)},
            status_code=503
        )

@app.get("/health/celery")
async def celery_health():
    """Celery-specific health check"""
    try:
        from backend.config.celery import celery_app
        inspect = celery_app.control.inspect()
        
        # Get worker stats
        stats = inspect.stats()
        active_tasks = inspect.active()
        
        if not stats:
            return JSONResponse(
                content={"status": "unhealthy", "error": "No Celery workers available"},
                status_code=503
            )
        
        return {
            "status": "healthy",
            "message": "Celery workers are active",
            "workers": list(stats.keys()) if stats else [],
            "active_tasks_count": sum(len(tasks) for tasks in active_tasks.values()) if active_tasks else 0
        }
    except Exception as e:
        return JSONResponse(
            content={"status": "unhealthy", "error": str(e)},
            status_code=503
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )