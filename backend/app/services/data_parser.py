"""
File: data_parser.py

Overview:
CSV and data file parsing service with support for large files and chunked processing

Purpose:
Provides robust CSV parsing capabilities with error handling, encoding detection,
and memory-efficient processing for large datasets

Dependencies:
- pandas: Core data manipulation and CSV parsing
- numpy: Numerical operations and data type detection
- aiofiles: Async file operations
- chardet: Encoding detection

Last Modified: 2025-08-15
Author: Claude
"""

import pandas as pd
import numpy as np
import aiofiles
import chardet
from typing import Dict, List, Optional, Tuple, AsyncIterator, Any, Union
from pathlib import Path
import logging
from io import StringIO, BytesIO

logger = logging.getLogger(__name__)

class DataParseError(Exception):
    """Custom exception for data parsing errors"""
    pass

class CSVParser:
    """
    Advanced CSV parser with support for large files, encoding detection,
    and flexible parsing options
    """
    
    def __init__(self, chunk_size: int = 10000, max_file_size: int = 100 * 1024 * 1024):
        """
        Initialize CSV parser
        
        Args:
            chunk_size: Number of rows to process per chunk for large files
            max_file_size: Maximum file size in bytes (default: 100MB)
        """
        self.chunk_size = chunk_size
        self.max_file_size = max_file_size
        
    async def detect_encoding(self, file_path: Union[str, Path]) -> str:
        """
        Detect file encoding using chardet
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Detected encoding string
            
        Raises:
            DataParseError: If encoding detection fails
        """
        try:
            async with aiofiles.open(file_path, 'rb') as f:
                raw_data = await f.read(10000)  # Read first 10KB for detection
                
            result = chardet.detect(raw_data)
            encoding = result.get('encoding', 'utf-8')
            confidence = result.get('confidence', 0)
            
            logger.info(f"Detected encoding: {encoding} (confidence: {confidence:.2f})")
            
            if confidence < 0.7:
                logger.warning(f"Low confidence in encoding detection: {confidence:.2f}")
                encoding = 'utf-8'  # Fallback to UTF-8
                
            return encoding
            
        except Exception as e:
            logger.error(f"Encoding detection failed: {e}")
            raise DataParseError(f"Failed to detect file encoding: {e}")
    
    async def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get basic file information
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Dictionary with file information
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise DataParseError(f"File not found: {file_path}")
            
        file_size = file_path.stat().st_size
        
        if file_size > self.max_file_size:
            logger.warning(f"File size ({file_size} bytes) exceeds maximum ({self.max_file_size} bytes)")
            
        encoding = await self.detect_encoding(file_path)
        
        return {
            "file_path": str(file_path),
            "file_size": file_size,
            "encoding": encoding,
            "requires_chunking": file_size > (10 * 1024 * 1024)  # 10MB threshold
        }
    
    def detect_delimiter(self, sample_data: str) -> str:
        """
        Detect CSV delimiter from sample data
        
        Args:
            sample_data: Sample of CSV data
            
        Returns:
            Detected delimiter character
        """
        common_delimiters = [',', ';', '\t', '|']
        delimiter_counts = {}
        
        for delimiter in common_delimiters:
            count = sample_data.count(delimiter)
            if count > 0:
                delimiter_counts[delimiter] = count
                
        if delimiter_counts:
            # Return delimiter with highest count
            return max(delimiter_counts.items(), key=lambda x: x[1])[0]
        
        return ','  # Default to comma
    
    async def parse_csv_sample(self, file_path: Union[str, Path], 
                              sample_rows: int = 1000) -> Dict[str, Any]:
        """
        Parse a sample of the CSV file for initial analysis
        
        Args:
            file_path: Path to the CSV file
            sample_rows: Number of rows to sample
            
        Returns:
            Dictionary with sample data and metadata
        """
        try:
            file_info = await self.get_file_info(file_path)
            encoding = file_info['encoding']
            
            # Read sample for delimiter detection
            async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
                sample_data = await f.read(1024)  # Read first 1KB
                
            delimiter = self.detect_delimiter(sample_data)
            
            # Parse sample data
            df_sample = pd.read_csv(
                file_path,
                delimiter=delimiter,
                encoding=encoding,
                nrows=sample_rows,
                low_memory=False
            )
            
            return {
                "file_info": file_info,
                "delimiter": delimiter,
                "sample_shape": df_sample.shape,
                "columns": df_sample.columns.tolist(),
                "dtypes": df_sample.dtypes.to_dict(),
                "sample_data": df_sample.head(10).to_dict('records'),
                "has_header": self._detect_header(df_sample)
            }
            
        except Exception as e:
            logger.error(f"Failed to parse CSV sample: {e}")
            raise DataParseError(f"Failed to parse CSV sample: {e}")
    
    def _detect_header(self, df: pd.DataFrame) -> bool:
        """
        Detect if first row contains headers
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            True if first row appears to be headers
        """
        if df.empty:
            return False
            
        # Check if first row has different data types from subsequent rows
        first_row = df.iloc[0]
        second_row = df.iloc[1] if len(df) > 1 else None
        
        if second_row is None:
            return True  # Single row, assume it's header
            
        # If first row is all strings and second row has mixed types, likely header
        first_all_strings = all(isinstance(val, str) for val in first_row)
        second_mixed_types = any(pd.api.types.is_numeric_dtype(type(val)) for val in second_row)
        
        return first_all_strings and second_mixed_types
    
    async def parse_csv_full(self, file_path: Union[str, Path], 
                           parse_options: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Parse complete CSV file
        
        Args:
            file_path: Path to the CSV file
            parse_options: Optional parsing parameters
            
        Returns:
            Complete DataFrame
        """
        try:
            # Get file info and sample
            sample_info = await self.parse_csv_sample(file_path)
            file_info = sample_info['file_info']
            
            # Set default parse options
            default_options = {
                'delimiter': sample_info['delimiter'],
                'encoding': file_info['encoding'],
                'low_memory': False
            }
            
            if parse_options:
                default_options.update(parse_options)
            
            # Check if chunking is needed
            if file_info['requires_chunking']:
                logger.info("Large file detected, using chunked parsing")
                return await self._parse_csv_chunked(file_path, default_options)
            else:
                logger.info("Small file, parsing in single operation")
                df = pd.read_csv(file_path, **default_options)
                return df
                
        except Exception as e:
            logger.error(f"Failed to parse CSV file: {e}")
            raise DataParseError(f"Failed to parse CSV file: {e}")
    
    async def _parse_csv_chunked(self, file_path: Union[str, Path], 
                               parse_options: Dict[str, Any]) -> pd.DataFrame:
        """
        Parse CSV file in chunks for memory efficiency
        
        Args:
            file_path: Path to the CSV file
            parse_options: Parsing parameters
            
        Returns:
            Complete DataFrame assembled from chunks
        """
        chunks = []
        
        try:
            chunk_reader = pd.read_csv(
                file_path,
                chunksize=self.chunk_size,
                **parse_options
            )
            
            for i, chunk in enumerate(chunk_reader):
                logger.debug(f"Processing chunk {i + 1}, shape: {chunk.shape}")
                chunks.append(chunk)
                
            # Combine all chunks
            df = pd.concat(chunks, ignore_index=True)
            logger.info(f"Successfully parsed file in {len(chunks)} chunks, final shape: {df.shape}")
            
            return df
            
        except Exception as e:
            logger.error(f"Chunked parsing failed: {e}")
            raise DataParseError(f"Chunked parsing failed: {e}")
    
    async def parse_csv_iterator(self, file_path: Union[str, Path], 
                               parse_options: Optional[Dict[str, Any]] = None) -> AsyncIterator[pd.DataFrame]:
        """
        Parse CSV file as an async iterator for streaming processing
        
        Args:
            file_path: Path to the CSV file
            parse_options: Optional parsing parameters
            
        Yields:
            DataFrame chunks
        """
        try:
            # Get file info and sample
            sample_info = await self.parse_csv_sample(file_path)
            file_info = sample_info['file_info']
            
            # Set default parse options
            default_options = {
                'delimiter': sample_info['delimiter'],
                'encoding': file_info['encoding'],
                'low_memory': False,
                'chunksize': self.chunk_size
            }
            
            if parse_options:
                default_options.update(parse_options)
            
            chunk_reader = pd.read_csv(file_path, **default_options)
            
            for i, chunk in enumerate(chunk_reader):
                logger.debug(f"Yielding chunk {i + 1}, shape: {chunk.shape}")
                yield chunk
                
        except Exception as e:
            logger.error(f"Iterator parsing failed: {e}")
            raise DataParseError(f"Iterator parsing failed: {e}")

class DataValidator:
    """
    Validates parsed data for common issues and inconsistencies
    """
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate DataFrame for common data quality issues
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            "is_valid": True,
            "issues": [],
            "warnings": [],
            "summary": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "memory_usage": df.memory_usage(deep=True).sum(),
                "duplicate_rows": df.duplicated().sum(),
                "empty_rows": df.isnull().all(axis=1).sum()
            }
        }
        
        # Check for empty DataFrame
        if df.empty:
            validation_results["issues"].append("DataFrame is empty")
            validation_results["is_valid"] = False
        
        # Check for duplicate columns
        duplicate_columns = df.columns[df.columns.duplicated()].tolist()
        if duplicate_columns:
            validation_results["issues"].append(f"Duplicate columns found: {duplicate_columns}")
            validation_results["is_valid"] = False
        
        # Check for excessive missing data
        missing_percentages = (df.isnull().sum() / len(df)) * 100
        high_missing_columns = missing_percentages[missing_percentages > 50].index.tolist()
        if high_missing_columns:
            validation_results["warnings"].append(
                f"Columns with >50% missing data: {high_missing_columns}"
            )
        
        # Check for single-value columns
        single_value_columns = []
        for col in df.columns:
            if df[col].nunique() <= 1:
                single_value_columns.append(col)
        
        if single_value_columns:
            validation_results["warnings"].append(
                f"Columns with single unique value: {single_value_columns}"
            )
        
        return validation_results