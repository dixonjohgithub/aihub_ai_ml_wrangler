"""
File: data_chunking.py

Overview:
Intelligent data chunking service for memory-efficient processing
of large datasets with adaptive chunk sizing and progress tracking.

Purpose:
Enables processing of large datasets (>10MB) by breaking them into
manageable chunks while maintaining data integrity and relationships.

Dependencies:
- pandas for data manipulation
- numpy for numerical operations
- asyncio for async processing
- typing for type hints

Last Modified: 2025-08-15
Author: Claude
"""

import asyncio
import os
from typing import Dict, Any, List, Optional, Iterator, Callable
import pandas as pd
import numpy as np
from pathlib import Path
import psutil

class DataChunkingService:
    """Intelligent data chunking for large dataset processing."""
    
    def __init__(self, 
                 default_chunk_size: int = 10000,
                 max_memory_usage: float = 0.8,
                 min_chunk_size: int = 1000):
        self.default_chunk_size = default_chunk_size
        self.max_memory_usage = max_memory_usage  # 80% of available memory
        self.min_chunk_size = min_chunk_size
        self.chunk_cache = {}
        
    async def calculate_optimal_chunk_size(self, 
                                         file_path: str,
                                         sample_rows: int = 1000) -> Dict[str, Any]:
        """Calculate optimal chunk size based on file and memory constraints."""
        try:
            # Get system memory info
            memory = psutil.virtual_memory()
            available_memory = memory.available
            
            # Sample the file to estimate memory usage
            sample_df = pd.read_csv(file_path, nrows=sample_rows)
            sample_memory = sample_df.memory_usage(deep=True).sum()
            
            # Estimate memory per row
            memory_per_row = sample_memory / len(sample_df) if len(sample_df) > 0 else 1000
            
            # Calculate safe chunk size based on available memory
            safe_memory_limit = available_memory * self.max_memory_usage
            optimal_chunk_size = int(safe_memory_limit / (memory_per_row * 2))  # Factor of 2 for safety
            
            # Apply constraints
            optimal_chunk_size = max(self.min_chunk_size, optimal_chunk_size)
            optimal_chunk_size = min(optimal_chunk_size, 100000)  # Max chunk size
            
            # Get file info
            file_size = os.path.getsize(file_path)
            estimated_total_rows = int(file_size / (sample_memory / sample_rows)) if sample_rows > 0 else 0
            estimated_chunks = max(1, estimated_total_rows // optimal_chunk_size)
            
            return {
                'success': True,
                'optimal_chunk_size': optimal_chunk_size,
                'memory_per_row': int(memory_per_row),
                'available_memory': available_memory,
                'estimated_total_rows': estimated_total_rows,
                'estimated_chunks': estimated_chunks,
                'file_size': file_size,
                'requires_chunking': file_size > 10 * 1024 * 1024  # > 10MB
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'optimal_chunk_size': self.default_chunk_size,
                'requires_chunking': True
            }
    
    async def create_chunked_reader(self, 
                                  file_path: str,
                                  chunk_size: Optional[int] = None) -> Dict[str, Any]:
        """Create a chunked reader for large files."""
        try:
            # Calculate optimal chunk size if not provided
            if chunk_size is None:
                chunk_info = await self.calculate_optimal_chunk_size(file_path)
                chunk_size = chunk_info['optimal_chunk_size']
            
            # Create pandas chunk reader
            chunk_reader = pd.read_csv(
                file_path,
                chunksize=chunk_size,
                low_memory=False,
                na_values=['', 'NULL', 'null', 'NaN', 'nan', 'N/A', 'n/a']
            )
            
            return {
                'success': True,
                'chunk_reader': chunk_reader,
                'chunk_size': chunk_size,
                'reader_id': id(chunk_reader)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'chunk_reader': None,
                'chunk_size': chunk_size or self.default_chunk_size
            }
    
    async def process_chunks_with_function(self,
                                         file_path: str,
                                         processing_function: Callable,
                                         chunk_size: Optional[int] = None,
                                         progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Process file chunks with a custom function."""
        try:
            chunk_reader_result = await self.create_chunked_reader(file_path, chunk_size)
            
            if not chunk_reader_result['success']:
                return chunk_reader_result
            
            chunk_reader = chunk_reader_result['chunk_reader']
            results = []
            total_rows_processed = 0
            chunk_count = 0
            
            for chunk in chunk_reader:
                chunk_count += 1
                chunk_rows = len(chunk)
                total_rows_processed += chunk_rows
                
                # Process chunk
                try:
                    chunk_result = await processing_function(chunk, chunk_count)
                    results.append({
                        'chunk_id': chunk_count,
                        'rows_processed': chunk_rows,
                        'result': chunk_result
                    })
                    
                    # Progress callback
                    if progress_callback:
                        await progress_callback(chunk_count, total_rows_processed)
                        
                except Exception as chunk_error:
                    results.append({
                        'chunk_id': chunk_count,
                        'rows_processed': chunk_rows,
                        'error': str(chunk_error)
                    })
            
            return {
                'success': True,
                'total_chunks_processed': chunk_count,
                'total_rows_processed': total_rows_processed,
                'chunk_results': results,
                'chunk_size_used': chunk_reader_result['chunk_size']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'total_chunks_processed': 0,
                'total_rows_processed': 0,
                'chunk_results': []
            }
    
    async def get_chunk_statistics(self, 
                                 file_path: str,
                                 chunk_size: Optional[int] = None) -> Dict[str, Any]:
        """Get statistics about file chunking without processing all data."""
        try:
            chunk_reader_result = await self.create_chunked_reader(file_path, chunk_size)
            
            if not chunk_reader_result['success']:
                return chunk_reader_result
            
            chunk_reader = chunk_reader_result['chunk_reader']
            chunk_stats = []
            total_rows = 0
            total_memory = 0
            chunk_count = 0
            
            # Process first few chunks for statistics
            for i, chunk in enumerate(chunk_reader):
                chunk_count += 1
                chunk_rows = len(chunk)
                chunk_memory = chunk.memory_usage(deep=True).sum()
                chunk_cols = len(chunk.columns)
                
                total_rows += chunk_rows
                total_memory += chunk_memory
                
                chunk_stats.append({
                    'chunk_id': chunk_count,
                    'rows': chunk_rows,
                    'columns': chunk_cols,
                    'memory_usage': chunk_memory,
                    'data_types': chunk.dtypes.value_counts().to_dict()
                })
                
                # Only analyze first 10 chunks for estimation
                if i >= 9:
                    break
            
            # Estimate total statistics
            if chunk_count > 0:
                avg_rows_per_chunk = total_rows / chunk_count
                avg_memory_per_chunk = total_memory / chunk_count
                
                # Estimate total file statistics
                file_size = os.path.getsize(file_path)
                estimated_total_chunks = max(1, int(file_size / (total_memory / chunk_count)) * 1.2)  # 20% buffer
                estimated_total_rows = int(avg_rows_per_chunk * estimated_total_chunks)
                estimated_total_memory = int(avg_memory_per_chunk * estimated_total_chunks)
            else:
                estimated_total_chunks = 0
                estimated_total_rows = 0
                estimated_total_memory = 0
            
            return {
                'success': True,
                'analyzed_chunks': chunk_count,
                'chunk_statistics': chunk_stats,
                'chunk_size_used': chunk_reader_result['chunk_size'],
                'average_rows_per_chunk': int(total_rows / chunk_count) if chunk_count > 0 else 0,
                'average_memory_per_chunk': int(total_memory / chunk_count) if chunk_count > 0 else 0,
                'estimated_total_chunks': estimated_total_chunks,
                'estimated_total_rows': estimated_total_rows,
                'estimated_total_memory': estimated_total_memory,
                'processing_recommendation': await self.get_processing_recommendation(estimated_total_memory)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'analyzed_chunks': 0,
                'chunk_statistics': []
            }
    
    async def get_processing_recommendation(self, estimated_memory: int) -> Dict[str, Any]:
        """Get processing recommendations based on data size."""
        memory_gb = estimated_memory / (1024**3)
        
        if memory_gb < 1:
            return {
                'strategy': 'in_memory',
                'message': 'Dataset is small enough for in-memory processing',
                'recommendations': ['Load entire dataset', 'Use standard pandas operations']
            }
        elif memory_gb < 10:
            return {
                'strategy': 'chunked_processing',
                'message': 'Use chunked processing for memory efficiency',
                'recommendations': ['Process in chunks', 'Use incremental algorithms', 'Monitor memory usage']
            }
        else:
            return {
                'strategy': 'distributed_processing',
                'message': 'Consider distributed processing for very large dataset',
                'recommendations': [
                    'Use chunked processing with smaller chunks',
                    'Consider Dask or similar frameworks',
                    'Process subsets independently',
                    'Use streaming algorithms'
                ]
            }
    
    async def create_data_sample(self,
                               file_path: str,
                               sample_size: int = 10000,
                               sampling_method: str = 'random') -> Dict[str, Any]:
        """Create a representative sample from a large file."""
        try:
            # First, get file statistics
            chunk_stats = await self.get_chunk_statistics(file_path)
            
            if not chunk_stats['success']:
                return chunk_stats
            
            estimated_rows = chunk_stats['estimated_total_rows']
            
            if estimated_rows <= sample_size:
                # File is small enough to load entirely
                df = pd.read_csv(file_path)
                return {
                    'success': True,
                    'sample': df,
                    'sample_size': len(df),
                    'sampling_ratio': 1.0,
                    'method': 'full_dataset'
                }
            
            # Calculate sampling parameters
            sampling_ratio = sample_size / estimated_rows
            
            if sampling_method == 'random':
                # Random sampling across chunks
                sample_data = []
                chunk_reader_result = await self.create_chunked_reader(file_path)
                chunk_reader = chunk_reader_result['chunk_reader']
                
                rows_collected = 0
                for chunk in chunk_reader:
                    if rows_collected >= sample_size:
                        break
                    
                    # Sample from this chunk
                    chunk_sample_size = min(
                        int(len(chunk) * sampling_ratio) + 1,
                        sample_size - rows_collected
                    )
                    
                    if chunk_sample_size > 0:
                        chunk_sample = chunk.sample(n=min(chunk_sample_size, len(chunk)))
                        sample_data.append(chunk_sample)
                        rows_collected += len(chunk_sample)
                
                sample_df = pd.concat(sample_data, ignore_index=True) if sample_data else pd.DataFrame()
                
            elif sampling_method == 'systematic':
                # Systematic sampling - every nth row
                step = max(1, estimated_rows // sample_size)
                sample_data = []
                current_row = 0
                target_rows = set(range(0, estimated_rows, step))
                
                chunk_reader_result = await self.create_chunked_reader(file_path)
                chunk_reader = chunk_reader_result['chunk_reader']
                
                for chunk in chunk_reader:
                    chunk_start = current_row
                    chunk_end = current_row + len(chunk)
                    
                    # Find target rows in this chunk
                    chunk_targets = [r - chunk_start for r in target_rows 
                                   if chunk_start <= r < chunk_end]
                    
                    if chunk_targets:
                        sampled_chunk = chunk.iloc[chunk_targets]
                        sample_data.append(sampled_chunk)
                    
                    current_row = chunk_end
                    
                    if len(sample_data) * (sample_size // 100) >= sample_size:
                        break
                
                sample_df = pd.concat(sample_data, ignore_index=True) if sample_data else pd.DataFrame()
                
            else:  # 'head' sampling
                # Take first N rows
                sample_df = pd.read_csv(file_path, nrows=sample_size)
            
            return {
                'success': True,
                'sample': sample_df,
                'sample_size': len(sample_df),
                'sampling_ratio': len(sample_df) / estimated_rows,
                'method': sampling_method,
                'estimated_total_rows': estimated_rows
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'sample': None,
                'sample_size': 0
            }
    
    async def validate_chunk_integrity(self, chunks: List[pd.DataFrame]) -> Dict[str, Any]:
        """Validate integrity of chunked data."""
        try:
            if not chunks:
                return {
                    'success': True,
                    'issues': ['No chunks provided'],
                    'total_rows': 0,
                    'column_consistency': False
                }
            
            issues = []
            total_rows = sum(len(chunk) for chunk in chunks)
            
            # Check column consistency
            base_columns = chunks[0].columns.tolist()
            column_consistent = all(chunk.columns.tolist() == base_columns for chunk in chunks)
            
            if not column_consistent:
                issues.append('Column names are inconsistent across chunks')
            
            # Check data type consistency
            base_dtypes = chunks[0].dtypes
            dtype_issues = []
            
            for i, chunk in enumerate(chunks[1:], 1):
                for col in base_columns:
                    if col in chunk.columns and chunk[col].dtype != base_dtypes[col]:
                        dtype_issues.append(f'Chunk {i}: Column {col} has different dtype')
            
            if dtype_issues:
                issues.extend(dtype_issues)
            
            # Check for gaps in index (if applicable)
            if all(hasattr(chunk.index, 'is_monotonic_increasing') for chunk in chunks):
                index_gaps = []
                prev_max_idx = -1
                
                for i, chunk in enumerate(chunks):
                    min_idx = chunk.index.min()
                    if min_idx != prev_max_idx + 1:
                        index_gaps.append(f'Gap detected between chunk {i-1} and {i}')
                    prev_max_idx = chunk.index.max()
                
                if index_gaps:
                    issues.extend(index_gaps)
            
            return {
                'success': True,
                'issues': issues,
                'total_rows': total_rows,
                'total_chunks': len(chunks),
                'column_consistency': column_consistent,
                'integrity_score': max(0, 100 - len(issues) * 10)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'issues': [],
                'total_rows': 0
            }