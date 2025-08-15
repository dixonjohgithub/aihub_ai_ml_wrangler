"""
Test suite for correlation service
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import json

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.correlation_service import (
    CorrelationAnalyzer,
    CorrelationType,
    CorrelationConfig,
    CorrelationResult
)


class TestCorrelationService:
    """Test suite for CorrelationAnalyzer"""
    
    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame for testing"""
        np.random.seed(42)
        n = 100
        df = pd.DataFrame({
            'feature_1': np.random.randn(n),
            'feature_2': np.random.randn(n),
            'feature_3': np.random.randn(n) * 2 + 1,
            'correlated': np.random.randn(n),
            'highly_correlated': np.zeros(n),  # Will be correlated with 'correlated'
            'categorical': np.random.choice(['A', 'B', 'C'], n),
            'binary': np.random.choice([0, 1], n)
        })
        # Create high correlation
        df['highly_correlated'] = df['correlated'] * 0.95 + np.random.randn(n) * 0.1
        return df
    
    @pytest.fixture
    def analyzer(self):
        """Create CorrelationAnalyzer instance"""
        return CorrelationAnalyzer()
    
    def test_initialization(self, analyzer):
        """Test analyzer initialization"""
        assert analyzer is not None
        assert analyzer.analysis_history == []
        assert analyzer.eda_instance is None
    
    def test_pearson_correlation(self, analyzer, sample_df):
        """Test Pearson correlation analysis"""
        config = CorrelationConfig(
            method=CorrelationType.PEARSON,
            threshold=0.8
        )
        
        result = analyzer.analyze_correlations(sample_df, config)
        
        assert isinstance(result, CorrelationResult)
        assert result.correlation_matrix is not None
        assert len(result.correlation_matrix) == len(sample_df.select_dtypes(include=[np.number]).columns)
        
        # Check for high correlations
        assert len(result.high_correlations) > 0
        # Should detect correlation between 'correlated' and 'highly_correlated'
        pairs = [(c[0], c[1]) for c in result.high_correlations]
        assert ('correlated', 'highly_correlated') in pairs or ('highly_correlated', 'correlated') in pairs
    
    def test_spearman_correlation(self, analyzer, sample_df):
        """Test Spearman correlation analysis"""
        config = CorrelationConfig(
            method=CorrelationType.SPEARMAN,
            threshold=0.7
        )
        
        result = analyzer.analyze_correlations(sample_df, config)
        
        assert result.correlation_matrix is not None
        assert result.metadata['method'] == 'spearman'
    
    def test_kendall_correlation(self, analyzer, sample_df):
        """Test Kendall correlation analysis"""
        config = CorrelationConfig(
            method=CorrelationType.KENDALL,
            threshold=0.6
        )
        
        result = analyzer.analyze_correlations(sample_df, config)
        
        assert result.correlation_matrix is not None
        assert result.metadata['method'] == 'kendall'
    
    @patch('app.services.correlation_service.EDA')
    def test_vif_calculation(self, mock_eda_class, analyzer, sample_df):
        """Test VIF calculation"""
        # Mock EDA instance
        mock_eda = MagicMock()
        mock_eda.calculate_vif.return_value = {
            'feature_1': 1.2,
            'feature_2': 1.5,
            'highly_correlated': 15.0  # High VIF
        }
        mock_eda_class.return_value = mock_eda
        
        vif_scores = analyzer.calculate_vif(sample_df, threshold=10.0)
        
        assert 'highly_correlated' in vif_scores
        assert vif_scores['highly_correlated'] == 15.0
    
    @patch('app.services.correlation_service.EDA')
    def test_multicollinearity_detection(self, mock_eda_class, analyzer, sample_df):
        """Test multicollinearity detection"""
        # Mock EDA instance
        mock_eda = MagicMock()
        mock_eda.detect_multicollinearity.return_value = {
            'high_correlations': [
                {'feature1': 'correlated', 'feature2': 'highly_correlated', 'correlation': 0.95}
            ],
            'high_vif': {'highly_correlated': 15.0},
            'recommendations': ['highly_correlated']
        }
        mock_eda_class.return_value = mock_eda
        
        result = analyzer.detect_multicollinearity(sample_df)
        
        assert 'high_correlations' in result
        assert 'high_vif' in result
        assert 'recommendations' in result
        assert len(result['recommendations']) > 0
    
    def test_feature_importance_with_target(self, analyzer, sample_df):
        """Test feature importance calculation with target"""
        # Add target column
        sample_df['target'] = sample_df['feature_1'] * 2 + np.random.randn(len(sample_df)) * 0.1
        
        config = CorrelationConfig(
            method=CorrelationType.PEARSON,
            threshold=0.7
        )
        
        result = analyzer.analyze_correlations(sample_df, config, target_column='target')
        
        assert result.feature_importance is not None
        assert 'feature_1' in result.feature_importance
        # feature_1 should have highest importance as it's directly related to target
        importance_values = list(result.feature_importance.values())
        assert result.feature_importance['feature_1'] == max(importance_values)
    
    def test_correlation_clustering(self, analyzer, sample_df):
        """Test hierarchical clustering of features"""
        config = CorrelationConfig(
            method=CorrelationType.PEARSON,
            threshold=0.5
        )
        
        result = analyzer.analyze_correlations(sample_df, config)
        
        # Clustering might fail due to missing scipy, but should handle gracefully
        assert result.clustering is not None or result.clustering == {}
    
    def test_recommendations_generation(self, analyzer, sample_df):
        """Test recommendation generation"""
        config = CorrelationConfig(
            method=CorrelationType.PEARSON,
            threshold=0.8
        )
        
        result = analyzer.analyze_correlations(sample_df, config)
        
        assert result.recommendations is not None
        assert len(result.recommendations) > 0
        # Should recommend removing highly correlated features
        assert any('multicollinearity' in rec.lower() for rec in result.recommendations)
    
    def test_categorical_correlation(self, analyzer):
        """Test Cramér's V for categorical variables"""
        # Create DataFrame with categorical variables
        df = pd.DataFrame({
            'cat1': ['A', 'B', 'A', 'C', 'B', 'A'] * 10,
            'cat2': ['X', 'Y', 'X', 'Z', 'Y', 'X'] * 10,
            'cat3': ['P', 'Q', 'P', 'P', 'Q', 'P'] * 10
        })
        
        config = CorrelationConfig(
            method=CorrelationType.CRAMERS_V,
            threshold=0.5
        )
        
        # This should handle categorical correlations
        result = analyzer.analyze_correlations(df, config)
        
        assert result.correlation_matrix is not None
    
    @patch('app.services.correlation_service.EDA')
    def test_correlation_export(self, mock_eda_class, analyzer, sample_df, tmp_path):
        """Test correlation matrix export"""
        # Mock EDA instance
        mock_eda = MagicMock()
        mock_eda_class.return_value = mock_eda
        
        export_path = tmp_path / "correlation_matrix.csv"
        analyzer.export_correlation_csv(sample_df, str(export_path))
        
        mock_eda.export_correlation_csv.assert_called_once()
    
    def test_correlation_change_analysis(self, analyzer):
        """Test correlation change analysis between two datasets"""
        np.random.seed(42)
        n = 50
        
        # Create before and after DataFrames
        df_before = pd.DataFrame({
            'a': np.random.randn(n),
            'b': np.random.randn(n),
            'c': np.random.randn(n)
        })
        
        df_after = df_before.copy()
        df_after['b'] = df_after['a'] * 0.8 + np.random.randn(n) * 0.2  # Increase correlation
        
        changes = analyzer.correlation_change_analysis(df_before, df_after, threshold=0.1)
        
        assert 'significant_changes' in changes
        assert 'max_change' in changes
        assert 'mean_change' in changes
        assert len(changes['significant_changes']) > 0
    
    def test_feature_relationships(self, analyzer, sample_df):
        """Test getting relationships for specific feature"""
        relationships = analyzer.get_feature_relationships(sample_df, 'correlated', top_n=3)
        
        assert 'feature' in relationships
        assert relationships['feature'] == 'correlated'
        assert 'top_correlations' in relationships
        assert 'statistics' in relationships
        
        # Should find high correlation with 'highly_correlated'
        assert 'highly_correlated' in relationships['top_correlations']
    
    def test_export_formats(self, analyzer, sample_df):
        """Test different export formats"""
        config = CorrelationConfig(
            method=CorrelationType.PEARSON,
            threshold=0.7
        )
        
        result = analyzer.analyze_correlations(sample_df, config)
        
        # Test CSV export
        csv_export = analyzer.export_correlation_matrix(result.correlation_matrix, format='csv')
        assert isinstance(csv_export, str)
        assert ',' in csv_export
        
        # Test JSON export
        json_export = analyzer.export_correlation_matrix(result.correlation_matrix, format='json')
        assert isinstance(json_export, str)
        parsed = json.loads(json_export)
        assert 'data' in parsed or 'columns' in parsed
        
        # Test HTML export
        html_export = analyzer.export_correlation_matrix(result.correlation_matrix, format='html')
        assert isinstance(html_export, str)
        assert '<table' in html_export
    
    def test_analysis_history(self, analyzer, sample_df):
        """Test analysis history tracking"""
        config = CorrelationConfig(
            method=CorrelationType.PEARSON,
            threshold=0.7
        )
        
        # Perform multiple analyses
        result1 = analyzer.analyze_correlations(sample_df, config)
        result2 = analyzer.analyze_correlations(sample_df, config)
        
        assert len(analyzer.analysis_history) == 2
        assert analyzer.analysis_history[0] == result1
        assert analyzer.analysis_history[1] == result2
    
    def test_empty_dataframe(self, analyzer):
        """Test handling of empty DataFrame"""
        empty_df = pd.DataFrame()
        config = CorrelationConfig(method=CorrelationType.PEARSON)
        
        with pytest.raises(Exception):
            analyzer.analyze_correlations(empty_df, config)
    
    def test_single_column_dataframe(self, analyzer):
        """Test handling of single column DataFrame"""
        single_col_df = pd.DataFrame({'a': [1, 2, 3, 4, 5]})
        config = CorrelationConfig(method=CorrelationType.PEARSON)
        
        result = analyzer.analyze_correlations(single_col_df, config)
        
        # Should handle gracefully
        assert result.correlation_matrix.shape == (1, 1)
        assert len(result.high_correlations) == 0


class TestCorrelationPerformance:
    """Performance tests for correlation service"""
    
    @pytest.fixture
    def large_df(self):
        """Create large DataFrame for performance testing"""
        np.random.seed(42)
        n_rows = 5000
        n_cols = 100
        
        data = np.random.randn(n_rows, n_cols)
        columns = [f'feature_{i}' for i in range(n_cols)]
        
        df = pd.DataFrame(data, columns=columns)
        
        # Add some highly correlated features
        for i in range(0, 10, 2):
            df[f'feature_{i+1}'] = df[f'feature_{i}'] * 0.9 + np.random.randn(n_rows) * 0.1
        
        return df
    
    def test_large_dataset_correlation(self, large_df):
        """Test correlation analysis on large dataset"""
        analyzer = CorrelationAnalyzer()
        config = CorrelationConfig(
            method=CorrelationType.PEARSON,
            threshold=0.8
        )
        
        import time
        start_time = time.time()
        result = analyzer.analyze_correlations(large_df, config)
        duration = time.time() - start_time
        
        assert result is not None
        assert result.correlation_matrix.shape == (100, 100)
        assert duration < 30  # Should complete within 30 seconds
        
        # Should find high correlations
        assert len(result.high_correlations) >= 5
    
    def test_correlation_caching(self, large_df):
        """Test that correlation results are efficiently cached"""
        analyzer = CorrelationAnalyzer()
        config = CorrelationConfig(
            method=CorrelationType.PEARSON,
            threshold=0.8
        )
        
        # First analysis
        import time
        start_time = time.time()
        result1 = analyzer.analyze_correlations(large_df, config)
        first_duration = time.time() - start_time
        
        # Second analysis (should use some cached computations)
        start_time = time.time()
        result2 = analyzer.analyze_correlations(large_df, config)
        second_duration = time.time() - start_time
        
        # Both should produce same results
        pd.testing.assert_frame_equal(result1.correlation_matrix, result2.correlation_matrix)
        
        # Second might be faster due to internal optimizations
        assert second_duration <= first_duration * 1.1  # Allow 10% variance