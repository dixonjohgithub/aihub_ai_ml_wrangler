"""
File: test_data_processing_pipeline.py

Overview:
Comprehensive tests for the data processing pipeline components
including parsers, validators, type detection, and missing data analysis.

Purpose:
Ensures all components of the T7 data processing pipeline work correctly
with various data scenarios and edge cases.

Dependencies:
- pytest for testing framework
- pandas for test data creation
- asyncio for async test support

Last Modified: 2025-08-15
Author: Claude
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import asyncio
from pathlib import Path

# Import the modules to test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.data_parser import DataParser
from app.services.data_validation import DataValidationService
from app.services.data_chunking import DataChunkingService
from app.ml_modules.type_detection import TypeDetector
from app.ml_modules.missing_data_analysis import MissingDataAnalyzer

class TestDataProcessingPipeline:
    """Test suite for the complete data processing pipeline."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.data_parser = DataParser()
        self.data_validator = DataValidationService()
        self.data_chunker = DataChunkingService()
        self.type_detector = TypeDetector()
        self.missing_analyzer = MissingDataAnalyzer()
        
        # Create test data
        self.test_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', None, 'Eve'],
            'age': [25, 30, 35, 40, None],
            'email': ['alice@test.com', 'bob@test.com', None, 'invalid-email', 'eve@test.com'],
            'binary_flag': [True, False, True, False, True],
            'category': ['A', 'B', 'A', 'C', 'B']
        })
    
    def create_temp_csv(self, data: pd.DataFrame) -> str:
        """Create a temporary CSV file for testing."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        data.to_csv(temp_file.name, index=False)
        temp_file.close()
        return temp_file.name
    
    @pytest.mark.asyncio
    async def test_data_parser_basic(self):
        """Test basic CSV parsing functionality."""
        temp_path = self.create_temp_csv(self.test_data)
        
        try:
            result = await self.data_parser.parse_csv_file(temp_path)
            
            assert result['success'] == True
            assert result['data'] is not None
            assert len(result['data']) == 5
            assert len(result['data'].columns) == 6
            assert result['metadata']['rows'] == 5
            assert result['metadata']['columns'] == 6
            
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_data_parser_preview(self):
        """Test data preview functionality."""
        temp_path = self.create_temp_csv(self.test_data)
        
        try:
            result = await self.data_parser.get_data_preview(temp_path, rows=3)
            
            assert result['success'] == True
            assert len(result['preview']) == 3
            assert result['metadata']['rows'] == 5  # Total rows
            
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_type_detection(self):
        """Test column type detection."""
        result = await self.type_detector.detect_column_types(self.test_data)
        
        assert result['success'] == True
        type_detection = result['type_detection']
        
        # Check specific type detections
        assert type_detection['columns']['id']['primary_type'] == 'numeric'
        assert type_detection['columns']['name']['primary_type'] in ['categorical', 'text']
        assert type_detection['columns']['age']['primary_type'] == 'numeric'
        assert type_detection['columns']['binary_flag']['primary_type'] == 'binary'
        
        # Check summary
        assert 'numeric' in type_detection['summary']
        assert 'binary' in type_detection['summary']
    
    @pytest.mark.asyncio
    async def test_data_validation(self):
        """Test data validation service."""
        result = await self.data_validator.validate_dataset(self.test_data)
        
        assert result['success'] == True
        validation = result['validation']
        
        # Check validation dimensions
        assert 'completeness' in validation['quality_dimensions']
        assert 'consistency' in validation['quality_dimensions']
        assert 'uniqueness' in validation['quality_dimensions']
        
        # Check overall score
        assert 0 <= validation['overall_score'] <= 100
        
        # Should detect missing values
        completeness = validation['quality_dimensions']['completeness']
        assert completeness['total_missing'] > 0
    
    @pytest.mark.asyncio
    async def test_missing_data_analysis(self):
        """Test missing data pattern analysis."""
        result = await self.missing_analyzer.analyze_missing_patterns(self.test_data)
        
        assert result['success'] == True
        missing_analysis = result['missing_analysis']
        
        # Check missing overview
        assert 'missing_overview' in missing_analysis
        assert missing_analysis['missing_overview']['total_missing_values'] > 0
        
        # Check mechanism analysis
        assert 'mechanism_analysis' in missing_analysis
        assert missing_analysis['mechanism_analysis']['overall_mechanism'] in ['MCAR', 'MAR', 'MNAR', 'Unknown']
        
        # Check recommendations
        assert 'recommendations' in missing_analysis
        assert isinstance(missing_analysis['recommendations'], list)
    
    @pytest.mark.asyncio
    async def test_data_chunking_calculation(self):
        """Test optimal chunk size calculation."""
        temp_path = self.create_temp_csv(self.test_data)
        
        try:
            result = await self.data_chunker.calculate_optimal_chunk_size(temp_path)
            
            assert result['success'] == True
            assert result['optimal_chunk_size'] > 0
            assert result['estimated_total_rows'] > 0
            
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_data_chunking_statistics(self):
        """Test chunk statistics gathering."""
        temp_path = self.create_temp_csv(self.test_data)
        
        try:
            result = await self.data_chunker.get_chunk_statistics(temp_path, chunk_size=2)
            
            assert result['success'] == True
            assert result['analyzed_chunks'] > 0
            assert len(result['chunk_statistics']) > 0
            
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_data_sampling(self):
        """Test data sampling functionality."""
        temp_path = self.create_temp_csv(self.test_data)
        
        try:
            result = await self.data_chunker.create_data_sample(
                temp_path, 
                sample_size=3, 
                sampling_method='random'
            )
            
            assert result['success'] == True
            assert len(result['sample']) <= 3
            assert result['sampling_ratio'] <= 1.0
            
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_pipeline_integration(self):
        """Test complete pipeline integration."""
        temp_path = self.create_temp_csv(self.test_data)
        
        try:
            # 1. Parse data
            parse_result = await self.data_parser.parse_csv_file(temp_path)
            assert parse_result['success'] == True
            
            df = parse_result['data']
            
            # 2. Detect types
            type_result = await self.type_detector.detect_column_types(df)
            assert type_result['success'] == True
            
            # 3. Validate data
            validation_result = await self.data_validator.validate_dataset(df)
            assert validation_result['success'] == True
            
            # 4. Analyze missing patterns
            missing_result = await self.missing_analyzer.analyze_missing_patterns(df)
            assert missing_result['success'] == True
            
            # All components should work together
            assert len(df) == 5
            assert len(df.columns) == 6
            
        finally:
            os.unlink(temp_path)
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test with empty dataframe
        empty_df = pd.DataFrame()
        
        # This should not crash
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.type_detector.detect_column_types(empty_df))
        
        # Should handle empty data gracefully
        assert result['success'] == True
        assert result['type_detection']['total_columns'] == 0

if __name__ == "__main__":
    # Run basic smoke test
    test_suite = TestDataProcessingPipeline()
    test_suite.setup_method()
    
    # Run a simple integration test
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_suite.test_pipeline_integration())
    
    print("✅ Basic pipeline integration test passed!")