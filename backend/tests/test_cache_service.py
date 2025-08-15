"""
File: test_cache_service.py

Overview:
Test suite for Redis cache service layer

Purpose:
Tests cache operations and Redis functionality with mocked Redis client

Dependencies:
- pytest: Testing framework
- unittest.mock: Mocking framework

Last Modified: 2025-08-15
Author: Claude
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from backend.services.cache_service import CacheService

@pytest.fixture
def cache_service():
    """Cache service fixture"""
    return CacheService()

@pytest.fixture
def mock_redis_client():
    """Mock Redis client"""
    client = AsyncMock()
    return client

class TestCacheService:
    """Test cases for CacheService"""
    
    @pytest.mark.asyncio
    async def test_get_value_success(self, cache_service):
        """Test successful cache get operation"""
        with patch.object(cache_service, 'client', new=AsyncMock()) as mock_client:
            # Mock Redis get
            test_data = {"key": "value", "number": 42}
            mock_client.get.return_value = json.dumps(test_data)
            
            result = await cache_service.get("test_key")
            
            assert result == test_data
            mock_client.get.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_get_value_not_found(self, cache_service):
        """Test cache get when key doesn't exist"""
        with patch.object(cache_service, 'client', new=AsyncMock()) as mock_client:
            # Mock Redis get returning None
            mock_client.get.return_value = None
            
            result = await cache_service.get("nonexistent_key")
            
            assert result is None
            mock_client.get.assert_called_once_with("nonexistent_key")
    
    @pytest.mark.asyncio
    async def test_get_value_error(self, cache_service):
        """Test cache get with Redis error"""
        with patch.object(cache_service, 'client', new=AsyncMock()) as mock_client:
            # Mock Redis get raising exception
            mock_client.get.side_effect = Exception("Redis connection error")
            
            result = await cache_service.get("test_key")
            
            assert result is None
            mock_client.get.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_set_value_success(self, cache_service):
        """Test successful cache set operation"""
        with patch.object(cache_service, 'client', new=AsyncMock()) as mock_client:
            # Mock Redis setex
            mock_client.setex.return_value = True
            
            test_data = {"key": "value", "number": 42}
            result = await cache_service.set("test_key", test_data, ttl=1800)
            
            assert result is True
            mock_client.setex.assert_called_once_with(
                "test_key", 
                1800, 
                json.dumps(test_data, default=str)
            )
    
    @pytest.mark.asyncio
    async def test_set_value_default_ttl(self, cache_service):
        """Test cache set with default TTL"""
        with patch.object(cache_service, 'client', new=AsyncMock()) as mock_client:
            # Mock Redis setex
            mock_client.setex.return_value = True
            
            test_data = "simple_string"
            result = await cache_service.set("test_key", test_data)
            
            assert result is True
            mock_client.setex.assert_called_once_with(
                "test_key", 
                cache_service.default_ttl, 
                json.dumps(test_data, default=str)
            )
    
    @pytest.mark.asyncio
    async def test_set_value_error(self, cache_service):
        """Test cache set with Redis error"""
        with patch.object(cache_service, 'client', new=AsyncMock()) as mock_client:
            # Mock Redis setex raising exception
            mock_client.setex.side_effect = Exception("Redis connection error")
            
            result = await cache_service.set("test_key", "test_value")
            
            assert result is False
            mock_client.setex.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_value_success(self, cache_service):
        """Test successful cache delete operation"""
        with patch.object(cache_service, 'client', new=AsyncMock()) as mock_client:
            # Mock Redis delete returning 1 (key was deleted)
            mock_client.delete.return_value = 1
            
            result = await cache_service.delete("test_key")
            
            assert result is True
            mock_client.delete.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_delete_value_not_found(self, cache_service):
        """Test cache delete when key doesn't exist"""
        with patch.object(cache_service, 'client', new=AsyncMock()) as mock_client:
            # Mock Redis delete returning 0 (key not found)
            mock_client.delete.return_value = 0
            
            result = await cache_service.delete("nonexistent_key")
            
            assert result is False
            mock_client.delete.assert_called_once_with("nonexistent_key")
    
    @pytest.mark.asyncio
    async def test_exists_key_found(self, cache_service):
        """Test cache exists when key exists"""
        with patch.object(cache_service, 'client', new=AsyncMock()) as mock_client:
            # Mock Redis exists returning 1
            mock_client.exists.return_value = 1
            
            result = await cache_service.exists("test_key")
            
            assert result is True
            mock_client.exists.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_exists_key_not_found(self, cache_service):
        """Test cache exists when key doesn't exist"""
        with patch.object(cache_service, 'client', new=AsyncMock()) as mock_client:
            # Mock Redis exists returning 0
            mock_client.exists.return_value = 0
            
            result = await cache_service.exists("nonexistent_key")
            
            assert result is False
            mock_client.exists.assert_called_once_with("nonexistent_key")
    
    @pytest.mark.asyncio
    async def test_increment_value(self, cache_service):
        """Test cache increment operation"""
        with patch.object(cache_service, 'client', new=AsyncMock()) as mock_client:
            # Mock Redis incrby returning new value
            mock_client.incrby.return_value = 5
            
            result = await cache_service.increment("counter_key", 2)
            
            assert result == 5
            mock_client.incrby.assert_called_once_with("counter_key", 2)
    
    @pytest.mark.asyncio
    async def test_set_hash_success(self, cache_service):
        """Test successful hash set operation"""
        with patch.object(cache_service, 'client', new=AsyncMock()) as mock_client:
            # Mock Redis hset and expire
            mock_client.hset.return_value = 2
            mock_client.expire.return_value = True
            
            test_data = {"field1": "value1", "field2": 42}
            result = await cache_service.set_hash("hash_key", test_data, ttl=1800)
            
            assert result is True
            mock_client.hset.assert_called_once()
            mock_client.expire.assert_called_once_with("hash_key", 1800)
    
    @pytest.mark.asyncio
    async def test_get_hash_all_fields(self, cache_service):
        """Test get all hash fields"""
        with patch.object(cache_service, 'client', new=AsyncMock()) as mock_client:
            # Mock Redis hgetall
            mock_redis_data = {
                "field1": json.dumps("value1"),
                "field2": json.dumps(42)
            }
            mock_client.hgetall.return_value = mock_redis_data
            
            result = await cache_service.get_hash("hash_key")
            
            expected = {"field1": "value1", "field2": 42}
            assert result == expected
            mock_client.hgetall.assert_called_once_with("hash_key")
    
    @pytest.mark.asyncio
    async def test_get_hash_single_field(self, cache_service):
        """Test get single hash field"""
        with patch.object(cache_service, 'client', new=AsyncMock()) as mock_client:
            # Mock Redis hget
            mock_client.hget.return_value = json.dumps("value1")
            
            result = await cache_service.get_hash("hash_key", "field1")
            
            assert result == "value1"
            mock_client.hget.assert_called_once_with("hash_key", "field1")
    
    @pytest.mark.asyncio
    async def test_add_to_list_with_max_size(self, cache_service):
        """Test adding to list with max size limit"""
        with patch.object(cache_service, 'client', new=AsyncMock()) as mock_client:
            # Mock Redis lpush and ltrim
            mock_client.lpush.return_value = 1
            mock_client.ltrim.return_value = True
            
            result = await cache_service.add_to_list("list_key", "new_item", max_size=10)
            
            assert result is True
            mock_client.lpush.assert_called_once_with("list_key", json.dumps("new_item", default=str))
            mock_client.ltrim.assert_called_once_with("list_key", 0, 9)
    
    @pytest.mark.asyncio
    async def test_get_list_values(self, cache_service):
        """Test get list values"""
        with patch.object(cache_service, 'client', new=AsyncMock()) as mock_client:
            # Mock Redis lrange
            mock_redis_data = [
                json.dumps("item1"),
                json.dumps("item2"),
                json.dumps(42)
            ]
            mock_client.lrange.return_value = mock_redis_data
            
            result = await cache_service.get_list("list_key", 0, 2)
            
            expected = ["item1", "item2", 42]
            assert result == expected
            mock_client.lrange.assert_called_once_with("list_key", 0, 2)
    
    @pytest.mark.asyncio
    async def test_clear_pattern(self, cache_service):
        """Test clear keys by pattern"""
        with patch.object(cache_service, 'client', new=AsyncMock()) as mock_client:
            # Mock Redis keys and delete
            mock_client.keys.return_value = ["key1", "key2", "key3"]
            mock_client.delete.return_value = 3
            
            result = await cache_service.clear_pattern("test:*")
            
            assert result == 3
            mock_client.keys.assert_called_once_with("test:*")
            mock_client.delete.assert_called_once_with("key1", "key2", "key3")
    
    @pytest.mark.asyncio
    async def test_ping_success(self, cache_service):
        """Test successful Redis ping"""
        with patch.object(cache_service, 'client', new=AsyncMock()) as mock_client:
            # Mock Redis ping
            mock_client.ping.return_value = True
            
            result = await cache_service.ping()
            
            assert result is True
            mock_client.ping.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_ping_error(self, cache_service):
        """Test Redis ping with error"""
        with patch.object(cache_service, 'client', new=AsyncMock()) as mock_client:
            # Mock Redis ping raising exception
            mock_client.ping.side_effect = Exception("Connection failed")
            
            result = await cache_service.ping()
            
            assert result is False
            mock_client.ping.assert_called_once()