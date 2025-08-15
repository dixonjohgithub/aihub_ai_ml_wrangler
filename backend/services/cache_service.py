"""
File: cache_service.py

Overview:
Redis caching service for application data

Purpose:
High-level Redis operations with error handling and serialization

Dependencies:
- redis: Redis client
- json: Data serialization

Last Modified: 2025-08-15
Author: Claude
"""

import json
import logging
from typing import Any, Optional
from backend.config.redis import redis_client

logger = logging.getLogger(__name__)

class CacheService:
    """Redis cache service with error handling"""
    
    def __init__(self):
        self.redis = redis_client
    
    async def ping(self) -> bool:
        """Test Redis connection"""
        try:
            await self.redis.ping()
            return True
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False
    
    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set a value in cache with expiration"""
        try:
            serialized_value = json.dumps(value)
            await self.redis.setex(key, expire, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Cache set failed for key {key}: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get failed for key {key}: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete failed for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            result = await self.redis.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Cache exists check failed for key {key}: {e}")
            return False