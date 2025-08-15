"""
File: ai_analysis_api.py

Overview:
FastAPI endpoints for AI-powered analysis service providing intelligent
dataset insights and recommendations.

Purpose:
Exposes REST API for accessing AI analysis features including feature engineering,
encoding strategies, and imputation recommendations.

Dependencies:
- fastapi: Web framework
- backend.app.services.ai_analysis_service: AI analysis service
- backend.app.services.openai_service: OpenAI service

Last Modified: 2025-08-15
Author: Claude
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import pandas as pd
import json
import io
import logging

from backend.app.services.ai_analysis_service import (
    AIAnalysisService,
    AnalysisType,
    AnalysisResult,
    AnalysisSuggestion
)
from backend.app.services.openai_service import get_openai_service, OpenAIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai-analysis", tags=["ai-analysis"])


# Request/Response models
class DatasetAnalysisRequest(BaseModel):
    """Dataset analysis request"""
    data: Dict[str, List[Any]] = Field(..., description="Dataset as dictionary")
    analysis_type: str = Field("general", description="Type of analysis")
    target_column: Optional[str] = Field(None, description="Target column for supervised learning")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    model: str = Field("gpt-4-turbo-preview", description="Model to use")


class FeatureEngineeringRequest(BaseModel):
    """Feature engineering request"""
    data: Dict[str, List[Any]] = Field(..., description="Dataset as dictionary")
    target_column: Optional[str] = Field(None, description="Target column")
    max_suggestions: int = Field(10, ge=1, le=50, description="Maximum suggestions")


class EncodingRecommendationRequest(BaseModel):
    """Encoding recommendation request"""
    data: Dict[str, List[Any]] = Field(..., description="Dataset as dictionary")
    categorical_columns: Optional[List[str]] = Field(None, description="Categorical columns to analyze")


class ImputationStrategyRequest(BaseModel):
    """Imputation strategy request"""
    data: Dict[str, List[Any]] = Field(..., description="Dataset as dictionary")
    columns_with_missing: Optional[List[str]] = Field(None, description="Columns to analyze")


class FeedbackRequest(BaseModel):
    """Feedback request"""
    suggestion_id: str = Field(..., description="Suggestion ID")
    feedback_type: str = Field(..., description="Feedback type (positive/negative)")
    comment: Optional[str] = Field(None, description="Optional comment")


class SuggestionResponse(BaseModel):
    """Suggestion response model"""
    id: str
    type: str
    title: str
    description: str
    rationale: str
    priority: str
    impact_score: float
    confidence_score: float
    implementation_code: Optional[str]
    affected_columns: Optional[List[str]]
    estimated_improvement: Optional[str]


class AnalysisResponse(BaseModel):
    """Analysis response model"""
    analysis_type: str
    summary: str
    suggestions: List[SuggestionResponse]
    metadata: Dict[str, Any]
    timestamp: str
    model_used: str
    total_cost: float


# Dependency to get AI Analysis Service
async def get_ai_analysis_service(
    openai_service: OpenAIService = Depends(get_openai_service)
) -> AIAnalysisService:
    """Get or create AI Analysis Service instance"""
    return AIAnalysisService(openai_service)


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_dataset(
    request: DatasetAnalysisRequest,
    ai_service: AIAnalysisService = Depends(get_ai_analysis_service)
) -> Dict[str, Any]:
    """
    Perform comprehensive AI-powered dataset analysis
    
    Returns:
        Structured analysis with suggestions and recommendations
    """
    try:
        # Convert data to DataFrame
        df = pd.DataFrame(request.data)
        
        # Parse analysis type
        try:
            analysis_type = AnalysisType(request.analysis_type)
        except ValueError:
            analysis_type = AnalysisType.GENERAL
        
        # Perform analysis
        result = await ai_service.analyze_dataset(
            df=df,
            analysis_type=analysis_type,
            target_column=request.target_column,
            context=request.context,
            model=request.model
        )
        
        # Convert to response format
        return {
            "analysis_type": result.analysis_type.value,
            "summary": result.summary,
            "suggestions": [
                {
                    "id": s.id,
                    "type": s.type,
                    "title": s.title,
                    "description": s.description,
                    "rationale": s.rationale,
                    "priority": s.priority.value,
                    "impact_score": s.impact_score,
                    "confidence_score": s.confidence_score,
                    "implementation_code": s.implementation_code,
                    "affected_columns": s.affected_columns,
                    "estimated_improvement": s.estimated_improvement
                }
                for s in result.suggestions
            ],
            "metadata": result.metadata,
            "timestamp": result.timestamp.isoformat(),
            "model_used": result.model_used,
            "total_cost": result.total_cost
        }
        
    except Exception as e:
        logger.error(f"Dataset analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-file")
async def analyze_uploaded_file(
    file: UploadFile = File(...),
    analysis_type: str = "general",
    target_column: Optional[str] = None,
    ai_service: AIAnalysisService = Depends(get_ai_analysis_service)
) -> Dict[str, Any]:
    """
    Analyze an uploaded CSV file
    
    Args:
        file: Uploaded CSV file
        analysis_type: Type of analysis to perform
        target_column: Optional target column
        
    Returns:
        Analysis results
    """
    try:
        # Read file content
        content = await file.read()
        
        # Parse CSV
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        # Limit size for analysis
        if len(df) > 10000:
            df = df.sample(n=10000, random_state=42)
        
        # Parse analysis type
        try:
            analysis_type_enum = AnalysisType(analysis_type)
        except ValueError:
            analysis_type_enum = AnalysisType.GENERAL
        
        # Perform analysis
        result = await ai_service.analyze_dataset(
            df=df,
            analysis_type=analysis_type_enum,
            target_column=target_column
        )
        
        return {
            "success": True,
            "data": {
                "analysis_type": result.analysis_type.value,
                "summary": result.summary,
                "suggestions": [
                    {
                        "id": s.id,
                        "type": s.type,
                        "title": s.title,
                        "description": s.description,
                        "rationale": s.rationale,
                        "priority": s.priority.value,
                        "impact_score": s.impact_score,
                        "confidence_score": s.confidence_score,
                        "implementation_code": s.implementation_code,
                        "affected_columns": s.affected_columns,
                        "estimated_improvement": s.estimated_improvement
                    }
                    for s in result.suggestions
                ],
                "metadata": result.metadata,
                "timestamp": result.timestamp.isoformat(),
                "model_used": result.model_used,
                "total_cost": result.total_cost
            }
        }
        
    except Exception as e:
        logger.error(f"File analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feature-engineering")
async def get_feature_engineering_suggestions(
    request: FeatureEngineeringRequest,
    ai_service: AIAnalysisService = Depends(get_ai_analysis_service)
) -> Dict[str, Any]:
    """
    Get AI-powered feature engineering suggestions
    
    Returns:
        List of feature engineering suggestions
    """
    try:
        # Convert data to DataFrame
        df = pd.DataFrame(request.data)
        
        # Get suggestions
        suggestions = await ai_service.get_feature_engineering_suggestions(
            df=df,
            target_column=request.target_column,
            max_suggestions=request.max_suggestions
        )
        
        return {
            "success": True,
            "data": {
                "suggestions": [
                    {
                        "id": s.id,
                        "title": s.title,
                        "description": s.description,
                        "rationale": s.rationale,
                        "priority": s.priority.value,
                        "impact_score": s.impact_score,
                        "implementation_code": s.implementation_code,
                        "affected_columns": s.affected_columns
                    }
                    for s in suggestions
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Feature engineering analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/encoding-recommendations")
async def get_encoding_recommendations(
    request: EncodingRecommendationRequest,
    ai_service: AIAnalysisService = Depends(get_ai_analysis_service)
) -> Dict[str, Any]:
    """
    Get encoding recommendations for categorical columns
    
    Returns:
        Column-specific encoding recommendations
    """
    try:
        # Convert data to DataFrame
        df = pd.DataFrame(request.data)
        
        # Get recommendations
        recommendations = await ai_service.get_encoding_recommendations(
            df=df,
            categorical_columns=request.categorical_columns
        )
        
        return {
            "success": True,
            "data": {
                "recommendations": recommendations
            }
        }
        
    except Exception as e:
        logger.error(f"Encoding recommendation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/imputation-strategies")
async def get_imputation_strategies(
    request: ImputationStrategyRequest,
    ai_service: AIAnalysisService = Depends(get_ai_analysis_service)
) -> Dict[str, Any]:
    """
    Get imputation strategies for columns with missing data
    
    Returns:
        Column-specific imputation strategies
    """
    try:
        # Convert data to DataFrame
        df = pd.DataFrame(request.data)
        
        # Get strategies
        strategies = await ai_service.get_imputation_strategies(
            df=df,
            columns_with_missing=request.columns_with_missing
        )
        
        return {
            "success": True,
            "data": {
                "strategies": strategies
            }
        }
        
    except Exception as e:
        logger.error(f"Imputation strategy analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    ai_service: AIAnalysisService = Depends(get_ai_analysis_service)
) -> Dict[str, Any]:
    """
    Submit feedback for a suggestion
    
    Returns:
        Confirmation of feedback submission
    """
    try:
        ai_service.record_feedback(
            suggestion_id=request.suggestion_id,
            feedback_type=request.feedback_type,
            comment=request.comment
        )
        
        return {
            "success": True,
            "message": "Feedback recorded successfully"
        }
        
    except Exception as e:
        logger.error(f"Feedback submission failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_suggestion_history(
    analysis_type: Optional[str] = None,
    limit: int = 10,
    ai_service: AIAnalysisService = Depends(get_ai_analysis_service)
) -> Dict[str, Any]:
    """
    Get history of analysis suggestions
    
    Args:
        analysis_type: Filter by analysis type
        limit: Maximum number of results
        
    Returns:
        List of historical analysis results
    """
    try:
        # Parse analysis type if provided
        analysis_type_enum = None
        if analysis_type:
            try:
                analysis_type_enum = AnalysisType(analysis_type)
            except ValueError:
                pass
        
        # Get history
        history = ai_service.get_suggestion_history(
            analysis_type=analysis_type_enum,
            limit=limit
        )
        
        return {
            "success": True,
            "data": {
                "history": [
                    {
                        "analysis_type": result.analysis_type.value,
                        "summary": result.summary,
                        "suggestion_count": len(result.suggestions),
                        "timestamp": result.timestamp.isoformat(),
                        "model_used": result.model_used,
                        "total_cost": result.total_cost
                    }
                    for result in history
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/{format}")
async def export_suggestions(
    format: str,
    analysis_index: int = -1,
    ai_service: AIAnalysisService = Depends(get_ai_analysis_service)
) -> Dict[str, Any]:
    """
    Export suggestions in specified format
    
    Args:
        format: Export format (json or markdown)
        analysis_index: Index of analysis to export (-1 for latest)
        
    Returns:
        Exported content
    """
    try:
        # Get analysis result
        history = ai_service.get_suggestion_history(limit=abs(analysis_index) + 1)
        
        if not history:
            raise HTTPException(status_code=404, detail="No analysis history found")
        
        result = history[analysis_index]
        
        # Export in requested format
        exported = ai_service.export_suggestions(result, format=format)
        
        return {
            "success": True,
            "data": {
                "format": format,
                "content": exported
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis-types")
async def get_analysis_types() -> Dict[str, Any]:
    """
    Get available analysis types
    
    Returns:
        List of available analysis types with descriptions
    """
    types = {
        AnalysisType.GENERAL.value: {
            "name": "General Analysis",
            "description": "Comprehensive dataset analysis with quality assessment and recommendations"
        },
        AnalysisType.FEATURE_ENGINEERING.value: {
            "name": "Feature Engineering",
            "description": "Suggestions for creating new features and transformations"
        },
        AnalysisType.ENCODING_STRATEGY.value: {
            "name": "Encoding Strategy",
            "description": "Recommendations for encoding categorical variables"
        },
        AnalysisType.IMPUTATION_STRATEGY.value: {
            "name": "Imputation Strategy",
            "description": "Strategies for handling missing data"
        },
        AnalysisType.DATA_QUALITY.value: {
            "name": "Data Quality",
            "description": "Assessment of data quality issues and cleansing recommendations"
        },
        AnalysisType.CORRELATION_ANALYSIS.value: {
            "name": "Correlation Analysis",
            "description": "Analysis of feature correlations and multicollinearity"
        },
        AnalysisType.OUTLIER_DETECTION.value: {
            "name": "Outlier Detection",
            "description": "Detection and handling strategies for outliers"
        }
    }
    
    return {
        "success": True,
        "data": types
    }