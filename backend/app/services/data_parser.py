"""
File: data_parser.py

Overview:
Advanced data parser for CSV files with encoding detection, delimiter inference,
and chunked processing for large datasets.

Purpose:
Provides robust CSV parsing capabilities with error handling and memory efficiency
for the data processing pipeline.

Dependencies:
- pandas for data manipulation
- chardet for encoding detection
- asyncio for async processing
- io for string handling

Last Modified: 2025-08-15
Author: Claude
"""

import asyncio
import io
from typing import Optional, Dict, Any, List, Tuple
import pandas as pd
import chardet
from pathlib import Path

class DataParser:
    """Advanced CSV parser with encoding detection and chunked processing."""
    
    def __init__(self, chunk_size: int = 10000):
        self.chunk_size = chunk_size
        self.supported_encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
        
    async def detect_encoding(self, file_content: bytes) -> str:
        """Detect file encoding using chardet."""
        try:
            # Use first 100KB for encoding detection
            sample = file_content[:100000] if len(file_content) > 100000 else file_content
            result = chardet.detect(sample)
            encoding = result.get('encoding', 'utf-8')
            confidence = result.get('confidence', 0)
            
            # Fallback to utf-8 if confidence is too low
            if confidence < 0.7:
                encoding = 'utf-8'
                
            return encoding
        except Exception:
            return 'utf-8'
    
    async def detect_delimiter(self, sample_text: str) -> str:
        """Detect CSV delimiter from sample text."""
        potential_delimiters = [',', ';', '\t', '|']
        delimiter_counts = {}
        
        # Analyze first few lines
        lines = sample_text.split('\n')[:5]
        for line in lines:
            for delim in potential_delimiters:
                count = line.count(delim)
                delimiter_counts[delim] = delimiter_counts.get(delim, 0) + count
        
        # Return delimiter with highest consistent count
        if delimiter_counts:
            return max(delimiter_counts, key=delimiter_counts.get)
        return ','
    
    async def parse_csv_file(self, file_path: str) -> Dict[str, Any]:
        """Parse CSV file with automatic encoding and delimiter detection."""
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Detect encoding
            encoding = await self.detect_encoding(content)
            
            # Convert to text
            try:
                text_content = content.decode(encoding)
            except UnicodeDecodeError:
                # Fallback encoding
                text_content = content.decode('utf-8', errors='ignore')
                encoding = 'utf-8'
            
            # Detect delimiter from sample
            delimiter = await self.detect_delimiter(text_content[:1000])
            
            # Parse CSV
            df = pd.read_csv(
                io.StringIO(text_content),
                delimiter=delimiter,
                encoding=encoding,
                low_memory=False,
                na_values=['', 'NULL', 'null', 'NaN', 'nan', 'N/A', 'n/a']
            )
            
            return {
                'success': True,
                'data': df,
                'metadata': {
                    'encoding': encoding,
                    'delimiter': delimiter,
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': df.columns.tolist(),
                    'memory_usage': df.memory_usage(deep=True).sum()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': None,
                'metadata': None
            }
    
    async def parse_csv_chunks(self, file_path: str, chunk_size: Optional[int] = None) -> Dict[str, Any]:
        """Parse large CSV files in chunks for memory efficiency."""
        chunk_size = chunk_size or self.chunk_size
        
        try:
            # First, detect encoding and delimiter
            with open(file_path, 'rb') as f:
                sample = f.read(100000)  # Read 100KB sample
            
            encoding = await self.detect_encoding(sample)
            text_sample = sample.decode(encoding, errors='ignore')
            delimiter = await self.detect_delimiter(text_sample)
            
            # Initialize chunk processing
            chunks = []
            total_rows = 0
            
            # Process file in chunks
            chunk_reader = pd.read_csv(
                file_path,
                delimiter=delimiter,
                encoding=encoding,
                chunksize=chunk_size,
                low_memory=False,
                na_values=['', 'NULL', 'null', 'NaN', 'nan', 'N/A', 'n/a']
            )
            
            for i, chunk in enumerate(chunk_reader):
                chunks.append({
                    'chunk_id': i,
                    'rows': len(chunk),
                    'columns': len(chunk.columns),
                    'data_preview': chunk.head(5).to_dict('records') if len(chunk) > 0 else []
                })
                total_rows += len(chunk)
                
                # Limit number of chunks processed for memory
                if i >= 100:  # Max 100 chunks
                    break
            
            # Get column information from first chunk if available
            first_chunk = pd.read_csv(
                file_path,
                delimiter=delimiter,
                encoding=encoding,
                nrows=1000,
                low_memory=False
            )
            
            return {
                'success': True,
                'chunks': chunks,
                'total_chunks': len(chunks),
                'total_rows': total_rows,
                'metadata': {
                    'encoding': encoding,
                    'delimiter': delimiter,
                    'columns': len(first_chunk.columns),
                    'column_names': first_chunk.columns.tolist(),
                    'chunk_size': chunk_size
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'chunks': [],
                'total_chunks': 0,
                'total_rows': 0,
                'metadata': None
            }
    
    async def get_data_preview(self, file_path: str, rows: int = 100) -> Dict[str, Any]:
        """Get a preview of the data without loading the entire file."""
        try:
            result = await self.parse_csv_file(file_path)
            
            if not result['success']:
                return result
            
            df = result['data']
            preview_rows = min(rows, len(df))
            
            return {
                'success': True,
                'preview': df.head(preview_rows).to_dict('records'),
                'metadata': result['metadata']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'preview': [],
                'metadata': None
            }