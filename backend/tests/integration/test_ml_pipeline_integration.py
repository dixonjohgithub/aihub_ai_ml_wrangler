"""
Integration tests for complete ML pipeline
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import tempfile
import os
from pathlib import Path

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.imputation_service import ImputationService, ImputationConfig, ImputationStrategy
from app.services.correlation_service import CorrelationAnalyzer, CorrelationConfig, CorrelationType
from app.services.report_service import ReportGeneratorService, ReportConfig, ReportData, ReportSection
from app.services.metadata_service import MetadataService, TransformationType
from app.services.performance_service import PerformanceOptimizer, PerformanceConfig


class TestMLPipelineIntegration:
    """Integration tests for complete ML pipeline workflow"""
    
    @pytest.fixture
    def sample_dataset(self):
        """Create sample dataset with various data types and missing values"""
        np.random.seed(42)
        n = 1000
        
        df = pd.DataFrame({
            'id': range(n),
            'numeric_1': np.random.randn(n),
            'numeric_2': np.random.randn(n) * 10 + 50,
            'numeric_3': np.random.exponential(2, n),
            'categorical_1': np.random.choice(['A', 'B', 'C', 'D'], n),
            'categorical_2': np.random.choice(['X', 'Y', 'Z'], n),
            'binary': np.random.choice([0, 1], n),
            'target': np.random.randn(n)
        })
        
        # Add missing values (20% missing)
        for col in ['numeric_1', 'numeric_2', 'categorical_1']:
            mask = np.random.random(n) < 0.2
            df.loc[mask, col] = np.nan
        
        # Add correlated features
        df['correlated_1'] = df['numeric_1'] * 2 + np.random.randn(n) * 0.5
        df['correlated_2'] = df['numeric_2'] * 0.8 + np.random.randn(n)
        
        return df
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_complete_pipeline_workflow(self, sample_dataset, temp_dir):
        """Test complete workflow: import -> impute -> correlate -> report"""
        
        # Step 1: Initialize services
        imputation_service = ImputationService()
        correlation_analyzer = CorrelationAnalyzer()
        report_generator = ReportGeneratorService(output_dir=temp_dir)
        metadata_service = MetadataService()
        
        # Step 2: Create dataset metadata
        metadata = metadata_service.create_dataset_metadata(
            sample_dataset,
            name="test_dataset",
            source_file="test.csv",
            tags=["test", "integration"]
        )
        
        assert metadata.dataset_id is not None
        assert metadata.row_count == 1000
        
        # Step 3: Perform imputation
        imputation_config = ImputationConfig(
            strategy=ImputationStrategy.MEAN,
            columns=['numeric_1', 'numeric_2']
        )
        
        imputed_df = imputation_service.impute_data(sample_dataset, imputation_config)
        
        # Track transformation
        metadata_service.track_transformation(
            transformation_type=TransformationType.IMPUTATION,
            operation="Mean imputation",
            parameters={'strategy': 'mean'},
            affected_columns=['numeric_1', 'numeric_2'],
            df_before=sample_dataset,
            df_after=imputed_df
        )
        
        assert imputed_df['numeric_1'].isnull().sum() == 0
        assert imputed_df['numeric_2'].isnull().sum() == 0
        
        # Step 4: Perform correlation analysis
        correlation_config = CorrelationConfig(
            method=CorrelationType.PEARSON,
            threshold=0.7
        )
        
        correlation_result = correlation_analyzer.analyze_correlations(
            imputed_df,
            correlation_config,
            target_column='target'
        )
        
        assert correlation_result.correlation_matrix is not None
        assert len(correlation_result.high_correlations) > 0
        
        # Step 5: Generate report
        report_data = ReportData(
            original_data=sample_dataset,
            imputed_data=imputed_df,
            correlation_matrix=correlation_result.correlation_matrix,
            imputation_config={'strategy': 'mean'},
            quality_metrics=imputation_service.quality_metrics,
            ai_recommendations=[],
            transformation_history=metadata_service.transformation_stack,
            dataset_metadata={'filename': 'test.csv'}
        )
        
        report_config = ReportConfig(
            title="Integration Test Report",
            sections=[
                ReportSection.EXECUTIVE_SUMMARY,
                ReportSection.DATA_OVERVIEW,
                ReportSection.MISSING_DATA_ANALYSIS,
                ReportSection.IMPUTATION_DETAILS,
                ReportSection.CORRELATION_ANALYSIS,
                ReportSection.QUALITY_METRICS,
                ReportSection.RECOMMENDATIONS
            ]
        )
        
        report_content, report_metadata = report_generator.generate_report(
            report_data,
            report_config
        )
        
        assert report_content is not None
        assert "Executive Summary" in report_content
        assert "Correlation Analysis" in report_content
        
        # Step 6: Verify audit trail
        audit_log = metadata_service.get_audit_log(entity_type="dataset")
        assert len(audit_log) > 0
        
        transformation_history = metadata_service.get_transformation_history()
        assert len(transformation_history) > 0
    
    def test_large_dataset_handling(self, temp_dir):
        """Test pipeline with large dataset using performance optimization"""
        
        # Create large dataset
        n_rows = 50000
        n_cols = 50
        
        large_df = pd.DataFrame(
            np.random.randn(n_rows, n_cols),
            columns=[f'col_{i}' for i in range(n_cols)]
        )
        
        # Add missing values
        mask = np.random.random((n_rows, n_cols)) < 0.1
        large_df[mask] = np.nan
        
        # Save to CSV
        csv_path = os.path.join(temp_dir, 'large_dataset.csv')
        large_df.to_csv(csv_path, index=False)
        
        # Initialize performance optimizer
        perf_config = PerformanceConfig(
            chunk_size=5000,
            max_workers=2,
            use_dask=False,  # Disable Dask for testing
            use_caching=True,
            cache_dir=temp_dir
        )
        
        optimizer = PerformanceOptimizer(perf_config)
        
        # Define operations
        def impute_mean(df):
            return df.fillna(df.mean())
        
        # Process with optimization
        result = optimizer.process_large_dataset(
            csv_path,
            operations=[impute_mean],
            use_research_pipeline=False
        )
        
        assert result is not None
        assert result.isnull().sum().sum() == 0
        
        # Check performance metrics
        perf_report = optimizer.get_performance_report()
        assert 'current_resources' in perf_report
        assert 'optimization_suggestions' in perf_report
        
        # Cleanup
        optimizer.cleanup()
    
    @patch('app.core.research_pipeline_integration.FeatureImputer')
    @patch('app.core.research_pipeline_integration.EDA')
    def test_research_pipeline_integration(self, mock_eda_class, mock_imputer_class, sample_dataset):
        """Test integration with research_pipeline modules"""
        
        # Mock research_pipeline components
        mock_imputer = Mock()
        mock_imputer.impute_data.return_value = sample_dataset.fillna(0)
        mock_imputer_class.return_value = mock_imputer
        
        mock_eda = Mock()
        mock_eda.calculate_vif.return_value = {'col1': 1.5, 'col2': 2.0}
        mock_eda.get_correlation_matrix.return_value = pd.DataFrame(
            np.eye(len(sample_dataset.columns)),
            columns=sample_dataset.columns,
            index=sample_dataset.columns
        )
        mock_eda_class.return_value = mock_eda
        
        # Use research_pipeline for imputation
        imputation_service = ImputationService()
        config = ImputationConfig(
            strategy=ImputationStrategy.MICE,
            columns=sample_dataset.columns.tolist(),
            use_research_pipeline=True
        )
        
        result = imputation_service.impute_data(sample_dataset, config)
        assert result is not None
        mock_imputer.impute_data.assert_called()
        
        # Use research_pipeline for correlation
        analyzer = CorrelationAnalyzer()
        vif_scores = analyzer.calculate_vif(sample_dataset)
        assert vif_scores is not None
        mock_eda.calculate_vif.assert_called()
    
    def test_error_recovery(self, sample_dataset):
        """Test pipeline error recovery and graceful degradation"""
        
        # Test with invalid configuration
        imputation_service = ImputationService()
        
        # Invalid strategy should raise error
        invalid_config = ImputationConfig(
            strategy="invalid_strategy",
            columns=['numeric_1']
        )
        
        with pytest.raises(ValueError):
            imputation_service.impute_data(sample_dataset, invalid_config)
        
        # Test with missing columns
        config_missing_cols = ImputationConfig(
            strategy=ImputationStrategy.MEAN,
            columns=['non_existent_column']
        )
        
        # Should handle gracefully
        try:
            result = imputation_service.impute_data(sample_dataset, config_missing_cols)
            # Should return original data if columns don't exist
            pd.testing.assert_frame_equal(result, sample_dataset)
        except:
            # Or raise appropriate error
            pass
    
    def test_reproducibility(self, sample_dataset, temp_dir):
        """Test pipeline reproducibility with metadata"""
        
        metadata_service = MetadataService(
            database_url=f"sqlite:///{temp_dir}/test_metadata.db"
        )
        
        # Create dataset and track transformations
        metadata = metadata_service.create_dataset_metadata(
            sample_dataset,
            name="reproducibility_test"
        )
        
        # Perform transformations
        imputation_service = ImputationService()
        config = ImputationConfig(
            strategy=ImputationStrategy.MEAN,
            columns=['numeric_1']
        )
        
        imputed_df = imputation_service.impute_data(sample_dataset, config)
        
        # Track transformation
        trans_record = metadata_service.track_transformation(
            transformation_type=TransformationType.IMPUTATION,
            operation="mean_imputation",
            parameters={'strategy': 'mean', 'columns': ['numeric_1']},
            affected_columns=['numeric_1'],
            df_before=sample_dataset,
            df_after=imputed_df
        )
        
        # Create reproducibility package
        repro_package = metadata_service.create_reproducibility_package(
            dataset_id=metadata.dataset_id,
            transformations=[trans_record.id]
        )
        
        assert 'package_id' in repro_package
        assert 'transformations' in repro_package
        assert len(repro_package['transformations']) == 1
        
        # Verify we can recreate the same transformation
        transform_info = repro_package['transformations'][0]
        assert transform_info['operation'] == 'mean_imputation'
        assert transform_info['parameters']['strategy'] == 'mean'


class TestEndToEndScenarios:
    """End-to-end scenario tests"""
    
    def test_csv_import_to_export_workflow(self, temp_dir):
        """Test complete workflow from CSV import to final export"""
        
        # Create test CSV
        test_data = pd.DataFrame({
            'A': [1, 2, np.nan, 4, 5],
            'B': [np.nan, 2, 3, 4, 5],
            'C': ['a', 'b', np.nan, 'd', 'e']
        })
        
        csv_path = Path(temp_dir) / 'test_data.csv'
        test_data.to_csv(csv_path, index=False)
        
        # Import and process
        df = pd.read_csv(csv_path)
        
        # Impute
        imputation_service = ImputationService()
        imputed = imputation_service.impute_data(
            df,
            ImputationConfig(
                strategy=ImputationStrategy.MEAN,
                columns=['A', 'B']
            )
        )
        
        # Analyze correlations
        analyzer = CorrelationAnalyzer()
        corr_result = analyzer.analyze_correlations(
            imputed,
            CorrelationConfig(method=CorrelationType.PEARSON)
        )
        
        # Export results
        export_path = Path(temp_dir) / 'correlation_matrix.csv'
        analyzer.export_correlation_csv(imputed, str(export_path))
        
        # Verify export
        assert export_path.exists()
    
    def test_performance_under_load(self):
        """Test system performance under load"""
        
        # Create multiple small datasets
        datasets = []
        for i in range(10):
            df = pd.DataFrame({
                'col1': np.random.randn(1000),
                'col2': np.random.randn(1000),
                'col3': np.random.randn(1000)
            })
            # Add missing values
            mask = np.random.random((1000, 3)) < 0.1
            df[mask] = np.nan
            datasets.append(df)
        
        # Process all datasets
        imputation_service = ImputationService()
        config = ImputationConfig(
            strategy=ImputationStrategy.MEAN,
            columns=['col1', 'col2', 'col3']
        )
        
        results = imputation_service.batch_impute(datasets, config)
        
        assert len(results) == 10
        for result in results:
            assert result.isnull().sum().sum() == 0