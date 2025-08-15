"""
Tests for data parser module
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from pathlib import Path
from app.services.data_parser import CSVParser, DataValidator, DataParseError

class TestCSVParser:
    """Test cases for CSV parser"""
    
    @pytest.fixture
    def sample_csv_data(self):
        """Create sample CSV data for testing"""
        return """name,age,city,salary
John Doe,30,New York,50000
Jane Smith,25,Los Angeles,55000
Bob Johnson,35,Chicago,60000
Alice Brown,28,Houston,52000"""
    
    @pytest.fixture
    def large_csv_data(self):
        """Create large CSV data for testing chunking"""
        data = "id,value,category\n"
        for i in range(15000):
            data += f"{i},{i*10},cat_{i%5}\n"
        return data
    
    @pytest.fixture
    def csv_parser(self):
        """Create CSV parser instance"""
        return CSVParser(chunk_size=5000)
    
    def test_detect_encoding(self, csv_parser, sample_csv_data):
        """Test encoding detection"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv_data)
            temp_path = f.name
        
        try:
            import asyncio
            encoding = asyncio.run(csv_parser.detect_encoding(temp_path))
            assert encoding in ['utf-8', 'ascii', 'utf-8-sig']
        finally:
            os.unlink(temp_path)
    
    def test_get_file_info(self, csv_parser, sample_csv_data):
        """Test file info extraction"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv_data)
            temp_path = f.name
        
        try:
            import asyncio
            file_info = asyncio.run(csv_parser.get_file_info(temp_path))
            
            assert 'file_path' in file_info
            assert 'file_size' in file_info
            assert 'encoding' in file_info
            assert 'requires_chunking' in file_info
            assert file_info['file_size'] > 0
        finally:
            os.unlink(temp_path)
    
    def test_detect_delimiter(self, csv_parser):
        """Test delimiter detection"""
        csv_data = "a,b,c\n1,2,3"
        delimiter = csv_parser.detect_delimiter(csv_data)
        assert delimiter == ','
        
        tsv_data = "a\tb\tc\n1\t2\t3"
        delimiter = csv_parser.detect_delimiter(tsv_data)
        assert delimiter == '\t'
    
    def test_parse_csv_sample(self, csv_parser, sample_csv_data):
        """Test CSV sample parsing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv_data)
            temp_path = f.name
        
        try:
            import asyncio
            sample_info = asyncio.run(csv_parser.parse_csv_sample(temp_path))
            
            assert 'file_info' in sample_info
            assert 'delimiter' in sample_info
            assert 'sample_shape' in sample_info
            assert 'columns' in sample_info
            assert 'sample_data' in sample_info
            
            assert sample_info['delimiter'] == ','
            assert sample_info['sample_shape'] == (4, 4)
            assert set(sample_info['columns']) == {'name', 'age', 'city', 'salary'}
        finally:
            os.unlink(temp_path)
    
    def test_parse_csv_full_small(self, csv_parser, sample_csv_data):
        """Test full CSV parsing for small files"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv_data)
            temp_path = f.name
        
        try:
            import asyncio
            df = asyncio.run(csv_parser.parse_csv_full(temp_path))
            
            assert len(df) == 4
            assert len(df.columns) == 4
            assert list(df.columns) == ['name', 'age', 'city', 'salary']
            assert df.iloc[0]['name'] == 'John Doe'
        finally:
            os.unlink(temp_path)
    
    def test_parse_csv_chunked(self, csv_parser, large_csv_data):
        """Test chunked CSV parsing for large files"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(large_csv_data)
            temp_path = f.name
        
        try:
            import asyncio
            df = asyncio.run(csv_parser.parse_csv_full(temp_path))
            
            assert len(df) == 15000
            assert len(df.columns) == 3
            assert list(df.columns) == ['id', 'value', 'category']
        finally:
            os.unlink(temp_path)
    
    def test_parse_csv_iterator(self, csv_parser, large_csv_data):
        """Test CSV iterator parsing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(large_csv_data)
            temp_path = f.name
        
        try:
            import asyncio
            
            async def test_iterator():
                total_rows = 0
                chunk_count = 0
                async for chunk in csv_parser.parse_csv_iterator(temp_path):
                    total_rows += len(chunk)
                    chunk_count += 1
                return total_rows, chunk_count
            
            total_rows, chunk_count = asyncio.run(test_iterator())
            
            assert total_rows == 15000
            assert chunk_count >= 3  # Should be chunked
        finally:
            os.unlink(temp_path)
    
    def test_invalid_file(self, csv_parser):
        """Test handling of invalid file paths"""
        with pytest.raises(DataParseError):
            import asyncio
            asyncio.run(csv_parser.parse_csv_sample("nonexistent_file.csv"))

class TestDataValidator:
    """Test cases for data validator"""
    
    def test_validate_dataframe_empty(self):
        """Test validation of empty DataFrame"""
        df = pd.DataFrame()
        result = DataValidator.validate_dataframe(df)
        
        assert not result['is_valid']
        assert any('empty' in issue.lower() for issue in result['issues'])
    
    def test_validate_dataframe_normal(self):
        """Test validation of normal DataFrame"""
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e'],
            'C': [1.1, 2.2, 3.3, 4.4, 5.5]
        })
        
        result = DataValidator.validate_dataframe(df)
        
        assert result['is_valid']
        assert result['summary']['total_rows'] == 5
        assert result['summary']['total_columns'] == 3
        assert result['summary']['duplicate_rows'] == 0
    
    def test_validate_dataframe_duplicates(self):
        """Test validation with duplicate columns and rows"""
        df = pd.DataFrame({
            'A': [1, 2, 3, 2],
            'A': [4, 5, 6, 5],  # Duplicate column name
            'B': ['x', 'y', 'z', 'y']
        })
        
        result = DataValidator.validate_dataframe(df)
        
        # Should detect duplicate columns
        assert not result['is_valid']
        assert any('duplicate' in issue.lower() for issue in result['issues'])
    
    def test_validate_dataframe_missing_data(self):
        """Test validation with missing data"""
        df = pd.DataFrame({
            'A': [1, 2, np.nan, 4, np.nan],
            'B': ['a', np.nan, 'c', np.nan, 'e'],
            'C': [np.nan, np.nan, np.nan, np.nan, np.nan]  # All missing
        })
        
        result = DataValidator.validate_dataframe(df)
        
        assert len(result['warnings']) > 0  # Should have warnings about missing data