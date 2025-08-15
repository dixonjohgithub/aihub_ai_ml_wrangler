"""
Test suite for AI Analysis Service
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import json

from backend.app.services.ai_analysis_service import (
    AIAnalysisService,
    AnalysisType,
    SuggestionPriority,
    AnalysisSuggestion,
    AnalysisResult
)


class TestAIAnalysisService:
    """Test AI Analysis Service"""
    
    @pytest.fixture
    def mock_openai_service(self):
        """Create mock OpenAI service"""
        mock = AsyncMock()
        mock.chat_completion = AsyncMock()
        return mock
    
    @pytest.fixture
    def ai_service(self, mock_openai_service):
        """Create AI Analysis Service instance"""
        return AIAnalysisService(mock_openai_service)
    
    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame for testing"""
        return pd.DataFrame({
            'numeric_col': [1, 2, 3, 4, 5, np.nan],
            'categorical_col': ['A', 'B', 'A', 'C', 'B', 'A'],
            'text_col': ['text1', 'text2', 'text3', 'text4', 'text5', None],
            'target': [0, 1, 0, 1, 1, 0]
        })
    
    def test_prepare_dataset_info(self, ai_service, sample_df):
        """Test dataset info preparation"""
        info = ai_service._prepare_dataset_info(sample_df)
        
        assert info['shape'] == (6, 4)
        assert 'numeric_col' in info['columns']
        assert info['missing_counts']['numeric_col'] == 1
        assert info['missing_counts']['text_col'] == 1
        assert 'numeric_stats' in info
        assert 'categorical_info' in info
    
    def test_detect_data_quality_issues(self, ai_service):
        """Test data quality issue detection"""
        # Create DataFrame with issues
        df = pd.DataFrame({
            'constant_col': [1, 1, 1, 1],
            'high_card_col': ['a', 'b', 'c', 'd'],
            'normal_col': [1, 2, 3, 4]
        })
        
        # Add duplicate row
        df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
        
        issues = ai_service._detect_data_quality_issues(df)
        
        # Check for detected issues
        issue_types = [issue['type'] for issue in issues]
        assert 'duplicate_rows' in issue_types
        assert 'constant_column' in issue_types
        assert 'high_cardinality' in issue_types
    
    @pytest.mark.asyncio
    async def test_analyze_dataset_general(self, ai_service, mock_openai_service, sample_df):
        """Test general dataset analysis"""
        # Mock OpenAI response
        mock_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "summary": "Dataset analysis complete",
                        "suggestions": [
                            {
                                "title": "Handle missing values",
                                "description": "Impute missing values in numeric_col",
                                "rationale": "Missing data can affect model performance",
                                "priority": "high",
                                "impact_score": 0.8,
                                "affected_columns": ["numeric_col"]
                            }
                        ]
                    })
                }
            }],
            "cost_estimate": 0.05
        }
        mock_openai_service.chat_completion.return_value = mock_response
        
        # Perform analysis
        result = await ai_service.analyze_dataset(
            df=sample_df,
            analysis_type=AnalysisType.GENERAL
        )
        
        assert result.analysis_type == AnalysisType.GENERAL
        assert len(result.suggestions) == 1
        assert result.suggestions[0].title == "Handle missing values"
        assert result.suggestions[0].priority == SuggestionPriority.HIGH
        assert result.total_cost == 0.05
    
    @pytest.mark.asyncio
    async def test_get_feature_engineering_suggestions(self, ai_service, mock_openai_service, sample_df):
        """Test feature engineering suggestions"""
        # Mock OpenAI response
        mock_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "summary": "Feature engineering analysis",
                        "suggestions": [
                            {
                                "title": "Create interaction features",
                                "description": "Create interaction between numeric_col and categorical_col",
                                "rationale": "May capture non-linear relationships",
                                "priority": "medium",
                                "impact_score": 0.6,
                                "implementation_code": "df['interaction'] = df['numeric_col'] * pd.get_dummies(df['categorical_col'])"
                            }
                        ]
                    })
                }
            }],
            "cost_estimate": 0.04
        }
        mock_openai_service.chat_completion.return_value = mock_response
        
        # Get suggestions
        suggestions = await ai_service.get_feature_engineering_suggestions(
            df=sample_df,
            target_column='target'
        )
        
        assert len(suggestions) > 0
        assert suggestions[0].title == "Create interaction features"
        assert suggestions[0].implementation_code is not None
    
    @pytest.mark.asyncio
    async def test_get_encoding_recommendations(self, ai_service, mock_openai_service, sample_df):
        """Test encoding recommendations"""
        # Mock OpenAI response
        mock_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "summary": "Encoding analysis",
                        "suggestions": [
                            {
                                "title": "One-hot encoding",
                                "description": "Use one-hot encoding for categorical_col",
                                "rationale": "Low cardinality categorical variable",
                                "priority": "high",
                                "impact_score": 0.7,
                                "affected_columns": ["categorical_col"],
                                "implementation_code": "pd.get_dummies(df['categorical_col'])"
                            }
                        ]
                    })
                }
            }],
            "cost_estimate": 0.03
        }
        mock_openai_service.chat_completion.return_value = mock_response
        
        # Get recommendations
        recommendations = await ai_service.get_encoding_recommendations(
            df=sample_df,
            categorical_columns=['categorical_col']
        )
        
        assert 'categorical_col' in recommendations
        assert recommendations['categorical_col']['method'] == "One-hot encoding"
    
    @pytest.mark.asyncio
    async def test_get_imputation_strategies(self, ai_service, mock_openai_service, sample_df):
        """Test imputation strategy recommendations"""
        # Mock OpenAI response
        mock_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "summary": "Imputation analysis",
                        "suggestions": [
                            {
                                "title": "Mean imputation",
                                "description": "Use mean imputation for numeric_col",
                                "rationale": "MCAR pattern detected",
                                "priority": "high",
                                "impact_score": 0.8,
                                "affected_columns": ["numeric_col"],
                                "implementation_code": "df['numeric_col'].fillna(df['numeric_col'].mean())"
                            }
                        ]
                    })
                }
            }],
            "cost_estimate": 0.03
        }
        mock_openai_service.chat_completion.return_value = mock_response
        
        # Get strategies
        strategies = await ai_service.get_imputation_strategies(
            df=sample_df,
            columns_with_missing=['numeric_col', 'text_col']
        )
        
        assert 'numeric_col' in strategies
        assert strategies['numeric_col']['method'] == "Mean imputation"
        assert strategies['numeric_col']['priority'] == "high"
    
    def test_record_feedback(self, ai_service):
        """Test feedback recording"""
        # Record feedback
        ai_service.record_feedback(
            suggestion_id="test_123",
            feedback_type="positive",
            comment="Very helpful"
        )
        
        assert "test_123" in ai_service.feedback_data
        assert len(ai_service.feedback_data["test_123"]) == 1
        assert ai_service.feedback_data["test_123"][0]["type"] == "positive"
    
    def test_ranking_suggestions(self, ai_service, sample_df):
        """Test suggestion ranking"""
        # Create test suggestions
        suggestions = [
            AnalysisSuggestion(
                id="1",
                type="test",
                title="Low priority",
                description="",
                rationale="",
                priority=SuggestionPriority.LOW,
                impact_score=0.5,
                confidence_score=0.8
            ),
            AnalysisSuggestion(
                id="2",
                type="test",
                title="High priority",
                description="",
                rationale="",
                priority=SuggestionPriority.HIGH,
                impact_score=0.7,
                confidence_score=0.9
            ),
            AnalysisSuggestion(
                id="3",
                type="test",
                title="Critical priority",
                description="",
                rationale="",
                priority=SuggestionPriority.CRITICAL,
                impact_score=0.6,
                confidence_score=0.85
            )
        ]
        
        result = AnalysisResult(
            analysis_type=AnalysisType.GENERAL,
            suggestions=suggestions,
            summary="Test",
            metadata={},
            timestamp=datetime.now(),
            model_used="gpt-4",
            total_cost=0.1
        )
        
        # Rank suggestions
        ranked_result = ai_service._rank_suggestions(result, sample_df)
        
        # Check order (Critical > High > Low)
        assert ranked_result.suggestions[0].priority == SuggestionPriority.CRITICAL
        assert ranked_result.suggestions[1].priority == SuggestionPriority.HIGH
        assert ranked_result.suggestions[2].priority == SuggestionPriority.LOW
    
    def test_export_suggestions_json(self, ai_service):
        """Test exporting suggestions as JSON"""
        result = AnalysisResult(
            analysis_type=AnalysisType.GENERAL,
            suggestions=[
                AnalysisSuggestion(
                    id="1",
                    type="test",
                    title="Test suggestion",
                    description="Description",
                    rationale="Rationale",
                    priority=SuggestionPriority.HIGH,
                    impact_score=0.8,
                    confidence_score=0.9
                )
            ],
            summary="Test summary",
            metadata={"test": "data"},
            timestamp=datetime.now(),
            model_used="gpt-4",
            total_cost=0.05
        )
        
        exported = ai_service.export_suggestions(result, format="json")
        parsed = json.loads(exported)
        
        assert parsed["analysis_type"] == "general"
        assert parsed["summary"] == "Test summary"
        assert len(parsed["suggestions"]) == 1
        assert parsed["total_cost"] == 0.05
    
    def test_export_suggestions_markdown(self, ai_service):
        """Test exporting suggestions as Markdown"""
        result = AnalysisResult(
            analysis_type=AnalysisType.GENERAL,
            suggestions=[
                AnalysisSuggestion(
                    id="1",
                    type="test",
                    title="Test suggestion",
                    description="Description",
                    rationale="Rationale",
                    priority=SuggestionPriority.HIGH,
                    impact_score=0.8,
                    confidence_score=0.9,
                    implementation_code="print('test')"
                )
            ],
            summary="Test summary",
            metadata={},
            timestamp=datetime.now(),
            model_used="gpt-4",
            total_cost=0.05
        )
        
        exported = ai_service.export_suggestions(result, format="markdown")
        
        assert "# General Analysis" in exported
        assert "Test suggestion" in exported
        assert "```python" in exported
        assert "print('test')" in exported
    
    def test_suggestion_history(self, ai_service):
        """Test suggestion history management"""
        # Add some results to history
        for i in range(3):
            result = AnalysisResult(
                analysis_type=AnalysisType.GENERAL,
                suggestions=[],
                summary=f"Test {i}",
                metadata={},
                timestamp=datetime.now(),
                model_used="gpt-4",
                total_cost=0.01
            )
            ai_service.suggestion_history.append(result)
        
        # Get history
        history = ai_service.get_suggestion_history(limit=2)
        
        assert len(history) == 2
        assert history[-1].summary == "Test 2"
        
        # Get filtered history
        ai_service.suggestion_history.append(
            AnalysisResult(
                analysis_type=AnalysisType.FEATURE_ENGINEERING,
                suggestions=[],
                summary="Feature test",
                metadata={},
                timestamp=datetime.now(),
                model_used="gpt-4",
                total_cost=0.01
            )
        )
        
        fe_history = ai_service.get_suggestion_history(
            analysis_type=AnalysisType.FEATURE_ENGINEERING
        )
        
        assert len(fe_history) == 1
        assert fe_history[0].summary == "Feature test"