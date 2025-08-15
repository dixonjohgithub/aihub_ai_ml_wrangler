"""
File: deps.py

Overview:
FastAPI dependency injection utilities for common dependencies
like database sessions, Redis clients, and authentication.

Purpose:
Centralize dependency management for cleaner and more maintainable code.

Dependencies:
- redis: Redis client
- sqlalchemy: Database ORM

Last Modified: 2025-08-15
Author: Claude
"""

from typing import AsyncGenerator, Optional
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
import os
import logging

from backend.app.core.database import async_session_maker

logger = logging.getLogger(__name__)

# Global Redis client
_redis_client: Optional[redis.Redis] = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session
    
    Yields:
        AsyncSession: Database session
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_redis_client() -> redis.Redis:
    """
    Dependency for getting Redis client
    
    Returns:
        Redis client instance
    """
    global _redis_client
    
    if _redis_client is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        _redis_client = redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        
        # Test connection
        try:
            await _redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            _redis_client = None
            raise
    
    return _redis_client


async def close_redis():
    """Close Redis connection on app shutdown"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis connection closed")