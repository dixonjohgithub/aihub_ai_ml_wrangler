"""
File: services/cache_service.py

Overview:
Redis cache service for managing cached data and session storage.

Purpose:
Provides a high-level interface for Redis operations including caching,
session management, and temporary data storage.

Dependencies:
- redis: Redis client library
- json: JSON serialization
- typing: Type hints

Last Modified: 2025-08-15
Author: Claude
"""

import json
import logging
from typing import Any, Optional, Union, Dict, List
from datetime import timedelta

import redis.asyncio as redis
from redis.exceptions import RedisError, ConnectionError

from ..config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Redis cache service for data caching and session management."""
    
    def __init__(self):
        """Initialize Redis connection."""
        self._redis: Optional[redis.Redis] = None
        self._connection_pool: Optional[redis.ConnectionPool] = None
    
    async def connect(self) -> None:
        """Establish Redis connection."""
        try:
            self._connection_pool = redis.ConnectionPool.from_url(
                settings.redis.redis_url,
                max_connections=settings.redis.max_connections,
                retry_on_timeout=settings.redis.retry_on_timeout,
                decode_responses=True
            )
            
            self._redis = redis.Redis(connection_pool=self._connection_pool)
            
            # Test connection
            await self._redis.ping()
            logger.info("Redis connection established successfully")
            
        except ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to Redis: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            logger.info("Redis connection closed")
    
    async def ping(self) -> bool:
        """
        Check Redis connection status.
        
        Returns:
            bool: True if connection is healthy, False otherwise
        """
        try:
            if not self._redis:
                return False
            await self._redis.ping()
            return True
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[Union[int, timedelta]] = None,
        serialize: bool = True
    ) -> bool:
        """
        Set a value in Redis.
        
        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time in seconds or timedelta
            serialize: Whether to serialize value as JSON
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self._redis:
                logger.warning("Redis not connected")
                return False
            
            # Serialize value if needed
            if serialize and not isinstance(value, str):
                value = json.dumps(value, default=str)
            
            # Set value with optional expiration
            if expire:
                if isinstance(expire, timedelta):
                    expire = int(expire.total_seconds())
                await self._redis.setex(key, expire, value)
            else:
                await self._redis.set(key, value)
            
            logger.debug(f"Cached value for key: {key}")
            return True
            
        except RedisError as e:
            logger.error(f"Redis set error for key '{key}': {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error setting cache key '{key}': {e}")
            return False
    
    async def get(
        self,
        key: str,
        deserialize: bool = True,
        default: Any = None
    ) -> Any:
        """
        Get a value from Redis.
        
        Args:
            key: Cache key
            deserialize: Whether to deserialize JSON value
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        try:
            if not self._redis:
                logger.warning("Redis not connected")
                return default
            
            value = await self._redis.get(key)
            
            if value is None:
                return default
            
            # Deserialize if needed
            if deserialize and isinstance(value, str):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    # Return as string if not valid JSON
                    pass
            
            logger.debug(f"Retrieved cached value for key: {key}")
            return value
            
        except RedisError as e:
            logger.error(f"Redis get error for key '{key}': {e}")
            return default
        except Exception as e:
            logger.error(f"Unexpected error getting cache key '{key}': {e}")
            return default
    
    async def delete(self, key: str) -> bool:
        """
        Delete a key from Redis.
        
        Args:
            key: Cache key to delete
            
        Returns:
            bool: True if key was deleted, False otherwise
        """
        try:
            if not self._redis:
                logger.warning("Redis not connected")
                return False
            
            result = await self._redis.delete(key)
            logger.debug(f"Deleted cache key: {key}")
            return bool(result)
            
        except RedisError as e:
            logger.error(f"Redis delete error for key '{key}': {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting cache key '{key}': {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis.
        
        Args:
            key: Cache key to check
            
        Returns:
            bool: True if key exists, False otherwise
        """
        try:
            if not self._redis:
                return False
            
            result = await self._redis.exists(key)
            return bool(result)
            
        except RedisError as e:
            logger.error(f"Redis exists error for key '{key}': {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking cache key '{key}': {e}")
            return False
    
    async def expire(self, key: str, seconds: Union[int, timedelta]) -> bool:
        """
        Set expiration time for a key.
        
        Args:
            key: Cache key
            seconds: Expiration time in seconds or timedelta
            
        Returns:
            bool: True if expiration was set, False otherwise
        """
        try:
            if not self._redis:
                return False
            
            if isinstance(seconds, timedelta):
                seconds = int(seconds.total_seconds())
            
            result = await self._redis.expire(key, seconds)
            return bool(result)
            
        except RedisError as e:
            logger.error(f"Redis expire error for key '{key}': {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error setting expiration for key '{key}': {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """
        Get time to live for a key.
        
        Args:
            key: Cache key
            
        Returns:
            int: TTL in seconds, -1 if no expiration, -2 if key doesn't exist
        """
        try:
            if not self._redis:
                return -2
            
            return await self._redis.ttl(key)
            
        except RedisError as e:
            logger.error(f"Redis TTL error for key '{key}': {e}")
            return -2
        except Exception as e:
            logger.error(f"Unexpected error getting TTL for key '{key}': {e}")
            return -2
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """
        Get keys matching a pattern.
        
        Args:
            pattern: Pattern to match (default: all keys)
            
        Returns:
            List of matching keys
        """
        try:
            if not self._redis:
                return []
            
            keys = await self._redis.keys(pattern)
            return keys if keys else []
            
        except RedisError as e:
            logger.error(f"Redis keys error for pattern '{pattern}': {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting keys for pattern '{pattern}': {e}")
            return []
    
    async def flush_db(self) -> bool:
        """
        Clear all keys from the current database.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self._redis:
                return False
            
            await self._redis.flushdb()
            logger.warning("Redis database flushed")
            return True
            
        except RedisError as e:
            logger.error(f"Redis flush error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error flushing Redis: {e}")
            return False
    
    async def get_info(self) -> Dict[str, Any]:
        """
        Get Redis server information.
        
        Returns:
            dict: Redis server information
        """
        try:
            if not self._redis:
                return {}
            
            info = await self._redis.info()
            return info
            
        except RedisError as e:
            logger.error(f"Redis info error: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error getting Redis info: {e}")
            return {}


# Global cache service instance
cache_service = CacheService()