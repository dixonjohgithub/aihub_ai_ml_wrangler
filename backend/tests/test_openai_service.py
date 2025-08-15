"""
Test suite for OpenAI service integration
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import json

from backend.app.services.openai_service import (
    OpenAIService,
    RateLimiter,
    CostTracker,
    APIUsageMetrics,
    ModelType
)


class TestRateLimiter:
    """Test rate limiting functionality"""
    
    @pytest.mark.asyncio
    async def test_rate_limit_requests(self):
        """Test request rate limiting"""
        limiter = RateLimiter(max_requests_per_minute=2, max_tokens_per_minute=1000)
        
        # First request should pass
        can_proceed, wait_time = await limiter.check_rate_limit(100)
        assert can_proceed is True
        assert wait_time == 0.0
        
        # Second request should pass
        can_proceed, wait_time = await limiter.check_rate_limit(100)
        assert can_proceed is True
        assert wait_time == 0.0
        
        # Third request should be rate limited
        can_proceed, wait_time = await limiter.check_rate_limit(100)
        assert can_proceed is False
        assert wait_time > 0
    
    @pytest.mark.asyncio
    async def test_rate_limit_tokens(self):
        """Test token rate limiting"""
        limiter = RateLimiter(max_requests_per_minute=100, max_tokens_per_minute=500)
        
        # Request with 400 tokens should pass
        can_proceed, wait_time = await limiter.check_rate_limit(400)
        assert can_proceed is True
        
        # Request with 200 tokens should fail (exceeds limit)
        can_proceed, wait_time = await limiter.check_rate_limit(200)
        assert can_proceed is False
        assert wait_time > 0
    
    @pytest.mark.asyncio
    async def test_rate_limit_cleanup(self):
        """Test that old timestamps are cleaned up"""
        limiter = RateLimiter(max_requests_per_minute=1, max_tokens_per_minute=1000)
        
        # Add a request
        await limiter.check_rate_limit(100)
        
        # Manually set timestamp to old value
        limiter.request_timestamps[0] = datetime.now() - timedelta(minutes=2)
        
        # Next request should pass after cleanup
        can_proceed, wait_time = await limiter.check_rate_limit(100)
        assert can_proceed is True


class TestCostTracker:
    """Test cost tracking functionality"""
    
    def test_calculate_cost_gpt4(self):
        """Test cost calculation for GPT-4"""
        tracker = CostTracker()
        
        cost = tracker.calculate_cost(
            ModelType.GPT_4.value,
            prompt_tokens=1000,
            completion_tokens=500
        )
        
        # GPT-4: $0.03 per 1K prompt tokens, $0.06 per 1K completion tokens
        expected_cost = (1000/1000 * 0.03) + (500/1000 * 0.06)
        assert cost == expected_cost
    
    def test_calculate_cost_gpt35(self):
        """Test cost calculation for GPT-3.5"""
        tracker = CostTracker()
        
        cost = tracker.calculate_cost(
            ModelType.GPT_35_TURBO.value,
            prompt_tokens=2000,
            completion_tokens=1000
        )
        
        # GPT-3.5: $0.0005 per 1K prompt tokens, $0.0015 per 1K completion tokens
        expected_cost = (2000/1000 * 0.0005) + (1000/1000 * 0.0015)
        assert cost == expected_cost
    
    def test_track_usage(self):
        """Test usage tracking"""
        tracker = CostTracker()
        
        metrics = APIUsageMetrics(
            timestamp=datetime.now(),
            model=ModelType.GPT_4.value,
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            estimated_cost=0.01,
            request_id="test-123"
        )
        
        tracker.track_usage(metrics)
        
        assert len(tracker.usage_history) == 1
        assert tracker._total_cost == 0.01
    
    def test_usage_summary(self):
        """Test usage summary generation"""
        tracker = CostTracker()
        
        # Add some usage
        for i in range(3):
            metrics = APIUsageMetrics(
                timestamp=datetime.now(),
                model=ModelType.GPT_35_TURBO.value,
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                estimated_cost=0.001,
                request_id=f"test-{i}",
                cache_hit=(i == 2),
                response_time_ms=100.0
            )
            tracker.track_usage(metrics)
        
        summary = tracker.get_usage_summary(days=30)
        
        assert summary["total_requests"] == 3
        assert summary["total_tokens"] == 450
        assert summary["total_cost"] == 0.003
        assert summary["cache_hit_rate"] == 1/3
        assert summary["average_response_time_ms"] == 100.0


class TestOpenAIService:
    """Test OpenAI service"""
    
    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client"""
        mock = AsyncMock()
        mock.get = AsyncMock(return_value=None)
        mock.setex = AsyncMock(return_value=True)
        return mock
    
    @pytest.fixture
    def service(self, mock_redis):
        """Create OpenAI service instance"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            return OpenAIService(
                redis_client=mock_redis,
                enable_rate_limiting=False,
                enable_caching=True,
                enable_cost_tracking=True
            )
    
    def test_init_without_api_key(self):
        """Test initialization without API key raises error"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key not provided"):
                OpenAIService()
    
    def test_generate_cache_key(self, service):
        """Test cache key generation"""
        params = {"model": "gpt-3.5-turbo", "temperature": 0.7}
        key = service._generate_cache_key("chat", params)
        
        assert key.startswith("openai:chat:")
        assert len(key) == 28  # prefix + 16 char hash
    
    def test_count_tokens(self, service):
        """Test token counting"""
        text = "Hello, this is a test message."
        count = service.count_tokens(text)
        
        assert isinstance(count, int)
        assert count > 0
    
    @pytest.mark.asyncio
    async def test_chat_completion_with_cache_hit(self, service, mock_redis):
        """Test chat completion with cache hit"""
        cached_response = {
            "id": "cached-123",
            "choices": [{"message": {"content": "Cached response"}}],
            "usage": {"total_tokens": 10}
        }
        mock_redis.get.return_value = json.dumps(cached_response)
        
        with patch.object(service.client.chat.completions, 'create') as mock_create:
            response = await service.chat_completion(
                messages=[{"role": "user", "content": "test"}],
                use_cache=True
            )
        
        # Should not call OpenAI API
        mock_create.assert_not_called()
        assert response["id"] == "cached-123"
    
    @pytest.mark.asyncio
    async def test_chat_completion_with_api_call(self, service, mock_redis):
        """Test chat completion with actual API call"""
        mock_redis.get.return_value = None  # No cache hit
        
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.id = "new-123"
        mock_response.model = "gpt-3.5-turbo"
        mock_response.choices = [
            MagicMock(
                index=0,
                message=MagicMock(role="assistant", content="New response"),
                finish_reason="stop"
            )
        ]
        mock_response.usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15
        )
        
        with patch.object(service.client.chat.completions, 'create', 
                         return_value=mock_response) as mock_create:
            response = await service.chat_completion(
                messages=[{"role": "user", "content": "test"}]
            )
        
        mock_create.assert_called_once()
        assert response["id"] == "new-123"
        assert response["usage"]["total_tokens"] == 15
        
        # Should cache the response
        mock_redis.setex.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_dataset(self, service):
        """Test dataset analysis"""
        dataset_sample = "col1,col2,col3\n1,2,3\n4,5,6"
        
        with patch.object(service, 'chat_completion') as mock_chat:
            mock_chat.return_value = {
                "choices": [{"message": {"content": "Analysis results"}}],
                "model": "gpt-4-turbo-preview"
            }
            
            result = await service.analyze_dataset(
                dataset_sample=dataset_sample,
                analysis_type="general"
            )
        
        assert result["analysis_type"] == "general"
        assert result["recommendations"] == "Analysis results"
        mock_chat.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_embedding(self, service, mock_redis):
        """Test embedding creation"""
        mock_redis.get.return_value = None
        
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
        mock_response.model = "text-embedding-3-small"
        
        with patch.object(service.client.embeddings, 'create',
                         return_value=mock_response) as mock_create:
            embedding = await service.create_embedding("test text")
        
        assert embedding == [0.1, 0.2, 0.3]
        mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, service):
        """Test successful health check"""
        with patch.object(service, 'chat_completion') as mock_chat:
            mock_chat.return_value = {"id": "test"}
            
            health = await service.health_check()
        
        assert health["status"] == "healthy"
        assert health["api_key_valid"] is True
        assert len(health["models_available"]) > 0
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, service):
        """Test health check with API failure"""
        with patch.object(service, 'chat_completion') as mock_chat:
            mock_chat.side_effect = Exception("API error")
            
            health = await service.health_check()
        
        assert health["status"] == "unhealthy"
        assert health["api_key_valid"] is False
        assert "API error" in health["error"]
    
    def test_get_usage_statistics(self, service):
        """Test getting usage statistics"""
        # Add some usage
        service.cost_tracker.track_usage(
            APIUsageMetrics(
                timestamp=datetime.now(),
                model="gpt-3.5-turbo",
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                estimated_cost=0.001,
                request_id="test-1"
            )
        )
        
        stats = service.get_usage_statistics(days=30)
        
        assert stats["total_requests"] == 1
        assert stats["total_tokens"] == 150
        assert stats["total_cost"] > 0


@pytest.mark.asyncio
async def test_singleton_service():
    """Test singleton service management"""
    from backend.app.services.openai_service import get_openai_service, _service_instance
    
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        service1 = await get_openai_service()
        service2 = await get_openai_service()
        
        assert service1 is service2  # Should be same instance