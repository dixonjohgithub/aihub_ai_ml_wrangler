"""
File: cache_service.py

Overview:
Redis cache service for managing application cache operations

Purpose:
Provides high-level caching operations with error handling and async support

Dependencies:
- redis: Redis client
- json: Data serialization
- backend.config.redis: Redis configuration

Last Modified: 2025-08-15
Author: Claude
"""

import json
import logging
from typing import Any, Optional, Dict, List
from backend.config.redis import redis_client

logger = logging.getLogger(__name__)

class CacheService:
    """Redis cache service for managing application cache"""

    def __init__(self):
        self.client = redis_client
        self.default_ttl = 3600  # 1 hour default TTL

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, default=str)
            await self.client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            result = await self.client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            result = await self.client.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment numeric value in cache"""
        try:
            result = await self.client.incrby(key, amount)
            return result
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None

    async def set_hash(self, key: str, field_values: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set hash values in cache"""
        try:
            serialized_values = {k: json.dumps(v, default=str) for k, v in field_values.items()}
            await self.client.hset(key, mapping=serialized_values)
            if ttl:
                await self.client.expire(key, ttl)
            return True
        except Exception as e:
            logger.error(f"Cache set_hash error for key {key}: {e}")
            return False

    async def get_hash(self, key: str, field: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get hash values from cache"""
        try:
            if field:
                value = await self.client.hget(key, field)
                if value is None:
                    return None
                return json.loads(value)
            else:
                hash_data = await self.client.hgetall(key)
                if not hash_data:
                    return None
                return {k: json.loads(v) for k, v in hash_data.items()}
        except Exception as e:
            logger.error(f"Cache get_hash error for key {key}: {e}")
            return None

    async def add_to_list(self, key: str, value: Any, max_size: Optional[int] = None) -> bool:
        """Add value to list with optional max size"""
        try:
            serialized_value = json.dumps(value, default=str)
            await self.client.lpush(key, serialized_value)
            if max_size:
                await self.client.ltrim(key, 0, max_size - 1)
            return True
        except Exception as e:
            logger.error(f"Cache add_to_list error for key {key}: {e}")
            return False

    async def get_list(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """Get list values from cache"""
        try:
            values = await self.client.lrange(key, start, end)
            return [json.loads(v) for v in values]
        except Exception as e:
            logger.error(f"Cache get_list error for key {key}: {e}")
            return []

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            keys = await self.client.keys(pattern)
            if keys:
                return await self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear_pattern error for pattern {pattern}: {e}")
            return 0

    async def ping(self) -> bool:
        """Test Redis connection"""
        try:
            await self.client.ping()
            return True
        except Exception as e:
            logger.error(f"Cache ping error: {e}")
            return False