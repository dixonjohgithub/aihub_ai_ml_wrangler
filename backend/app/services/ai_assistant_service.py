"""
File: ai_assistant_service.py

Overview:
OpenAI API integration for intelligent data analysis and imputation suggestions.

Purpose:
Provides AI-powered recommendations for feature engineering, encoding, and imputation strategies.

Dependencies:
- openai: OpenAI API client
- pandas: Data analysis
- numpy: Numerical operations

Last Modified: 2025-08-15
Author: Claude
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import pandas as pd
import numpy as np
from openai import OpenAI
from functools import lru_cache
import hashlib

logger = logging.getLogger(__name__)


class AnalysisType(Enum):
    """Types of AI analysis available"""
    MISSING_DATA_PATTERN = "missing_data_pattern"
    IMPUTATION_STRATEGY = "imputation_strategy"
    FEATURE_ENGINEERING = "feature_engineering"
    ENCODING_STRATEGY = "encoding_strategy"
    CORRELATION_INSIGHTS = "correlation_insights"
    DATA_QUALITY = "data_quality"


@dataclass
class AIRecommendation:
    """AI recommendation result"""
    recommendation_type: str
    column: Optional[str]
    strategy: str
    confidence: float
    reasoning: str
    parameters: Dict[str, Any]
    alternatives: List[Dict[str, Any]]
    timestamp: datetime


@dataclass
class DatasetProfile:
    """Profile of dataset for AI analysis"""
    total_rows: int
    total_columns: int
    numeric_columns: List[str]
    categorical_columns: List[str]
    binary_columns: List[str]
    missing_summary: Dict[str, float]
    correlation_summary: Optional[Dict[str, Any]]
    data_types: Dict[str, str]
    sample_data: Dict[str, List[Any]]


class AIAssistantService:
    """
    Service for AI-powered data analysis and recommendations using OpenAI API
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        """
        Initialize AI Assistant Service
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
            model: OpenAI model to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OpenAI API key not found. AI features will be limited.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
        
        self.model = model
        self.cache = {}  # Simple in-memory cache
        self.usage_stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }
    
    def analyze_dataset(
        self,
        df: pd.DataFrame,
        user_goal: str,
        analysis_type: AnalysisType
    ) -> List[AIRecommendation]:
        """
        Analyze dataset and provide AI recommendations
        
        Args:
            df: DataFrame to analyze
            user_goal: User's stated goal for the analysis
            analysis_type: Type of analysis to perform
            
        Returns:
            List of AI recommendations
        """
        if not self.client:
            return self._get_fallback_recommendations(df, analysis_type)
        
        # Create dataset profile
        profile = self._create_dataset_profile(df)
        
        # Check cache
        cache_key = self._generate_cache_key(profile, user_goal, analysis_type)
        if cache_key in self.cache:
            logger.info("Returning cached AI recommendations")
            return self.cache[cache_key]
        
        # Generate prompt based on analysis type
        prompt = self._generate_prompt(profile, user_goal, analysis_type)
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            recommendations = self._parse_response(response, analysis_type)
            
            # Update usage stats
            self._update_usage_stats(response)
            
            # Cache results
            self.cache[cache_key] = recommendations
            
            return recommendations
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return self._get_fallback_recommendations(df, analysis_type)
    
    def _create_dataset_profile(self, df: pd.DataFrame) -> DatasetProfile:
        """Create a profile of the dataset for AI analysis"""
        # Classify columns
        numeric_columns = []
        categorical_columns = []
        binary_columns = []
        
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                unique_vals = df[col].dropna().unique()
                if len(unique_vals) <= 2 and set(unique_vals).issubset({0, 1}):
                    binary_columns.append(col)
                else:
                    numeric_columns.append(col)
            else:
                categorical_columns.append(col)
        
        # Calculate missing data summary
        missing_summary = {}
        for col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            missing_summary[col] = round(missing_pct, 2)
        
        # Get sample data (first 5 non-null values per column)
        sample_data = {}
        for col in df.columns:
            non_null_values = df[col].dropna().head(5).tolist()
            sample_data[col] = non_null_values
        
        # Data types
        data_types = {col: str(df[col].dtype) for col in df.columns}
        
        return DatasetProfile(
            total_rows=len(df),
            total_columns=len(df.columns),
            numeric_columns=numeric_columns,
            categorical_columns=categorical_columns,
            binary_columns=binary_columns,
            missing_summary=missing_summary,
            correlation_summary=None,  # Computed separately if needed
            data_types=data_types,
            sample_data=sample_data
        )
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for OpenAI"""
        return """You are an expert data scientist assistant specializing in data imputation and feature engineering.
Your role is to analyze datasets and provide actionable recommendations for:
1. Handling missing data with appropriate imputation strategies
2. Feature engineering to improve model performance
3. Encoding strategies for categorical variables
4. Identifying data quality issues and correlations

Always provide recommendations in JSON format with the following structure:
{
    "recommendations": [
        {
            "type": "string",
            "column": "string or null",
            "strategy": "string",
            "confidence": 0.0-1.0,
            "reasoning": "string",
            "parameters": {},
            "alternatives": []
        }
    ]
}

Be specific, practical, and consider the user's stated goals. Provide confidence scores based on data characteristics."""
    
    def _generate_prompt(
        self,
        profile: DatasetProfile,
        user_goal: str,
        analysis_type: AnalysisType
    ) -> str:
        """Generate prompt for OpenAI based on analysis type"""
        base_info = f"""
Dataset Overview:
- Rows: {profile.total_rows}
- Columns: {profile.total_columns}
- Numeric columns: {', '.join(profile.numeric_columns[:10])} {'...' if len(profile.numeric_columns) > 10 else ''}
- Categorical columns: {', '.join(profile.categorical_columns[:10])} {'...' if len(profile.categorical_columns) > 10 else ''}
- Binary columns: {', '.join(profile.binary_columns[:10])} {'...' if len(profile.binary_columns) > 10 else ''}

User Goal: {user_goal}

Missing Data Summary (top 10 columns with highest missing %):
"""
        # Add top missing columns
        sorted_missing = sorted(profile.missing_summary.items(), key=lambda x: x[1], reverse=True)[:10]
        for col, pct in sorted_missing:
            base_info += f"\n- {col}: {pct}% missing"
        
        # Add analysis-specific prompts
        if analysis_type == AnalysisType.IMPUTATION_STRATEGY:
            prompt = base_info + """

Task: Recommend optimal imputation strategies for each column with missing data.
Consider:
1. Data type and distribution
2. Missing data mechanism (MCAR, MAR, MNAR)
3. Percentage of missing values
4. User's analysis goals
5. Relationships between variables

For each column with significant missing data, recommend:
- Primary imputation strategy with parameters
- Alternative strategies if the primary fails
- Specific warnings or considerations
"""
        
        elif analysis_type == AnalysisType.FEATURE_ENGINEERING:
            prompt = base_info + """

Task: Suggest feature engineering techniques to improve the dataset.
Consider:
1. Creating interaction features
2. Polynomial features for numeric columns
3. Binning continuous variables
4. Date/time feature extraction
5. Text feature extraction if applicable

Provide specific, actionable recommendations with expected benefits.
"""
        
        elif analysis_type == AnalysisType.ENCODING_STRATEGY:
            prompt = base_info + """

Task: Recommend encoding strategies for categorical variables.
Consider:
1. Cardinality of each categorical column
2. Ordinal vs nominal nature
3. Target variable relationship (if classification/regression)
4. Memory and computational efficiency

For each categorical column, suggest:
- Optimal encoding method (one-hot, label, target, etc.)
- Parameters and considerations
- Potential issues to watch for
"""
        
        elif analysis_type == AnalysisType.DATA_QUALITY:
            prompt = base_info + """

Task: Identify data quality issues and provide remediation strategies.
Look for:
1. Outliers and anomalies
2. Data type mismatches
3. Inconsistent formats
4. Duplicate records
5. Logical inconsistencies

Provide specific quality issues found and actionable fixes.
"""
        
        else:
            prompt = base_info + """

Task: Provide general data analysis recommendations based on the dataset characteristics and user goals.
"""
        
        return prompt
    
    def _parse_response(
        self,
        response: Any,
        analysis_type: AnalysisType
    ) -> List[AIRecommendation]:
        """Parse OpenAI response into recommendations"""
        recommendations = []
        
        try:
            # Parse JSON response
            content = response.choices[0].message.content
            data = json.loads(content)
            
            for rec in data.get("recommendations", []):
                recommendation = AIRecommendation(
                    recommendation_type=rec.get("type", analysis_type.value),
                    column=rec.get("column"),
                    strategy=rec.get("strategy", ""),
                    confidence=float(rec.get("confidence", 0.5)),
                    reasoning=rec.get("reasoning", ""),
                    parameters=rec.get("parameters", {}),
                    alternatives=rec.get("alternatives", []),
                    timestamp=datetime.now()
                )
                recommendations.append(recommendation)
                
        except Exception as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            # Return a basic recommendation on parse failure
            recommendations.append(AIRecommendation(
                recommendation_type=analysis_type.value,
                column=None,
                strategy="Unable to parse AI response",
                confidence=0.0,
                reasoning=str(e),
                parameters={},
                alternatives=[],
                timestamp=datetime.now()
            ))
        
        return recommendations
    
    def _get_fallback_recommendations(
        self,
        df: pd.DataFrame,
        analysis_type: AnalysisType
    ) -> List[AIRecommendation]:
        """Get fallback recommendations when AI is unavailable"""
        recommendations = []
        
        if analysis_type == AnalysisType.IMPUTATION_STRATEGY:
            # Simple rule-based recommendations
            for col in df.columns:
                missing_pct = (df[col].isnull().sum() / len(df)) * 100
                if missing_pct > 0:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        if missing_pct < 5:
                            strategy = "mean"
                            reasoning = "Low missing percentage, mean imputation is efficient"
                        elif missing_pct < 20:
                            strategy = "knn"
                            reasoning = "Moderate missing data, KNN captures patterns"
                        else:
                            strategy = "mice"
                            reasoning = "High missing data, multivariate imputation recommended"
                    else:
                        strategy = "mode"
                        reasoning = "Categorical data, use most frequent value"
                    
                    recommendations.append(AIRecommendation(
                        recommendation_type=analysis_type.value,
                        column=col,
                        strategy=strategy,
                        confidence=0.7,
                        reasoning=reasoning,
                        parameters={},
                        alternatives=[],
                        timestamp=datetime.now()
                    ))
        
        elif analysis_type == AnalysisType.FEATURE_ENGINEERING:
            recommendations.append(AIRecommendation(
                recommendation_type=analysis_type.value,
                column=None,
                strategy="Consider polynomial features for numeric columns",
                confidence=0.5,
                reasoning="Default recommendation without AI analysis",
                parameters={"degree": 2},
                alternatives=[],
                timestamp=datetime.now()
            ))
        
        return recommendations
    
    def _generate_cache_key(
        self,
        profile: DatasetProfile,
        user_goal: str,
        analysis_type: AnalysisType
    ) -> str:
        """Generate cache key for recommendations"""
        # Create a hash of the profile and parameters
        key_data = {
            "rows": profile.total_rows,
            "columns": profile.total_columns,
            "missing": list(profile.missing_summary.keys())[:10],  # Top 10 columns
            "goal": user_goal[:100],  # First 100 chars
            "type": analysis_type.value
        }
        
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _update_usage_stats(self, response: Any):
        """Update API usage statistics"""
        if hasattr(response, 'usage'):
            self.usage_stats["total_requests"] += 1
            self.usage_stats["total_tokens"] += response.usage.total_tokens
            
            # Estimate cost (GPT-4 pricing as of 2024)
            # Input: $0.01 per 1K tokens, Output: $0.03 per 1K tokens
            input_cost = (response.usage.prompt_tokens / 1000) * 0.01
            output_cost = (response.usage.completion_tokens / 1000) * 0.03
            self.usage_stats["total_cost"] += (input_cost + output_cost)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current API usage statistics"""
        return self.usage_stats.copy()
    
    def clear_cache(self):
        """Clear recommendation cache"""
        self.cache.clear()
        logger.info("AI recommendation cache cleared")
    
    def interactive_chat(
        self,
        df: pd.DataFrame,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Interactive chat for data analysis questions
        
        Args:
            df: DataFrame being analyzed
            user_message: User's question or request
            conversation_history: Previous conversation messages
            
        Returns:
            AI response as string
        """
        if not self.client:
            return "AI assistant is not available. Please check your OpenAI API key."
        
        # Create dataset context
        profile = self._create_dataset_profile(df)
        
        # Build conversation
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "system", "content": f"Dataset context: {json.dumps(asdict(profile), default=str)[:2000]}"}
        ]
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-5:])  # Keep last 5 messages for context
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            self._update_usage_stats(response)
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Chat API call failed: {e}")
            return f"I encountered an error: {str(e)}. Please try again."
    
    def estimate_cost(self, df: pd.DataFrame, analysis_types: List[AnalysisType]) -> float:
        """
        Estimate API cost for analyzing a dataset
        
        Args:
            df: DataFrame to analyze
            analysis_types: Types of analysis to perform
            
        Returns:
            Estimated cost in USD
        """
        # Estimate tokens based on dataset size
        profile = self._create_dataset_profile(df)
        
        # Rough estimation: ~500 tokens base + 50 tokens per column + 100 per analysis type
        estimated_tokens = 500 + (50 * profile.total_columns) + (100 * len(analysis_types))
        
        # GPT-4 pricing estimate
        estimated_cost = (estimated_tokens / 1000) * 0.02  # Average of input/output pricing
        
        return round(estimated_cost, 4)