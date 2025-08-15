"""
Tests for type detection module
"""

import pytest
import pandas as pd
import numpy as np
from app.ml_modules.type_detection import ColumnTypeDetector, DataType

class TestColumnTypeDetector:
    """Test cases for column type detector"""
    
    @pytest.fixture
    def type_detector(self):
        """Create type detector instance"""
        return ColumnTypeDetector()
    
    def test_detect_integer_type(self, type_detector):
        """Test integer type detection"""
        series = pd.Series([1, 2, 3, 4, 5])
        result = type_detector.detect_single_column_type(series, "test_col")
        
        assert result.detected_type == DataType.INTEGER
        assert result.confidence >= 0.9
    
    def test_detect_float_type(self, type_detector):
        """Test float type detection"""
        series = pd.Series([1.1, 2.2, 3.3, 4.4, 5.5])
        result = type_detector.detect_single_column_type(series, "test_col")
        
        assert result.detected_type == DataType.FLOAT
        assert result.confidence >= 0.9
    
    def test_detect_boolean_type(self, type_detector):
        """Test boolean type detection"""
        series = pd.Series([True, False, True, False, True])
        result = type_detector.detect_single_column_type(series, "test_col")
        
        assert result.detected_type == DataType.BOOLEAN
        assert result.confidence >= 0.9
    
    def test_detect_boolean_string_type(self, type_detector):
        """Test boolean string type detection"""
        series = pd.Series(['true', 'false', 'true', 'false'])
        result = type_detector.detect_single_column_type(series, "test_col")
        
        assert result.detected_type == DataType.BOOLEAN
        assert result.confidence >= 0.8
    
    def test_detect_categorical_type(self, type_detector):
        """Test categorical type detection"""
        series = pd.Series(['A', 'B', 'A', 'C', 'B', 'A', 'C'] * 20)  # Low cardinality
        result = type_detector.detect_single_column_type(series, "test_col")
        
        assert result.detected_type == DataType.CATEGORICAL
        assert result.confidence > 0.5
    
    def test_detect_binary_type(self, type_detector):
        """Test binary categorical type detection"""
        series = pd.Series(['Yes', 'No', 'Yes', 'No', 'Yes'])
        result = type_detector.detect_single_column_type(series, "test_col")
        
        assert result.detected_type == DataType.BINARY
        assert result.confidence >= 0.8
    
    def test_detect_datetime_type(self, type_detector):
        """Test datetime type detection"""
        series = pd.Series(['2023-01-01', '2023-01-02', '2023-01-03'])
        result = type_detector.detect_single_column_type(series, "test_col")
        
        assert result.detected_type == DataType.DATETIME
        assert result.confidence >= 0.8
    
    def test_detect_email_type(self, type_detector):
        """Test email type detection"""
        series = pd.Series(['user1@example.com', 'user2@test.org', 'admin@company.net'])
        result = type_detector.detect_single_column_type(series, "test_col")
        
        assert result.detected_type == DataType.EMAIL
        assert result.confidence >= 0.8
    
    def test_detect_url_type(self, type_detector):
        """Test URL type detection"""
        series = pd.Series(['https://example.com', 'http://test.org', 'https://company.net/page'])
        result = type_detector.detect_single_column_type(series, "test_col")
        
        assert result.detected_type == DataType.URL
        assert result.confidence >= 0.8
    
    def test_detect_text_type(self, type_detector):
        """Test text type detection (fallback)"""
        series = pd.Series(['This is a long text string', 'Another text string', 'Yet another one'])
        result = type_detector.detect_single_column_type(series, "test_col")
        
        assert result.detected_type == DataType.TEXT
    
    def test_detect_column_types_dataframe(self, type_detector):
        """Test type detection for entire DataFrame"""
        df = pd.DataFrame({
            'integers': [1, 2, 3, 4, 5],
            'floats': [1.1, 2.2, 3.3, 4.4, 5.5],
            'booleans': [True, False, True, False, True],
            'categories': ['A', 'B', 'A', 'C', 'B'],
            'dates': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'],
            'emails': ['a@b.com', 'c@d.org', 'e@f.net', 'g@h.edu', 'i@j.gov']
        })
        
        results = type_detector.detect_column_types(df)
        
        assert len(results) == 6
        assert results['integers'].detected_type == DataType.INTEGER
        assert results['floats'].detected_type == DataType.FLOAT
        assert results['booleans'].detected_type == DataType.BOOLEAN
        assert results['categories'].detected_type == DataType.CATEGORICAL
        assert results['dates'].detected_type == DataType.DATETIME
        assert results['emails'].detected_type == DataType.EMAIL
    
    def test_optimize_dtypes(self, type_detector):
        """Test dtype optimization"""
        df = pd.DataFrame({
            'integers': ['1', '2', '3', '4', '5'],  # String integers
            'floats': ['1.1', '2.2', '3.3', '4.4', '5.5'],  # String floats
            'categories': ['A', 'B', 'A', 'C', 'B']
        })
        
        detection_results = type_detector.detect_column_types(df)
        optimized_df = type_detector.optimize_dtypes(df, detection_results)
        
        # Check that dtypes were optimized
        assert pd.api.types.is_integer_dtype(optimized_df['integers'])
        assert pd.api.types.is_float_dtype(optimized_df['floats'])
        assert pd.api.types.is_categorical_dtype(optimized_df['categories'])
    
    def test_generate_type_report(self, type_detector):
        """Test type report generation"""
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c'],
            'col3': [1.1, 2.2, 3.3]
        })
        
        detection_results = type_detector.detect_column_types(df)
        report = type_detector.generate_type_report(detection_results)
        
        assert 'summary' in report
        assert 'column_details' in report
        assert 'recommendations' in report
        assert report['summary']['total_columns'] == 3
    
    def test_missing_data_handling(self, type_detector):
        """Test type detection with missing data"""
        series = pd.Series([1, 2, np.nan, 4, 5])
        result = type_detector.detect_single_column_type(series, "test_col")
        
        assert result.detected_type == DataType.INTEGER
        assert 'missing_count' in result.metadata
    
    def test_all_null_column(self, type_detector):
        """Test type detection for all-null column"""
        series = pd.Series([np.nan, np.nan, np.nan])
        result = type_detector.detect_single_column_type(series, "test_col")
        
        assert result.detected_type == DataType.UNKNOWN
        assert "only null values" in result.issues[0]
    
    def test_low_confidence_detection(self, type_detector):
        """Test handling of low confidence detection"""
        # Mixed data that's hard to classify
        series = pd.Series(['1', 'a', '2.5', 'b', '3'])
        result = type_detector.detect_single_column_type(series, "test_col")
        
        # Should still return a type but with low confidence
        assert result.detected_type in DataType
        if result.confidence < 0.8:
            assert len(result.issues) > 0