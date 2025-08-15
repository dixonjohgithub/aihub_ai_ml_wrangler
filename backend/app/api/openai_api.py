"""
File: openai_api.py

Overview:
FastAPI endpoints for OpenAI integration including dataset analysis,
usage monitoring, and health checks.

Purpose:
Provides REST API interface for OpenAI functionality with proper
error handling and response formatting.

Dependencies:
- fastapi: Web framework
- backend.app.services.openai_service: OpenAI service layer

Last Modified: 2025-08-15
Author: Claude
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import json

from backend.app.services.openai_service import (
    get_openai_service,
    OpenAIService,
    ModelType
)
from backend.app.core.deps import get_redis_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/openai", tags=["openai"])


# Request/Response models
class ChatCompletionRequest(BaseModel):
    """Chat completion request model"""
    messages: List[Dict[str, str]] = Field(..., description="List of messages")
    model: str = Field(ModelType.GPT_35_TURBO.value, description="Model to use")
    temperature: float = Field(0.7, ge=0, le=2, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, ge=1, le=4000, description="Max tokens")
    use_cache: bool = Field(True, description="Use caching")


class DatasetAnalysisRequest(BaseModel):
    """Dataset analysis request model"""
    dataset_sample: str = Field(..., description="Dataset sample (CSV or JSON)")
    analysis_type: str = Field("general", description="Type of analysis")
    model: str = Field(ModelType.GPT_4_TURBO.value, description="Model to use")
    max_rows: int = Field(100, ge=10, le=1000, description="Max rows to analyze")


class ImputationStrategyRequest(BaseModel):
    """Request for imputation strategy recommendations"""
    column_info: Dict[str, Any] = Field(..., description="Column information")
    missing_patterns: Dict[str, Any] = Field(..., description="Missing data patterns")
    data_sample: Optional[str] = Field(None, description="Optional data sample")


class FeatureEngineeringRequest(BaseModel):
    """Request for feature engineering suggestions"""
    columns: List[str] = Field(..., description="List of columns")
    data_types: Dict[str, str] = Field(..., description="Column data types")
    statistics: Dict[str, Any] = Field(..., description="Column statistics")
    target_variable: Optional[str] = Field(None, description="Target variable if known")


@router.post("/chat")
async def chat_completion(
    request: ChatCompletionRequest,
    openai_service: OpenAIService = Depends(get_openai_service)
) -> Dict[str, Any]:
    """
    Create a chat completion using OpenAI API
    
    Returns:
        Chat completion response with usage metrics
    """
    try:
        response = await openai_service.chat_completion(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            use_cache=request.use_cache
        )
        
        return {
            "success": True,
            "data": response
        }
        
    except Exception as e:
        logger.error(f"Chat completion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-dataset")
async def analyze_dataset(
    request: DatasetAnalysisRequest,
    openai_service: OpenAIService = Depends(get_openai_service)
) -> Dict[str, Any]:
    """
    Analyze a dataset sample for insights and recommendations
    
    Returns:
        Analysis results with recommendations
    """
    try:
        # Truncate sample if too large
        lines = request.dataset_sample.split('\n')
        if len(lines) > request.max_rows:
            truncated_sample = '\n'.join(lines[:request.max_rows])
            truncated_sample += f"\n... (showing first {request.max_rows} rows)"
        else:
            truncated_sample = request.dataset_sample
        
        analysis = await openai_service.analyze_dataset(
            dataset_sample=truncated_sample,
            analysis_type=request.analysis_type,
            model=request.model
        )
        
        return {
            "success": True,
            "data": analysis
        }
        
    except Exception as e:
        logger.error(f"Dataset analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/imputation-strategy")
async def suggest_imputation_strategy(
    request: ImputationStrategyRequest,
    openai_service: OpenAIService = Depends(get_openai_service)
) -> Dict[str, Any]:
    """
    Get AI-powered imputation strategy recommendations
    
    Returns:
        Imputation strategies for each column with missing data
    """
    try:
        # Prepare context for analysis
        context = f"""
Column Information:
{json.dumps(request.column_info, indent=2)}

Missing Data Patterns:
{json.dumps(request.missing_patterns, indent=2)}
"""
        
        if request.data_sample:
            context += f"\n\nData Sample:\n{request.data_sample[:1000]}"
        
        messages = [
            {
                "role": "system",
                "content": """You are a data imputation expert. Analyze the missing data patterns 
                and recommend specific imputation strategies for each column. Consider:
                1. Missing data mechanism (MCAR, MAR, MNAR)
                2. Data type and distribution
                3. Relationships between variables
                4. Domain-specific considerations
                
                Provide specific, actionable recommendations."""
            },
            {
                "role": "user",
                "content": context
            }
        ]
        
        response = await openai_service.chat_completion(
            messages=messages,
            model=ModelType.GPT_4_TURBO.value,
            temperature=0.3,
            max_tokens=1500
        )
        
        return {
            "success": True,
            "data": {
                "recommendations": response["choices"][0]["message"]["content"],
                "model_used": response["model"],
                "cost_estimate": response.get("cost_estimate", 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Imputation strategy suggestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feature-engineering")
async def suggest_feature_engineering(
    request: FeatureEngineeringRequest,
    openai_service: OpenAIService = Depends(get_openai_service)
) -> Dict[str, Any]:
    """
    Get AI-powered feature engineering suggestions
    
    Returns:
        Feature engineering recommendations
    """
    try:
        # Prepare context
        context = f"""
Columns: {', '.join(request.columns)}

Data Types:
{json.dumps(request.data_types, indent=2)}

Statistics:
{json.dumps(request.statistics, indent=2)}
"""
        
        if request.target_variable:
            context += f"\nTarget Variable: {request.target_variable}"
        
        messages = [
            {
                "role": "system",
                "content": """You are a feature engineering expert. Analyze the dataset structure 
                and suggest feature engineering strategies. Consider:
                1. Feature transformations (log, sqrt, polynomial)
                2. Feature interactions and combinations
                3. Encoding strategies for categorical variables
                4. Handling of temporal features
                5. Domain-specific feature creation
                
                Provide specific, implementable suggestions with Python code examples where helpful."""
            },
            {
                "role": "user",
                "content": context
            }
        ]
        
        response = await openai_service.chat_completion(
            messages=messages,
            model=ModelType.GPT_4_TURBO.value,
            temperature=0.4,
            max_tokens=2000
        )
        
        return {
            "success": True,
            "data": {
                "suggestions": response["choices"][0]["message"]["content"],
                "model_used": response["model"],
                "cost_estimate": response.get("cost_estimate", 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Feature engineering suggestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage-statistics")
async def get_usage_statistics(
    days: int = 30,
    openai_service: OpenAIService = Depends(get_openai_service)
) -> Dict[str, Any]:
    """
    Get OpenAI API usage statistics
    
    Args:
        days: Number of days to include in statistics
        
    Returns:
        Usage statistics including costs and performance metrics
    """
    try:
        stats = openai_service.get_usage_statistics(days=days)
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get usage statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check(
    openai_service: OpenAIService = Depends(get_openai_service)
) -> Dict[str, Any]:
    """
    Check OpenAI service health and configuration
    
    Returns:
        Service health status and configuration
    """
    try:
        health = await openai_service.health_check()
        
        return {
            "success": True,
            "data": health
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": {
                "status": "unhealthy"
            }
        }


@router.get("/models")
async def list_available_models() -> Dict[str, Any]:
    """
    List available OpenAI models
    
    Returns:
        List of available models with descriptions
    """
    models = {
        ModelType.GPT_4_TURBO.value: {
            "name": "GPT-4 Turbo",
            "description": "Most capable model, best for complex analysis",
            "context_window": 128000,
            "recommended_for": ["complex analysis", "feature engineering", "detailed recommendations"]
        },
        ModelType.GPT_4.value: {
            "name": "GPT-4",
            "description": "High capability model for advanced tasks",
            "context_window": 8192,
            "recommended_for": ["data analysis", "pattern recognition", "strategy recommendations"]
        },
        ModelType.GPT_35_TURBO.value: {
            "name": "GPT-3.5 Turbo",
            "description": "Fast and cost-effective for most tasks",
            "context_window": 4096,
            "recommended_for": ["quick analysis", "simple recommendations", "data validation"]
        },
        ModelType.GPT_35_TURBO_16K.value: {
            "name": "GPT-3.5 Turbo 16K",
            "description": "Extended context for larger datasets",
            "context_window": 16384,
            "recommended_for": ["large sample analysis", "batch processing", "comprehensive reports"]
        }
    }
    
    return {
        "success": True,
        "data": models
    }


@router.post("/validate-api-key")
async def validate_api_key(
    api_key: str,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Validate an OpenAI API key
    
    Args:
        api_key: API key to validate
        
    Returns:
        Validation result
    """
    try:
        # Create temporary service with provided key
        test_service = OpenAIService(api_key=api_key, enable_cost_tracking=False)
        
        # Test the key with minimal API call
        health = await test_service.health_check()
        
        return {
            "success": True,
            "data": {
                "valid": health["api_key_valid"],
                "models_available": health.get("models_available", [])
            }
        }
        
    except Exception as e:
        logger.error(f"API key validation failed: {e}")
        return {
            "success": False,
            "data": {
                "valid": False,
                "error": str(e)
            }
        }