"""
Test suite for imputation service
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.imputation_service import (
    ImputationService,
    ImputationStrategy,
    ImputationConfig,
    ColumnImputationConfig
)


class TestImputationService:
    """Test suite for ImputationService"""
    
    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame with missing values"""
        np.random.seed(42)
        df = pd.DataFrame({
            'numeric_1': [1, 2, np.nan, 4, 5, np.nan, 7],
            'numeric_2': [10, np.nan, 30, 40, np.nan, 60, 70],
            'category': ['A', 'B', np.nan, 'A', 'B', 'C', np.nan],
            'binary': [0, 1, 0, np.nan, 1, 0, 1]
        })
        return df
    
    @pytest.fixture
    def imputation_service(self):
        """Create ImputationService instance"""
        return ImputationService()
    
    def test_initialization(self, imputation_service):
        """Test service initialization"""
        assert imputation_service is not None
        assert imputation_service.imputation_history == []
        assert imputation_service.quality_metrics == {}
    
    def test_mean_imputation(self, imputation_service, sample_df):
        """Test mean imputation strategy"""
        config = ImputationConfig(
            strategy=ImputationStrategy.MEAN,
            columns=['numeric_1', 'numeric_2']
        )
        
        result = imputation_service.impute_data(sample_df, config)
        
        # Check no missing values in specified columns
        assert result['numeric_1'].isnull().sum() == 0
        assert result['numeric_2'].isnull().sum() == 0
        
        # Check mean values were used
        expected_mean_1 = sample_df['numeric_1'].mean()
        assert np.allclose(result['numeric_1'].fillna(expected_mean_1), result['numeric_1'])
    
    def test_median_imputation(self, imputation_service, sample_df):
        """Test median imputation strategy"""
        config = ImputationConfig(
            strategy=ImputationStrategy.MEDIAN,
            columns=['numeric_1', 'numeric_2']
        )
        
        result = imputation_service.impute_data(sample_df, config)
        
        assert result['numeric_1'].isnull().sum() == 0
        assert result['numeric_2'].isnull().sum() == 0
    
    def test_mode_imputation(self, imputation_service, sample_df):
        """Test mode imputation for categorical data"""
        config = ImputationConfig(
            strategy=ImputationStrategy.MODE,
            columns=['category']
        )
        
        result = imputation_service.impute_data(sample_df, config)
        
        assert result['category'].isnull().sum() == 0
        # Mode should be 'A' or 'B' (both appear twice)
        filled_values = result.loc[sample_df['category'].isnull(), 'category']
        assert all(v in ['A', 'B'] for v in filled_values)
    
    @patch('app.services.imputation_service.KNNImputer')
    def test_knn_imputation(self, mock_knn, imputation_service, sample_df):
        """Test KNN imputation strategy"""
        # Mock KNN imputer
        mock_imputer = MagicMock()
        mock_imputer.fit_transform.return_value = sample_df[['numeric_1', 'numeric_2']].fillna(0).values
        mock_knn.return_value = mock_imputer
        
        config = ImputationConfig(
            strategy=ImputationStrategy.KNN,
            columns=['numeric_1', 'numeric_2'],
            knn_neighbors=3
        )
        
        result = imputation_service.impute_data(sample_df, config)
        
        assert result is not None
        mock_knn.assert_called_once_with(n_neighbors=3)
    
    def test_forward_fill(self, imputation_service, sample_df):
        """Test forward fill imputation"""
        config = ImputationConfig(
            strategy=ImputationStrategy.FORWARD_FILL,
            columns=['numeric_1', 'category']
        )
        
        result = imputation_service.impute_data(sample_df, config)
        
        # Check that forward fill was applied
        assert result.loc[2, 'numeric_1'] == 2  # Filled from previous value
        assert result.loc[2, 'category'] == 'B'  # Filled from previous value
    
    def test_backward_fill(self, imputation_service, sample_df):
        """Test backward fill imputation"""
        config = ImputationConfig(
            strategy=ImputationStrategy.BACKWARD_FILL,
            columns=['numeric_1', 'category']
        )
        
        result = imputation_service.impute_data(sample_df, config)
        
        # Check that backward fill was applied
        assert result.loc[2, 'numeric_1'] == 4  # Filled from next value
        assert result.loc[2, 'category'] == 'A'  # Filled from next value
    
    def test_interpolation(self, imputation_service, sample_df):
        """Test interpolation imputation"""
        config = ImputationConfig(
            strategy=ImputationStrategy.INTERPOLATE,
            columns=['numeric_1', 'numeric_2']
        )
        
        result = imputation_service.impute_data(sample_df, config)
        
        assert result['numeric_1'].isnull().sum() == 0
        assert result['numeric_2'].isnull().sum() == 0
        # Check interpolated values are between surrounding values
        assert 2 < result.loc[2, 'numeric_1'] < 4
    
    def test_constant_imputation(self, imputation_service, sample_df):
        """Test constant value imputation"""
        config = ImputationConfig(
            strategy=ImputationStrategy.CONSTANT,
            columns=['numeric_1', 'category'],
            constant_value=999
        )
        
        result = imputation_service.impute_data(sample_df, config)
        
        # Check constant value was used
        assert result.loc[2, 'numeric_1'] == 999
        assert result.loc[2, 'category'] == 999
    
    def test_column_specific_strategies(self, imputation_service, sample_df):
        """Test different strategies for different columns"""
        column_configs = [
            ColumnImputationConfig(
                column='numeric_1',
                strategy=ImputationStrategy.MEAN
            ),
            ColumnImputationConfig(
                column='numeric_2',
                strategy=ImputationStrategy.MEDIAN
            ),
            ColumnImputationConfig(
                column='category',
                strategy=ImputationStrategy.MODE
            )
        ]
        
        config = ImputationConfig(column_configs=column_configs)
        
        result = imputation_service.impute_data(sample_df, config)
        
        # Check all columns have no missing values
        assert result['numeric_1'].isnull().sum() == 0
        assert result['numeric_2'].isnull().sum() == 0
        assert result['category'].isnull().sum() == 0
    
    @patch('app.core.research_pipeline_integration.FeatureImputer')
    def test_research_pipeline_integration(self, mock_imputer_class, imputation_service, sample_df):
        """Test integration with research_pipeline"""
        # Mock research_pipeline imputer
        mock_imputer = MagicMock()
        mock_imputer.impute_data.return_value = sample_df.fillna(0)
        mock_imputer_class.return_value = mock_imputer
        
        config = ImputationConfig(
            strategy=ImputationStrategy.MICE,
            columns=sample_df.columns.tolist(),
            use_research_pipeline=True
        )
        
        result = imputation_service.impute_data(sample_df, config)
        
        assert result is not None
        mock_imputer.impute_data.assert_called_once()
    
    def test_quality_metrics_calculation(self, imputation_service, sample_df):
        """Test quality metrics calculation"""
        config = ImputationConfig(
            strategy=ImputationStrategy.MEAN,
            columns=['numeric_1', 'numeric_2']
        )
        
        result = imputation_service.impute_data(sample_df, config)
        metrics = imputation_service.calculate_quality_metrics(sample_df, result)
        
        assert 'completeness_before' in metrics
        assert 'completeness_after' in metrics
        assert 'rmse' in metrics
        assert 'mae' in metrics
        assert metrics['completeness_after'] > metrics['completeness_before']
    
    def test_imputation_preview(self, imputation_service, sample_df):
        """Test imputation preview functionality"""
        config = ImputationConfig(
            strategy=ImputationStrategy.MEAN,
            columns=['numeric_1']
        )
        
        preview = imputation_service.preview_imputation(sample_df, config, n_rows=5)
        
        assert 'before' in preview
        assert 'after' in preview
        assert len(preview['before']) <= 5
        assert preview['after']['numeric_1'].isnull().sum() == 0
    
    def test_batch_imputation(self, imputation_service):
        """Test batch imputation for multiple DataFrames"""
        dfs = [
            pd.DataFrame({'a': [1, np.nan, 3], 'b': [4, 5, np.nan]}),
            pd.DataFrame({'a': [np.nan, 2, 3], 'b': [4, np.nan, 6]})
        ]
        
        config = ImputationConfig(
            strategy=ImputationStrategy.MEAN,
            columns=['a', 'b']
        )
        
        results = imputation_service.batch_impute(dfs, config)
        
        assert len(results) == 2
        for result in results:
            assert result['a'].isnull().sum() == 0
            assert result['b'].isnull().sum() == 0
    
    def test_imputation_history(self, imputation_service, sample_df):
        """Test imputation history tracking"""
        config = ImputationConfig(
            strategy=ImputationStrategy.MEAN,
            columns=['numeric_1']
        )
        
        result = imputation_service.impute_data(sample_df, config)
        
        assert len(imputation_service.imputation_history) == 1
        history = imputation_service.imputation_history[0]
        assert history['strategy'] == ImputationStrategy.MEAN
        assert 'timestamp' in history
        assert 'affected_columns' in history
    
    def test_export_imputation_config(self, imputation_service, sample_df, tmp_path):
        """Test export of imputation configuration"""
        config = ImputationConfig(
            strategy=ImputationStrategy.MEAN,
            columns=['numeric_1', 'numeric_2']
        )
        
        result = imputation_service.impute_data(sample_df, config)
        
        # Export configuration
        export_path = tmp_path / "imputation_config.json"
        imputation_service.export_configuration(str(export_path))
        
        assert export_path.exists()
        
        # Load and verify
        import json
        with open(export_path, 'r') as f:
            exported_config = json.load(f)
        
        assert 'strategy' in exported_config
        assert 'columns' in exported_config
    
    def test_invalid_strategy(self, imputation_service, sample_df):
        """Test handling of invalid imputation strategy"""
        config = ImputationConfig(
            strategy="invalid_strategy",
            columns=['numeric_1']
        )
        
        with pytest.raises(ValueError):
            imputation_service.impute_data(sample_df, config)
    
    def test_empty_dataframe(self, imputation_service):
        """Test handling of empty DataFrame"""
        empty_df = pd.DataFrame()
        config = ImputationConfig(strategy=ImputationStrategy.MEAN)
        
        result = imputation_service.impute_data(empty_df, config)
        
        assert result.empty
    
    def test_no_missing_values(self, imputation_service):
        """Test imputation on DataFrame with no missing values"""
        complete_df = pd.DataFrame({
            'a': [1, 2, 3],
            'b': [4, 5, 6]
        })
        
        config = ImputationConfig(
            strategy=ImputationStrategy.MEAN,
            columns=['a', 'b']
        )
        
        result = imputation_service.impute_data(complete_df, config)
        
        # Should return unchanged DataFrame
        pd.testing.assert_frame_equal(result, complete_df)


class TestImputationPerformance:
    """Performance tests for imputation service"""
    
    @pytest.fixture
    def large_df(self):
        """Create large DataFrame for performance testing"""
        np.random.seed(42)
        n_rows = 10000
        n_cols = 50
        
        data = np.random.randn(n_rows, n_cols)
        # Add 20% missing values
        mask = np.random.random((n_rows, n_cols)) < 0.2
        data[mask] = np.nan
        
        columns = [f'col_{i}' for i in range(n_cols)]
        return pd.DataFrame(data, columns=columns)
    
    def test_large_dataset_imputation(self, large_df):
        """Test imputation on large dataset"""
        service = ImputationService()
        config = ImputationConfig(
            strategy=ImputationStrategy.MEAN,
            columns=large_df.columns.tolist()
        )
        
        start_time = datetime.now()
        result = service.impute_data(large_df, config)
        duration = (datetime.now() - start_time).total_seconds()
        
        assert result.isnull().sum().sum() == 0
        assert duration < 10  # Should complete within 10 seconds
        
        # Performance metrics
        rows_per_second = len(large_df) / duration
        assert rows_per_second > 1000  # Should process at least 1000 rows/second
    
    def test_parallel_imputation(self, large_df):
        """Test parallel imputation for performance"""
        service = ImputationService()
        config = ImputationConfig(
            strategy=ImputationStrategy.MEAN,
            columns=large_df.columns.tolist(),
            n_jobs=4  # Use parallel processing
        )
        
        start_time = datetime.now()
        result = service.impute_data(large_df, config)
        duration = (datetime.now() - start_time).total_seconds()
        
        assert result.isnull().sum().sum() == 0
        assert duration < 5  # Should be faster with parallel processing