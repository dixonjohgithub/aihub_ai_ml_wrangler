"""
Test suite for OpenAI API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
import json

from backend.main import app
from backend.app.services.openai_service import OpenAIService, ModelType


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_openai_service():
    """Create mock OpenAI service"""
    mock = AsyncMock(spec=OpenAIService)
    mock.chat_completion = AsyncMock()
    mock.analyze_dataset = AsyncMock()
    mock.create_embedding = AsyncMock()
    mock.get_usage_statistics = Mock()
    mock.health_check = AsyncMock()
    return mock


class TestChatCompletion:
    """Test chat completion endpoint"""
    
    def test_chat_completion_success(self, client, mock_openai_service):
        """Test successful chat completion"""
        mock_response = {
            "id": "test-123",
            "choices": [{"message": {"content": "Test response"}}],
            "usage": {"total_tokens": 50}
        }
        mock_openai_service.chat_completion.return_value = mock_response
        
        with patch('backend.app.api.openai_api.get_openai_service', return_value=mock_openai_service):
            response = client.post(
                "/api/openai/chat",
                json={
                    "messages": [{"role": "user", "content": "Hello"}],
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.7
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "test-123"
    
    def test_chat_completion_with_cache(self, client, mock_openai_service):
        """Test chat completion with caching enabled"""
        mock_response = {"id": "cached-123", "choices": []}
        mock_openai_service.chat_completion.return_value = mock_response
        
        with patch('backend.app.api.openai_api.get_openai_service', return_value=mock_openai_service):
            response = client.post(
                "/api/openai/chat",
                json={
                    "messages": [{"role": "user", "content": "Test"}],
                    "use_cache": True
                }
            )
        
        assert response.status_code == 200
        mock_openai_service.chat_completion.assert_called_with(
            messages=[{"role": "user", "content": "Test"}],
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=None,
            use_cache=True
        )
    
    def test_chat_completion_error(self, client, mock_openai_service):
        """Test chat completion with API error"""
        mock_openai_service.chat_completion.side_effect = Exception("API error")
        
        with patch('backend.app.api.openai_api.get_openai_service', return_value=mock_openai_service):
            response = client.post(
                "/api/openai/chat",
                json={
                    "messages": [{"role": "user", "content": "Test"}]
                }
            )
        
        assert response.status_code == 500
        assert "API error" in response.json()["detail"]


class TestDatasetAnalysis:
    """Test dataset analysis endpoint"""
    
    def test_analyze_dataset_success(self, client, mock_openai_service):
        """Test successful dataset analysis"""
        mock_response = {
            "analysis_type": "general",
            "recommendations": "Test recommendations",
            "model_used": "gpt-4-turbo-preview",
            "cost_estimate": 0.05
        }
        mock_openai_service.analyze_dataset.return_value = mock_response
        
        with patch('backend.app.api.openai_api.get_openai_service', return_value=mock_openai_service):
            response = client.post(
                "/api/openai/analyze-dataset",
                json={
                    "dataset_sample": "col1,col2\n1,2\n3,4",
                    "analysis_type": "general"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["analysis_type"] == "general"
    
    def test_analyze_dataset_truncation(self, client, mock_openai_service):
        """Test dataset truncation for large samples"""
        # Create large dataset
        large_dataset = "\n".join([f"row{i}" for i in range(200)])
        
        mock_openai_service.analyze_dataset.return_value = {
            "analysis_type": "general",
            "recommendations": "Truncated analysis"
        }
        
        with patch('backend.app.api.openai_api.get_openai_service', return_value=mock_openai_service):
            response = client.post(
                "/api/openai/analyze-dataset",
                json={
                    "dataset_sample": large_dataset,
                    "max_rows": 50
                }
            )
        
        assert response.status_code == 200
        # Check that truncation was applied
        call_args = mock_openai_service.analyze_dataset.call_args
        assert "showing first 50 rows" in call_args[1]["dataset_sample"]


class TestImputationStrategy:
    """Test imputation strategy endpoint"""
    
    def test_imputation_strategy_success(self, client, mock_openai_service):
        """Test successful imputation strategy suggestion"""
        mock_response = {
            "id": "test-123",
            "choices": [{"message": {"content": "Use mean imputation"}}],
            "model": "gpt-4-turbo-preview",
            "cost_estimate": 0.03
        }
        mock_openai_service.chat_completion.return_value = mock_response
        
        with patch('backend.app.api.openai_api.get_openai_service', return_value=mock_openai_service):
            response = client.post(
                "/api/openai/imputation-strategy",
                json={
                    "column_info": {"col1": "numeric", "col2": "categorical"},
                    "missing_patterns": {"col1": 0.2, "col2": 0.1}
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Use mean imputation" in data["data"]["recommendations"]


class TestFeatureEngineering:
    """Test feature engineering endpoint"""
    
    def test_feature_engineering_success(self, client, mock_openai_service):
        """Test successful feature engineering suggestions"""
        mock_response = {
            "id": "test-123",
            "choices": [{"message": {"content": "Create polynomial features"}}],
            "model": "gpt-4-turbo-preview",
            "cost_estimate": 0.04
        }
        mock_openai_service.chat_completion.return_value = mock_response
        
        with patch('backend.app.api.openai_api.get_openai_service', return_value=mock_openai_service):
            response = client.post(
                "/api/openai/feature-engineering",
                json={
                    "columns": ["col1", "col2"],
                    "data_types": {"col1": "numeric", "col2": "categorical"},
                    "statistics": {"col1": {"mean": 5.0}},
                    "target_variable": "target"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "Create polynomial features" in data["data"]["suggestions"]


class TestUsageStatistics:
    """Test usage statistics endpoint"""
    
    def test_get_usage_statistics(self, client, mock_openai_service):
        """Test getting usage statistics"""
        mock_stats = {
            "total_requests": 100,
            "total_tokens": 50000,
            "total_cost": 2.50,
            "cache_hit_rate": 0.3
        }
        mock_openai_service.get_usage_statistics.return_value = mock_stats
        
        with patch('backend.app.api.openai_api.get_openai_service', return_value=mock_openai_service):
            response = client.get("/api/openai/usage-statistics?days=7")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_requests"] == 100


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check_success(self, client, mock_openai_service):
        """Test successful health check"""
        mock_health = {
            "status": "healthy",
            "api_key_valid": True,
            "cache_enabled": True,
            "models_available": ["gpt-4", "gpt-3.5-turbo"]
        }
        mock_openai_service.health_check.return_value = mock_health
        
        with patch('backend.app.api.openai_api.get_openai_service', return_value=mock_openai_service):
            response = client.get("/api/openai/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "healthy"
    
    def test_health_check_failure(self, client, mock_openai_service):
        """Test health check with unhealthy service"""
        mock_openai_service.health_check.side_effect = Exception("Connection failed")
        
        with patch('backend.app.api.openai_api.get_openai_service', return_value=mock_openai_service):
            response = client.get("/api/openai/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["data"]["status"] == "unhealthy"


class TestModels:
    """Test models listing endpoint"""
    
    def test_list_models(self, client):
        """Test listing available models"""
        response = client.get("/api/openai/models")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "gpt-4-turbo-preview" in data["data"]
        assert "gpt-3.5-turbo" in data["data"]


class TestAPIKeyValidation:
    """Test API key validation endpoint"""
    
    def test_validate_api_key_success(self, client):
        """Test successful API key validation"""
        with patch('backend.app.api.openai_api.OpenAIService') as MockService:
            mock_instance = AsyncMock()
            mock_instance.health_check.return_value = {
                "api_key_valid": True,
                "models_available": ["gpt-4", "gpt-3.5-turbo"]
            }
            MockService.return_value = mock_instance
            
            response = client.post(
                "/api/openai/validate-api-key",
                params={"api_key": "test-key-123"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["valid"] is True
    
    def test_validate_api_key_invalid(self, client):
        """Test invalid API key validation"""
        with patch('backend.app.api.openai_api.OpenAIService') as MockService:
            MockService.side_effect = Exception("Invalid API key")
            
            response = client.post(
                "/api/openai/validate-api-key",
                params={"api_key": "invalid-key"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["data"]["valid"] is False