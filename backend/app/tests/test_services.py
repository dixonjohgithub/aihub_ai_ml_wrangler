"""
File: tests/test_services.py

Overview:
Tests for service layer components including database and cache services.

Purpose:
Tests for DatabaseService and CacheService functionality including
health checks, connection management, and data operations.

Dependencies:
- pytest: Testing framework
- app.services: Service classes
- app.database: Database connections

Last Modified: 2025-08-15
Author: Claude
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.database_service import DatabaseService
from app.services.cache_service import CacheService


class TestDatabaseService:
    """Test DatabaseService functionality."""
    
    @pytest.fixture
    def db_service(self):
        """Create database service instance."""
        return DatabaseService()
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, db_service):
        """Test successful health check."""
        with patch('app.services.database_service.check_database_connection', return_value=True), \
             patch('app.services.database_service.check_database_connection_async', return_value=True), \
             patch.object(db_service, 'check_tables_exist', return_value=True), \
             patch('app.services.database_service.get_database_info', return_value={"pool_size": 10}):
            
            result = await db_service.health_check()
            
            assert result["status"] == "healthy"
            assert result["sync_connection"] is True
            assert result["async_connection"] is True
            assert result["tables_exist"] is True
            assert result["error"] is None
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, db_service):
        """Test health check with connection failure."""
        with patch('app.services.database_service.check_database_connection', return_value=False), \
             patch('app.services.database_service.check_database_connection_async', return_value=False):
            
            result = await db_service.health_check()
            
            assert result["status"] == "unhealthy"
            assert result["sync_connection"] is False
            assert result["async_connection"] is False
    
    @pytest.mark.asyncio
    async def test_check_tables_exist_mock(self, db_service):
        """Test check_tables_exist with mocked database."""
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = ["users", "datasets", "jobs"]
        
        with patch('app.services.database_service.async_engine') as mock_engine:
            mock_conn = AsyncMock()
            mock_conn.sync_connection = MagicMock()
            mock_engine.connect.return_value.__aenter__.return_value = mock_conn
            
            with patch('app.services.database_service.inspect', return_value=mock_inspector):
                result = await db_service.check_tables_exist()
                
                assert result is True
    
    @pytest.mark.asyncio
    async def test_check_tables_exist_missing_tables(self, db_service):
        """Test check_tables_exist with missing tables."""
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = ["users"]  # Missing datasets and jobs
        
        with patch('app.services.database_service.async_engine') as mock_engine:
            mock_conn = AsyncMock()
            mock_conn.sync_connection = MagicMock()
            mock_engine.connect.return_value.__aenter__.return_value = mock_conn
            
            with patch('app.services.database_service.inspect', return_value=mock_inspector):
                result = await db_service.check_tables_exist()
                
                assert result is False
    
    @pytest.mark.asyncio
    async def test_initialize_database_success(self, db_service):
        """Test successful database initialization."""
        with patch('app.services.database_service.create_tables_async') as mock_create, \
             patch.object(db_service, 'check_tables_exist', return_value=True):
            
            result = await db_service.initialize_database()
            
            assert result["success"] is True
            assert result["tables_created"] is True
            assert result["error"] is None
            mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_database_failure(self, db_service):
        """Test database initialization failure."""
        with patch('app.services.database_service.create_tables_async', side_effect=Exception("DB Error")):
            
            result = await db_service.initialize_database()
            
            assert result["success"] is False
            assert result["tables_created"] is False
            assert "DB Error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_reset_database_success(self, db_service):
        """Test successful database reset."""
        with patch('app.services.database_service.drop_tables_async') as mock_drop, \
             patch('app.services.database_service.create_tables_async') as mock_create, \
             patch.object(db_service, 'check_tables_exist', return_value=True):
            
            result = await db_service.reset_database()
            
            assert result["success"] is True
            assert result["tables_dropped"] is True
            assert result["tables_created"] is True
            mock_drop.assert_called_once()
            mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_table_info_success(self, db_service):
        """Test getting table information."""
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = ["users", "datasets"]
        mock_inspector.get_columns.return_value = [
            {"name": "id", "type": "UUID", "nullable": False, "primary_key": True},
            {"name": "email", "type": "VARCHAR", "nullable": False}
        ]
        mock_inspector.get_indexes.return_value = [{"name": "ix_users_email"}]
        mock_inspector.get_foreign_keys.return_value = []
        
        with patch('app.services.database_service.async_engine') as mock_engine:
            mock_conn = AsyncMock()
            mock_conn.sync_connection = MagicMock()
            mock_engine.connect.return_value.__aenter__.return_value = mock_conn
            
            with patch('app.services.database_service.inspect', return_value=mock_inspector):
                result = await db_service.get_table_info()
                
                assert result["total_tables"] == 2
                assert "users" in result["tables"]
                assert "datasets" in result["tables"]
                assert len(result["tables"]["users"]["columns"]) == 2
    
    def test_get_connection_info(self, db_service):
        """Test getting connection information."""
        with patch('app.services.database_service.get_database_info', return_value={"pool_size": 10}):
            result = db_service.get_connection_info()
            assert "pool_size" in result


class TestCacheService:
    """Test CacheService functionality."""
    
    @pytest.fixture
    def cache_service(self):
        """Create cache service instance."""
        return CacheService()
    
    @pytest.mark.asyncio
    async def test_connect_success(self, cache_service):
        """Test successful Redis connection."""
        with patch('redis.asyncio.ConnectionPool.from_url') as mock_pool, \
             patch('redis.asyncio.Redis') as mock_redis_class:
            
            mock_redis = AsyncMock()
            mock_redis.ping.return_value = True
            mock_redis_class.return_value = mock_redis
            
            await cache_service.connect()
            
            assert cache_service._redis is not None
            mock_redis.ping.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connect_failure(self, cache_service):
        """Test Redis connection failure."""
        with patch('redis.asyncio.ConnectionPool.from_url') as mock_pool, \
             patch('redis.asyncio.Redis') as mock_redis_class:
            
            mock_redis = AsyncMock()
            mock_redis.ping.side_effect = Exception("Connection failed")
            mock_redis_class.return_value = mock_redis
            
            with pytest.raises(Exception):
                await cache_service.connect()
    
    @pytest.mark.asyncio
    async def test_disconnect(self, cache_service):
        """Test Redis disconnection."""
        mock_redis = AsyncMock()
        cache_service._redis = mock_redis
        
        await cache_service.disconnect()
        
        mock_redis.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_ping_success(self, cache_service):
        """Test successful ping."""
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        cache_service._redis = mock_redis
        
        result = await cache_service.ping()
        
        assert result is True
        mock_redis.ping.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_ping_failure(self, cache_service):
        """Test ping failure."""
        mock_redis = AsyncMock()
        mock_redis.ping.side_effect = Exception("Ping failed")
        cache_service._redis = mock_redis
        
        result = await cache_service.ping()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_ping_no_connection(self, cache_service):
        """Test ping with no Redis connection."""
        cache_service._redis = None
        
        result = await cache_service.ping()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_set_get_success(self, cache_service):
        """Test successful set and get operations."""
        mock_redis = AsyncMock()
        mock_redis.set.return_value = True
        mock_redis.setex.return_value = True
        mock_redis.get.return_value = '{"key": "value"}'
        cache_service._redis = mock_redis
        
        # Test set without expiration
        result = await cache_service.set("test_key", {"key": "value"})
        assert result is True
        mock_redis.set.assert_called_once()
        
        # Test set with expiration
        result = await cache_service.set("test_key", {"key": "value"}, expire=60)
        assert result is True
        mock_redis.setex.assert_called_once()
        
        # Test get
        result = await cache_service.get("test_key")
        assert result == {"key": "value"}
        mock_redis.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_not_found(self, cache_service):
        """Test get operation with key not found."""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None
        cache_service._redis = mock_redis
        
        result = await cache_service.get("nonexistent_key", default="default_value")
        
        assert result == "default_value"
    
    @pytest.mark.asyncio
    async def test_delete_success(self, cache_service):
        """Test successful delete operation."""
        mock_redis = AsyncMock()
        mock_redis.delete.return_value = 1  # 1 key deleted
        cache_service._redis = mock_redis
        
        result = await cache_service.delete("test_key")
        
        assert result is True
        mock_redis.delete.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_delete_not_found(self, cache_service):
        """Test delete operation with key not found."""
        mock_redis = AsyncMock()
        mock_redis.delete.return_value = 0  # 0 keys deleted
        cache_service._redis = mock_redis
        
        result = await cache_service.delete("nonexistent_key")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_exists_success(self, cache_service):
        """Test exists operation."""
        mock_redis = AsyncMock()
        mock_redis.exists.return_value = 1  # Key exists
        cache_service._redis = mock_redis
        
        result = await cache_service.exists("test_key")
        
        assert result is True
        mock_redis.exists.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_exists_not_found(self, cache_service):
        """Test exists operation with key not found."""
        mock_redis = AsyncMock()
        mock_redis.exists.return_value = 0  # Key doesn't exist
        cache_service._redis = mock_redis
        
        result = await cache_service.exists("nonexistent_key")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_expire_success(self, cache_service):
        """Test expire operation."""
        mock_redis = AsyncMock()
        mock_redis.expire.return_value = 1  # Expiration set
        cache_service._redis = mock_redis
        
        result = await cache_service.expire("test_key", 60)
        
        assert result is True
        mock_redis.expire.assert_called_once_with("test_key", 60)
    
    @pytest.mark.asyncio
    async def test_ttl_success(self, cache_service):
        """Test TTL operation."""
        mock_redis = AsyncMock()
        mock_redis.ttl.return_value = 60  # 60 seconds remaining
        cache_service._redis = mock_redis
        
        result = await cache_service.ttl("test_key")
        
        assert result == 60
        mock_redis.ttl.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_keys_success(self, cache_service):
        """Test keys operation."""
        mock_redis = AsyncMock()
        mock_redis.keys.return_value = ["key1", "key2", "key3"]
        cache_service._redis = mock_redis
        
        result = await cache_service.keys("test:*")
        
        assert result == ["key1", "key2", "key3"]
        mock_redis.keys.assert_called_once_with("test:*")
    
    @pytest.mark.asyncio
    async def test_flush_db_success(self, cache_service):
        """Test flush database operation."""
        mock_redis = AsyncMock()
        mock_redis.flushdb.return_value = True
        cache_service._redis = mock_redis
        
        result = await cache_service.flush_db()
        
        assert result is True
        mock_redis.flushdb.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_info_success(self, cache_service):
        """Test get info operation."""
        mock_redis = AsyncMock()
        mock_redis.info.return_value = {"redis_version": "7.0.0", "connected_clients": 1}
        cache_service._redis = mock_redis
        
        result = await cache_service.get_info()
        
        assert "redis_version" in result
        assert "connected_clients" in result
        mock_redis.info.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_operations_without_connection(self, cache_service):
        """Test operations without Redis connection."""
        cache_service._redis = None
        
        # All operations should handle missing connection gracefully
        assert await cache_service.set("key", "value") is False
        assert await cache_service.get("key") is None
        assert await cache_service.delete("key") is False
        assert await cache_service.exists("key") is False
        assert await cache_service.expire("key", 60) is False
        assert await cache_service.ttl("key") == -2
        assert await cache_service.keys("*") == []
        assert await cache_service.flush_db() is False
        assert await cache_service.get_info() == {}