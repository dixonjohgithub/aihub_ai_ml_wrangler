"""
File: ai_analysis_service.py

Overview:
Comprehensive AI-powered analysis service that provides intelligent insights,
recommendations, and suggestions for data preprocessing and feature engineering.

Purpose:
Leverages OpenAI to provide context-aware analysis, feature engineering suggestions,
encoding strategies, and imputation recommendations based on dataset characteristics.

Dependencies:
- backend.app.services.openai_service: OpenAI integration
- pandas: Data manipulation
- numpy: Numerical operations
- typing: Type hints

Last Modified: 2025-08-15
Author: Claude
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import pandas as pd
import numpy as np

from backend.app.services.openai_service import OpenAIService, ModelType

logger = logging.getLogger(__name__)


class AnalysisType(Enum):
    """Types of analysis available"""
    GENERAL = "general"
    FEATURE_ENGINEERING = "feature_engineering"
    ENCODING_STRATEGY = "encoding_strategy"
    IMPUTATION_STRATEGY = "imputation_strategy"
    DATA_QUALITY = "data_quality"
    CORRELATION_ANALYSIS = "correlation_analysis"
    OUTLIER_DETECTION = "outlier_detection"


class SuggestionPriority(Enum):
    """Priority levels for suggestions"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class AnalysisSuggestion:
    """Individual analysis suggestion"""
    id: str
    type: str
    title: str
    description: str
    rationale: str
    priority: SuggestionPriority
    impact_score: float
    implementation_code: Optional[str] = None
    affected_columns: Optional[List[str]] = None
    estimated_improvement: Optional[str] = None
    confidence_score: float = 0.8


@dataclass
class AnalysisResult:
    """Complete analysis result"""
    analysis_type: AnalysisType
    suggestions: List[AnalysisSuggestion]
    summary: str
    metadata: Dict[str, Any]
    timestamp: datetime
    model_used: str
    total_cost: float


class PromptTemplates:
    """Structured prompt templates for different analysis types"""
    
    GENERAL_ANALYSIS = """
Analyze this dataset and provide comprehensive insights:

Dataset Overview:
{dataset_info}

Sample Data:
{data_sample}

Please provide:
1. Data quality assessment with specific issues
2. Feature engineering opportunities
3. Preprocessing recommendations
4. Potential challenges and solutions
5. Priority ranking of suggested actions

Format response as JSON with structure:
{{
    "summary": "brief overview",
    "suggestions": [
        {{
            "title": "suggestion title",
            "description": "detailed description",
            "rationale": "why this is important",
            "priority": "critical/high/medium/low",
            "impact_score": 0-1,
            "affected_columns": ["col1", "col2"],
            "implementation_code": "python code if applicable"
        }}
    ]
}}
"""
    
    FEATURE_ENGINEERING = """
Analyze this dataset for feature engineering opportunities:

Column Information:
{column_info}

Statistics:
{statistics}

Target Variable: {target_variable}

Provide feature engineering suggestions:
1. Polynomial features
2. Interaction terms
3. Binning strategies
4. Transformations (log, sqrt, etc.)
5. Date/time features
6. Text features
7. Domain-specific features

Format as JSON with specific, implementable suggestions.
"""
    
    ENCODING_STRATEGY = """
Recommend encoding strategies for categorical variables:

Categorical Columns:
{categorical_info}

Dataset Context:
{context}

For each categorical column, recommend:
1. Best encoding method (one-hot, label, target, etc.)
2. Handling of rare categories
3. Dealing with unknown categories
4. Dimensionality considerations
5. Implementation approach

Format as JSON with column-specific recommendations.
"""
    
    IMPUTATION_STRATEGY = """
Analyze missing data patterns and recommend imputation strategies:

Missing Data Summary:
{missing_data_info}

Column Correlations:
{correlations}

Data Types:
{data_types}

For each column with missing data:
1. Identify missing mechanism (MCAR/MAR/MNAR)
2. Recommend imputation method
3. Consider multivariate vs univariate approaches
4. Suggest validation strategy
5. Provide implementation code

Format as JSON with detailed, actionable recommendations.
"""
    
    DATA_QUALITY = """
Perform comprehensive data quality assessment:

Dataset Statistics:
{statistics}

Data Types:
{data_types}

Sample Issues:
{sample_issues}

Identify and prioritize:
1. Data integrity issues
2. Inconsistencies and anomalies
3. Validation rule violations
4. Standardization needs
5. Cleansing requirements

Format as JSON with specific issues and solutions.
"""


class AIAnalysisService:
    """
    Main service for AI-powered data analysis and recommendations
    """
    
    def __init__(self, openai_service: OpenAIService):
        """
        Initialize AI Analysis Service
        
        Args:
            openai_service: OpenAI service instance
        """
        self.openai_service = openai_service
        self.templates = PromptTemplates()
        self.suggestion_history: List[AnalysisResult] = []
        self.feedback_data: Dict[str, List[Dict]] = {}
    
    async def analyze_dataset(
        self,
        df: pd.DataFrame,
        analysis_type: AnalysisType = AnalysisType.GENERAL,
        target_column: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        model: str = ModelType.GPT_4_TURBO.value
    ) -> AnalysisResult:
        """
        Perform comprehensive dataset analysis
        
        Args:
            df: DataFrame to analyze
            analysis_type: Type of analysis to perform
            target_column: Target variable for supervised learning context
            context: Additional context for analysis
            model: OpenAI model to use
            
        Returns:
            Structured analysis result with suggestions
        """
        try:
            # Prepare dataset information
            dataset_info = self._prepare_dataset_info(df)
            
            # Generate appropriate prompt based on analysis type
            prompt = await self._generate_prompt(
                df, dataset_info, analysis_type, target_column, context
            )
            
            # Get AI analysis
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert data scientist specializing in data preprocessing, feature engineering, and machine learning. Provide detailed, actionable recommendations in JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = await self.openai_service.chat_completion(
                messages=messages,
                model=model,
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse and structure response
            analysis_result = self._parse_ai_response(
                response,
                analysis_type,
                model
            )
            
            # Apply ranking and filtering
            analysis_result = self._rank_suggestions(analysis_result, df)
            
            # Store in history
            self.suggestion_history.append(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Dataset analysis failed: {e}")
            raise
    
    def _prepare_dataset_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Prepare comprehensive dataset information for analysis"""
        info = {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.to_dict(),
            "missing_counts": df.isnull().sum().to_dict(),
            "missing_percentage": (df.isnull().sum() / len(df) * 100).to_dict(),
            "unique_counts": df.nunique().to_dict(),
            "memory_usage": df.memory_usage(deep=True).sum()
        }
        
        # Add statistical summaries for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            info["numeric_stats"] = df[numeric_cols].describe().to_dict()
        
        # Add categorical information
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            info["categorical_info"] = {
                col: {
                    "unique_values": df[col].nunique(),
                    "top_values": df[col].value_counts().head(5).to_dict()
                }
                for col in categorical_cols
            }
        
        return info
    
    async def _generate_prompt(
        self,
        df: pd.DataFrame,
        dataset_info: Dict[str, Any],
        analysis_type: AnalysisType,
        target_column: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate appropriate prompt based on analysis type"""
        
        # Get sample data (first 5 rows)
        data_sample = df.head(5).to_dict()
        
        if analysis_type == AnalysisType.GENERAL:
            return self.templates.GENERAL_ANALYSIS.format(
                dataset_info=json.dumps(dataset_info, indent=2),
                data_sample=json.dumps(data_sample, indent=2)
            )
        
        elif analysis_type == AnalysisType.FEATURE_ENGINEERING:
            return self.templates.FEATURE_ENGINEERING.format(
                column_info=json.dumps(dataset_info["dtypes"], indent=2),
                statistics=json.dumps(dataset_info.get("numeric_stats", {}), indent=2),
                target_variable=target_column or "Not specified"
            )
        
        elif analysis_type == AnalysisType.ENCODING_STRATEGY:
            categorical_info = dataset_info.get("categorical_info", {})
            return self.templates.ENCODING_STRATEGY.format(
                categorical_info=json.dumps(categorical_info, indent=2),
                context=json.dumps(context or {}, indent=2)
            )
        
        elif analysis_type == AnalysisType.IMPUTATION_STRATEGY:
            # Calculate correlations for numeric columns
            numeric_df = df.select_dtypes(include=[np.number])
            correlations = {}
            if not numeric_df.empty:
                corr_matrix = numeric_df.corr()
                correlations = corr_matrix.to_dict()
            
            return self.templates.IMPUTATION_STRATEGY.format(
                missing_data_info=json.dumps({
                    "counts": dataset_info["missing_counts"],
                    "percentages": dataset_info["missing_percentage"]
                }, indent=2),
                correlations=json.dumps(correlations, indent=2),
                data_types=json.dumps(dataset_info["dtypes"], indent=2)
            )
        
        elif analysis_type == AnalysisType.DATA_QUALITY:
            # Detect sample issues
            sample_issues = self._detect_data_quality_issues(df)
            
            return self.templates.DATA_QUALITY.format(
                statistics=json.dumps(dataset_info.get("numeric_stats", {}), indent=2),
                data_types=json.dumps(dataset_info["dtypes"], indent=2),
                sample_issues=json.dumps(sample_issues, indent=2)
            )
        
        else:
            # Default to general analysis
            return self.templates.GENERAL_ANALYSIS.format(
                dataset_info=json.dumps(dataset_info, indent=2),
                data_sample=json.dumps(data_sample, indent=2)
            )
    
    def _detect_data_quality_issues(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect common data quality issues"""
        issues = []
        
        # Check for duplicate rows
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            issues.append({
                "type": "duplicate_rows",
                "count": int(duplicate_count),
                "percentage": float(duplicate_count / len(df) * 100)
            })
        
        # Check for constant columns
        for col in df.columns:
            if df[col].nunique() == 1:
                issues.append({
                    "type": "constant_column",
                    "column": col,
                    "value": str(df[col].iloc[0])
                })
        
        # Check for high cardinality in categorical columns
        object_cols = df.select_dtypes(include=['object']).columns
        for col in object_cols:
            cardinality_ratio = df[col].nunique() / len(df)
            if cardinality_ratio > 0.5:
                issues.append({
                    "type": "high_cardinality",
                    "column": col,
                    "unique_values": int(df[col].nunique()),
                    "ratio": float(cardinality_ratio)
                })
        
        return issues
    
    def _parse_ai_response(
        self,
        response: Dict[str, Any],
        analysis_type: AnalysisType,
        model: str
    ) -> AnalysisResult:
        """Parse AI response into structured format"""
        try:
            # Extract content from response
            content = response["choices"][0]["message"]["content"]
            
            # Try to parse as JSON
            try:
                # Find JSON content in the response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    parsed_content = json.loads(json_match.group())
                else:
                    # Fallback to treating entire content as text
                    parsed_content = {"summary": content, "suggestions": []}
            except json.JSONDecodeError:
                # If JSON parsing fails, create basic structure
                parsed_content = {"summary": content, "suggestions": []}
            
            # Convert to suggestion objects
            suggestions = []
            for idx, sugg_data in enumerate(parsed_content.get("suggestions", [])):
                suggestion = AnalysisSuggestion(
                    id=f"{analysis_type.value}_{idx}_{datetime.now().timestamp()}",
                    type=analysis_type.value,
                    title=sugg_data.get("title", "Suggestion"),
                    description=sugg_data.get("description", ""),
                    rationale=sugg_data.get("rationale", ""),
                    priority=SuggestionPriority(sugg_data.get("priority", "medium")),
                    impact_score=float(sugg_data.get("impact_score", 0.5)),
                    implementation_code=sugg_data.get("implementation_code"),
                    affected_columns=sugg_data.get("affected_columns"),
                    estimated_improvement=sugg_data.get("estimated_improvement"),
                    confidence_score=float(sugg_data.get("confidence_score", 0.8))
                )
                suggestions.append(suggestion)
            
            # Create analysis result
            result = AnalysisResult(
                analysis_type=analysis_type,
                suggestions=suggestions,
                summary=parsed_content.get("summary", "Analysis completed"),
                metadata={
                    "raw_response": content,
                    "parsed_successfully": True
                },
                timestamp=datetime.now(),
                model_used=model,
                total_cost=response.get("cost_estimate", 0)
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            # Return basic result on parsing failure
            return AnalysisResult(
                analysis_type=analysis_type,
                suggestions=[],
                summary="Analysis completed but parsing failed",
                metadata={"error": str(e)},
                timestamp=datetime.now(),
                model_used=model,
                total_cost=response.get("cost_estimate", 0)
            )
    
    def _rank_suggestions(
        self,
        result: AnalysisResult,
        df: pd.DataFrame
    ) -> AnalysisResult:
        """Rank and filter suggestions based on relevance and impact"""
        
        # Calculate relevance scores based on dataset characteristics
        for suggestion in result.suggestions:
            relevance_score = self._calculate_relevance_score(suggestion, df)
            
            # Combine with impact score for final ranking
            suggestion.impact_score = (
                suggestion.impact_score * 0.7 +
                relevance_score * 0.3
            )
        
        # Sort suggestions by priority and impact score
        priority_order = {
            SuggestionPriority.CRITICAL: 0,
            SuggestionPriority.HIGH: 1,
            SuggestionPriority.MEDIUM: 2,
            SuggestionPriority.LOW: 3
        }
        
        result.suggestions.sort(
            key=lambda s: (priority_order[s.priority], -s.impact_score)
        )
        
        return result
    
    def _calculate_relevance_score(
        self,
        suggestion: AnalysisSuggestion,
        df: pd.DataFrame
    ) -> float:
        """Calculate relevance score for a suggestion based on dataset"""
        score = 0.5  # Base score
        
        # Check if affected columns exist
        if suggestion.affected_columns:
            existing_cols = set(df.columns)
            affected_cols = set(suggestion.affected_columns)
            if affected_cols.issubset(existing_cols):
                score += 0.2
            else:
                score -= 0.3
        
        # Boost score for suggestions addressing missing data if dataset has missing values
        if "imputation" in suggestion.type.lower() or "missing" in suggestion.title.lower():
            missing_ratio = df.isnull().sum().sum() / (df.shape[0] * df.shape[1])
            if missing_ratio > 0.1:
                score += 0.3
        
        # Boost score for encoding suggestions if dataset has categorical columns
        if "encoding" in suggestion.type.lower():
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            if len(categorical_cols) > 0:
                score += 0.2
        
        return max(0, min(1, score))  # Clamp between 0 and 1
    
    async def get_feature_engineering_suggestions(
        self,
        df: pd.DataFrame,
        target_column: Optional[str] = None,
        max_suggestions: int = 10
    ) -> List[AnalysisSuggestion]:
        """Get specific feature engineering suggestions"""
        result = await self.analyze_dataset(
            df,
            analysis_type=AnalysisType.FEATURE_ENGINEERING,
            target_column=target_column
        )
        return result.suggestions[:max_suggestions]
    
    async def get_encoding_recommendations(
        self,
        df: pd.DataFrame,
        categorical_columns: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Get encoding recommendations for categorical columns"""
        if categorical_columns is None:
            categorical_columns = df.select_dtypes(
                include=['object', 'category']
            ).columns.tolist()
        
        if not categorical_columns:
            return {}
        
        # Create subset DataFrame for analysis
        subset_df = df[categorical_columns]
        
        result = await self.analyze_dataset(
            subset_df,
            analysis_type=AnalysisType.ENCODING_STRATEGY
        )
        
        # Structure recommendations by column
        recommendations = {}
        for suggestion in result.suggestions:
            if suggestion.affected_columns:
                for col in suggestion.affected_columns:
                    if col not in recommendations:
                        recommendations[col] = {
                            "method": suggestion.title,
                            "rationale": suggestion.rationale,
                            "implementation": suggestion.implementation_code
                        }
        
        return recommendations
    
    async def get_imputation_strategies(
        self,
        df: pd.DataFrame,
        columns_with_missing: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Get imputation strategies for columns with missing data"""
        if columns_with_missing is None:
            columns_with_missing = df.columns[df.isnull().any()].tolist()
        
        if not columns_with_missing:
            return {}
        
        result = await self.analyze_dataset(
            df,
            analysis_type=AnalysisType.IMPUTATION_STRATEGY
        )
        
        # Structure strategies by column
        strategies = {}
        for suggestion in result.suggestions:
            if suggestion.affected_columns:
                for col in suggestion.affected_columns:
                    if col in columns_with_missing:
                        strategies[col] = {
                            "method": suggestion.title,
                            "rationale": suggestion.rationale,
                            "implementation": suggestion.implementation_code,
                            "priority": suggestion.priority.value
                        }
        
        return strategies
    
    def record_feedback(
        self,
        suggestion_id: str,
        feedback_type: str,  # "positive" or "negative"
        comment: Optional[str] = None
    ):
        """Record user feedback for a suggestion"""
        feedback = {
            "suggestion_id": suggestion_id,
            "type": feedback_type,
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        }
        
        if suggestion_id not in self.feedback_data:
            self.feedback_data[suggestion_id] = []
        
        self.feedback_data[suggestion_id].append(feedback)
        logger.info(f"Feedback recorded for suggestion {suggestion_id}: {feedback_type}")
    
    def get_suggestion_history(
        self,
        analysis_type: Optional[AnalysisType] = None,
        limit: int = 10
    ) -> List[AnalysisResult]:
        """Get history of analysis suggestions"""
        history = self.suggestion_history
        
        if analysis_type:
            history = [r for r in history if r.analysis_type == analysis_type]
        
        return history[-limit:]
    
    def export_suggestions(
        self,
        result: AnalysisResult,
        format: str = "json"
    ) -> str:
        """Export suggestions in specified format"""
        if format == "json":
            return json.dumps({
                "analysis_type": result.analysis_type.value,
                "summary": result.summary,
                "suggestions": [asdict(s) for s in result.suggestions],
                "metadata": result.metadata,
                "timestamp": result.timestamp.isoformat(),
                "model_used": result.model_used,
                "total_cost": result.total_cost
            }, indent=2, default=str)
        
        elif format == "markdown":
            md = f"# {result.analysis_type.value.replace('_', ' ').title()} Analysis\n\n"
            md += f"**Summary:** {result.summary}\n\n"
            md += f"**Date:** {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            md += f"**Model:** {result.model_used}\n\n"
            
            md += "## Suggestions\n\n"
            for i, sugg in enumerate(result.suggestions, 1):
                md += f"### {i}. {sugg.title}\n"
                md += f"**Priority:** {sugg.priority.value}\n"
                md += f"**Impact Score:** {sugg.impact_score:.2f}\n\n"
                md += f"{sugg.description}\n\n"
                md += f"**Rationale:** {sugg.rationale}\n\n"
                
                if sugg.implementation_code:
                    md += "**Implementation:**\n```python\n"
                    md += sugg.implementation_code
                    md += "\n```\n\n"
            
            return md
        
        else:
            raise ValueError(f"Unsupported export format: {format}")