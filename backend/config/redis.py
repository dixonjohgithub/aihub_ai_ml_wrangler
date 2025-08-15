"""
File: redis.py

Overview:
Redis configuration for caching and task queue backend

Purpose:
Provides Redis client setup with connection pooling and async support

Dependencies:
- redis: Redis Python client
- python-dotenv: Environment variable management

Last Modified: 2025-08-15
Author: Claude
"""

import os
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create async Redis client
redis_client = redis.from_url(
    REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    max_connections=10,
    retry_on_timeout=True,
)

async def get_redis():
    """Get Redis client instance"""
    return redis_client

async def ping_redis():
    """Test Redis connection"""
    try:
        await redis_client.ping()
        return True
    except Exception:
        return False