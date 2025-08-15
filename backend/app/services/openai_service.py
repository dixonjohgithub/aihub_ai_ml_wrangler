"""
File: openai_service.py

Overview:
Comprehensive OpenAI API integration service with secure key management,
rate limiting, caching, and cost tracking.

Purpose:
Provides a centralized interface for all OpenAI API interactions with
enterprise-grade features for production deployment.

Dependencies:
- openai: OpenAI Python SDK
- tiktoken: Token counting for cost estimation
- redis: Caching layer for API responses
- tenacity: Retry logic with exponential backoff

Last Modified: 2025-08-15
Author: Claude
"""

import os
import json
import hashlib
import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from functools import wraps

from openai import AsyncOpenAI, OpenAI
import tiktoken
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
import redis.asyncio as redis
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Supported OpenAI model types"""
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4 = "gpt-4"
    GPT_35_TURBO = "gpt-3.5-turbo"
    GPT_35_TURBO_16K = "gpt-3.5-turbo-16k"
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"


@dataclass
class APIUsageMetrics:
    """Track API usage metrics"""
    timestamp: datetime
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float
    request_id: str
    cache_hit: bool = False
    response_time_ms: float = 0


class RateLimiter:
    """Token bucket rate limiter for API calls"""
    
    def __init__(self, max_requests_per_minute: int = 60, 
                 max_tokens_per_minute: int = 150000):
        self.max_requests_per_minute = max_requests_per_minute
        self.max_tokens_per_minute = max_tokens_per_minute
        self.request_timestamps: List[datetime] = []
        self.token_usage: List[Tuple[datetime, int]] = []
        self._lock = asyncio.Lock()
    
    async def check_rate_limit(self, estimated_tokens: int) -> Tuple[bool, float]:
        """
        Check if request can proceed under rate limits
        
        Returns:
            Tuple of (can_proceed, wait_time_seconds)
        """
        async with self._lock:
            now = datetime.now()
            one_minute_ago = now - timedelta(minutes=1)
            
            # Clean old timestamps
            self.request_timestamps = [
                ts for ts in self.request_timestamps if ts > one_minute_ago
            ]
            self.token_usage = [
                (ts, tokens) for ts, tokens in self.token_usage if ts > one_minute_ago
            ]
            
            # Check request limit
            if len(self.request_timestamps) >= self.max_requests_per_minute:
                wait_time = (self.request_timestamps[0] - one_minute_ago).total_seconds()
                return False, wait_time
            
            # Check token limit
            current_tokens = sum(tokens for _, tokens in self.token_usage)
            if current_tokens + estimated_tokens > self.max_tokens_per_minute:
                if self.token_usage:
                    wait_time = (self.token_usage[0][0] - one_minute_ago).total_seconds()
                    return False, wait_time
                return False, 60.0
            
            # Record usage
            self.request_timestamps.append(now)
            self.token_usage.append((now, estimated_tokens))
            
            return True, 0.0


class CostTracker:
    """Track and calculate OpenAI API costs"""
    
    # Pricing per 1K tokens (as of 2024)
    PRICING = {
        ModelType.GPT_4_TURBO.value: {"prompt": 0.01, "completion": 0.03},
        ModelType.GPT_4.value: {"prompt": 0.03, "completion": 0.06},
        ModelType.GPT_35_TURBO.value: {"prompt": 0.0005, "completion": 0.0015},
        ModelType.GPT_35_TURBO_16K.value: {"prompt": 0.001, "completion": 0.002},
        ModelType.TEXT_EMBEDDING_3_SMALL.value: {"prompt": 0.00002, "completion": 0},
        ModelType.TEXT_EMBEDDING_3_LARGE.value: {"prompt": 0.00013, "completion": 0},
        ModelType.TEXT_EMBEDDING_ADA_002.value: {"prompt": 0.0001, "completion": 0},
    }
    
    def __init__(self):
        self.usage_history: List[APIUsageMetrics] = []
        self._total_cost = 0.0
    
    def calculate_cost(self, model: str, prompt_tokens: int, 
                      completion_tokens: int) -> float:
        """Calculate cost for a specific API call"""
        if model not in self.PRICING:
            logger.warning(f"Unknown model {model}, using GPT-3.5 pricing")
            model = ModelType.GPT_35_TURBO.value
        
        pricing = self.PRICING[model]
        prompt_cost = (prompt_tokens / 1000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * pricing["completion"]
        
        return prompt_cost + completion_cost
    
    def track_usage(self, metrics: APIUsageMetrics):
        """Track API usage metrics"""
        self.usage_history.append(metrics)
        self._total_cost += metrics.estimated_cost
    
    def get_usage_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get usage summary for the specified period"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_usage = [m for m in self.usage_history if m.timestamp > cutoff_date]
        
        if not recent_usage:
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "cache_hit_rate": 0.0
            }
        
        total_requests = len(recent_usage)
        total_tokens = sum(m.total_tokens for m in recent_usage)
        total_cost = sum(m.estimated_cost for m in recent_usage)
        cache_hits = sum(1 for m in recent_usage if m.cache_hit)
        cache_hit_rate = cache_hits / total_requests if total_requests > 0 else 0
        
        return {
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 4),
            "cache_hit_rate": round(cache_hit_rate, 2),
            "average_response_time_ms": round(
                sum(m.response_time_ms for m in recent_usage) / total_requests, 2
            ),
            "by_model": self._aggregate_by_model(recent_usage)
        }
    
    def _aggregate_by_model(self, usage: List[APIUsageMetrics]) -> Dict[str, Any]:
        """Aggregate usage statistics by model"""
        by_model = {}
        for metric in usage:
            if metric.model not in by_model:
                by_model[metric.model] = {
                    "requests": 0,
                    "tokens": 0,
                    "cost": 0.0
                }
            by_model[metric.model]["requests"] += 1
            by_model[metric.model]["tokens"] += metric.total_tokens
            by_model[metric.model]["cost"] += metric.estimated_cost
        
        return by_model


class OpenAIService:
    """
    Main OpenAI service with comprehensive features for production use
    """
    
    def __init__(self, api_key: Optional[str] = None, 
                 redis_client: Optional[redis.Redis] = None,
                 cache_ttl_hours: int = 24,
                 enable_rate_limiting: bool = True,
                 enable_caching: bool = True,
                 enable_cost_tracking: bool = True):
        """
        Initialize OpenAI service
        
        Args:
            api_key: OpenAI API key (defaults to env variable)
            redis_client: Redis client for caching
            cache_ttl_hours: Cache TTL in hours
            enable_rate_limiting: Enable rate limiting
            enable_caching: Enable response caching
            enable_cost_tracking: Enable cost tracking
        """
        # API key management
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        # Initialize clients
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.sync_client = OpenAI(api_key=self.api_key)
        
        # Redis caching
        self.redis_client = redis_client
        self.cache_ttl = cache_ttl_hours * 3600
        self.enable_caching = enable_caching and redis_client is not None
        
        # Rate limiting
        self.enable_rate_limiting = enable_rate_limiting
        self.rate_limiter = RateLimiter() if enable_rate_limiting else None
        
        # Cost tracking
        self.enable_cost_tracking = enable_cost_tracking
        self.cost_tracker = CostTracker() if enable_cost_tracking else None
        
        # Token encoding
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def _generate_cache_key(self, prefix: str, params: Dict[str, Any]) -> str:
        """Generate cache key from parameters"""
        # Create stable string representation
        param_str = json.dumps(params, sort_keys=True)
        hash_digest = hashlib.sha256(param_str.encode()).hexdigest()[:16]
        return f"openai:{prefix}:{hash_digest}"
    
    def count_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """Count tokens in text for a specific model"""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = self.encoding
        
        return len(encoding.encode(text))
    
    async def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available"""
        if not self.enable_caching:
            return None
        
        try:
            cached = await self.redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
        
        return None
    
    async def _cache_response(self, cache_key: str, response: Dict[str, Any]):
        """Cache API response"""
        if not self.enable_caching:
            return
        
        try:
            await self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(response)
            )
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type((Exception,))
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = ModelType.GPT_35_TURBO.value,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        use_cache: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a chat completion with all production features
        
        Args:
            messages: List of message dictionaries
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            use_cache: Whether to use caching for this request
            **kwargs: Additional OpenAI API parameters
            
        Returns:
            API response with metadata
        """
        import time
        start_time = time.time()
        
        # Prepare parameters
        params = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            **kwargs
        }
        if max_tokens:
            params["max_tokens"] = max_tokens
        
        # Check cache
        cache_key = self._generate_cache_key("chat", params)
        if use_cache and self.enable_caching:
            cached_response = await self._get_cached_response(cache_key)
            if cached_response:
                logger.info(f"Cache hit for chat completion")
                if self.enable_cost_tracking:
                    # Track cache hit
                    metrics = APIUsageMetrics(
                        timestamp=datetime.now(),
                        model=model,
                        prompt_tokens=0,
                        completion_tokens=0,
                        total_tokens=0,
                        estimated_cost=0.0,
                        request_id="cache_hit",
                        cache_hit=True,
                        response_time_ms=(time.time() - start_time) * 1000
                    )
                    self.cost_tracker.track_usage(metrics)
                return cached_response
        
        # Estimate tokens for rate limiting
        prompt_tokens = sum(self.count_tokens(msg["content"], model) for msg in messages)
        estimated_total = prompt_tokens + (max_tokens or 500)
        
        # Check rate limits
        if self.enable_rate_limiting:
            can_proceed, wait_time = await self.rate_limiter.check_rate_limit(estimated_total)
            if not can_proceed:
                logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
                await asyncio.sleep(wait_time)
                # Retry after waiting
                can_proceed, _ = await self.rate_limiter.check_rate_limit(estimated_total)
                if not can_proceed:
                    raise Exception("Rate limit exceeded after waiting")
        
        # Make API call
        try:
            response = await self.client.chat.completions.create(**params)
            
            # Process response
            result = {
                "id": response.id,
                "model": response.model,
                "choices": [
                    {
                        "index": choice.index,
                        "message": {
                            "role": choice.message.role,
                            "content": choice.message.content
                        },
                        "finish_reason": choice.finish_reason
                    }
                    for choice in response.choices
                ],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            # Track usage
            if self.enable_cost_tracking:
                cost = self.cost_tracker.calculate_cost(
                    model,
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens
                )
                
                metrics = APIUsageMetrics(
                    timestamp=datetime.now(),
                    model=model,
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                    estimated_cost=cost,
                    request_id=response.id,
                    cache_hit=False,
                    response_time_ms=(time.time() - start_time) * 1000
                )
                self.cost_tracker.track_usage(metrics)
                
                result["cost_estimate"] = round(cost, 6)
            
            # Cache response
            if use_cache and self.enable_caching:
                await self._cache_response(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise
    
    async def create_embedding(
        self,
        text: str,
        model: str = ModelType.TEXT_EMBEDDING_3_SMALL.value,
        use_cache: bool = True
    ) -> List[float]:
        """
        Create text embedding
        
        Args:
            text: Text to embed
            model: Embedding model to use
            use_cache: Whether to use caching
            
        Returns:
            Embedding vector
        """
        import time
        start_time = time.time()
        
        # Check cache
        cache_key = self._generate_cache_key("embedding", {"text": text, "model": model})
        if use_cache and self.enable_caching:
            cached_response = await self._get_cached_response(cache_key)
            if cached_response:
                logger.info("Cache hit for embedding")
                return cached_response["embedding"]
        
        # Make API call
        try:
            response = await self.client.embeddings.create(
                model=model,
                input=text
            )
            
            embedding = response.data[0].embedding
            
            # Track usage
            if self.enable_cost_tracking:
                tokens = self.count_tokens(text, model)
                cost = self.cost_tracker.calculate_cost(model, tokens, 0)
                
                metrics = APIUsageMetrics(
                    timestamp=datetime.now(),
                    model=model,
                    prompt_tokens=tokens,
                    completion_tokens=0,
                    total_tokens=tokens,
                    estimated_cost=cost,
                    request_id=response.model,
                    cache_hit=False,
                    response_time_ms=(time.time() - start_time) * 1000
                )
                self.cost_tracker.track_usage(metrics)
            
            # Cache response
            if use_cache and self.enable_caching:
                await self._cache_response(cache_key, {"embedding": embedding})
            
            return embedding
            
        except Exception as e:
            logger.error(f"Embedding creation failed: {e}")
            raise
    
    async def analyze_dataset(
        self,
        dataset_sample: str,
        analysis_type: str = "general",
        model: str = ModelType.GPT_4_TURBO.value
    ) -> Dict[str, Any]:
        """
        Analyze dataset sample for insights and recommendations
        
        Args:
            dataset_sample: Sample of dataset (CSV or JSON string)
            analysis_type: Type of analysis (general, imputation, encoding, etc.)
            model: Model to use for analysis
            
        Returns:
            Analysis results and recommendations
        """
        # Prepare analysis prompt based on type
        prompts = {
            "general": """Analyze this dataset sample and provide:
1. Data quality assessment
2. Identified patterns and anomalies
3. Recommended preprocessing steps
4. Suggested feature engineering
5. Potential issues to address

Dataset sample:
{sample}""",
            
            "imputation": """Analyze missing data patterns in this dataset and recommend:
1. Missing data mechanisms (MCAR, MAR, MNAR)
2. Best imputation strategies for each column
3. Columns to potentially drop
4. Impact of missingness on analysis

Dataset sample:
{sample}""",
            
            "encoding": """Analyze categorical variables and recommend:
1. Encoding strategies for each categorical column
2. Handling of high cardinality features
3. Ordinal vs nominal encoding decisions
4. Feature interaction suggestions

Dataset sample:
{sample}""",
            
            "feature_engineering": """Suggest feature engineering for this dataset:
1. New features to create
2. Feature transformations needed
3. Polynomial or interaction features
4. Dimensionality reduction opportunities

Dataset sample:
{sample}"""
        }
        
        prompt = prompts.get(analysis_type, prompts["general"]).format(sample=dataset_sample)
        
        messages = [
            {"role": "system", "content": "You are a data science expert specializing in data preprocessing and feature engineering."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat_completion(
            messages=messages,
            model=model,
            temperature=0.3,  # Lower temperature for analytical tasks
            max_tokens=1500
        )
        
        return {
            "analysis_type": analysis_type,
            "recommendations": response["choices"][0]["message"]["content"],
            "model_used": model,
            "cost_estimate": response.get("cost_estimate", 0)
        }
    
    def get_usage_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics for the specified period"""
        if not self.enable_cost_tracking:
            return {"message": "Cost tracking is disabled"}
        
        return self.cost_tracker.get_usage_summary(days)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check OpenAI API connectivity and service health"""
        try:
            # Test with a minimal API call
            response = await self.chat_completion(
                messages=[{"role": "user", "content": "test"}],
                model=ModelType.GPT_35_TURBO.value,
                max_tokens=1,
                use_cache=False
            )
            
            return {
                "status": "healthy",
                "api_key_valid": True,
                "cache_enabled": self.enable_caching,
                "rate_limiting_enabled": self.enable_rate_limiting,
                "cost_tracking_enabled": self.enable_cost_tracking,
                "models_available": [model.value for model in ModelType]
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "api_key_valid": False
            }


# Singleton instance management
_service_instance: Optional[OpenAIService] = None


async def get_openai_service(redis_client: Optional[redis.Redis] = None) -> OpenAIService:
    """Get or create OpenAI service singleton"""
    global _service_instance
    
    if _service_instance is None:
        _service_instance = OpenAIService(redis_client=redis_client)
    
    return _service_instance