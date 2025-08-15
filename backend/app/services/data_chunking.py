"""
File: data_chunking.py

Overview:
Advanced data chunking service for efficient processing of large datasets
with memory management and streaming capabilities

Purpose:
Handles large files (>10MB) by implementing intelligent chunking strategies,
memory-efficient processing, and streaming data operations

Dependencies:
- pandas: Data manipulation with chunked reading
- numpy: Numerical operations and memory management
- asyncio: Asynchronous processing capabilities
- psutil: System resource monitoring

Last Modified: 2025-08-15
Author: Claude
"""

import pandas as pd
import numpy as np
import asyncio
import psutil
from typing import Dict, List, Optional, Any, Tuple, Union, AsyncIterator, Generator
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import logging
import gc
import time
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class ChunkStrategy(Enum):
    """Chunking strategies based on data characteristics"""
    FIXED_SIZE = "fixed_size"
    MEMORY_BASED = "memory_based"
    ADAPTIVE = "adaptive"
    COLUMN_BASED = "column_based"

@dataclass
class ChunkInfo:
    """Information about a data chunk"""
    chunk_id: int
    start_row: int
    end_row: int
    memory_usage: int
    processing_time: float
    row_count: int
    column_count: int

@dataclass
class ChunkingConfig:
    """Configuration for chunking operations"""
    strategy: ChunkStrategy
    max_memory_mb: int
    target_chunk_size: int
    min_chunk_size: int
    max_chunk_size: int
    overlap_rows: int
    enable_parallel: bool

class DataChunkingService:
    """
    Service for intelligent data chunking and memory-efficient processing
    """
    
    def __init__(self, 
                 default_chunk_size: int = 10000,
                 max_memory_percent: float = 0.25,
                 enable_monitoring: bool = True):
        """
        Initialize data chunking service
        
        Args:
            default_chunk_size: Default number of rows per chunk
            max_memory_percent: Maximum percentage of system memory to use
            enable_monitoring: Enable resource monitoring
        """
        self.default_chunk_size = default_chunk_size
        self.max_memory_percent = max_memory_percent
        self.enable_monitoring = enable_monitoring
        
        # System resources
        self.total_memory = psutil.virtual_memory().total
        self.max_memory_bytes = int(self.total_memory * max_memory_percent)
        
        # Performance tracking
        self.chunk_stats = []
        self.processing_history = {}
        
        logger.info(f"Chunking service initialized with max memory: {self.max_memory_bytes / 1024**3:.2f} GB")
    
    def get_optimal_chunk_config(self, file_path: Union[str, Path], 
                                sample_rows: int = 1000) -> ChunkingConfig:
        """
        Determine optimal chunking configuration for a file
        
        Args:
            file_path: Path to the data file
            sample_rows: Number of rows to sample for analysis
            
        Returns:
            Optimal chunking configuration
        """
        try:
            file_path = Path(file_path)
            file_size = file_path.stat().st_size
            
            # Sample the file to estimate memory usage
            sample_df = pd.read_csv(file_path, nrows=sample_rows)
            sample_memory = sample_df.memory_usage(deep=True).sum()
            
            # Estimate total memory if full file was loaded
            estimated_total_memory = (sample_memory / sample_rows) * self._estimate_total_rows(file_path)
            
            logger.info(f"File size: {file_size / 1024**2:.2f} MB, Estimated memory: {estimated_total_memory / 1024**2:.2f} MB")
            
            # Determine strategy based on file characteristics
            if estimated_total_memory <= self.max_memory_bytes * 0.5:
                # Small file - can load entirely
                strategy = ChunkStrategy.FIXED_SIZE
                chunk_size = len(sample_df) * 10  # Larger chunks for small files
            elif estimated_total_memory <= self.max_memory_bytes * 2:
                # Medium file - memory-based chunking
                strategy = ChunkStrategy.MEMORY_BASED
                chunk_size = int(self.max_memory_bytes * 0.8 / (sample_memory / sample_rows))
            else:
                # Large file - adaptive chunking
                strategy = ChunkStrategy.ADAPTIVE
                chunk_size = self.default_chunk_size
            
            # Ensure reasonable bounds
            chunk_size = max(1000, min(chunk_size, 100000))
            
            return ChunkingConfig(
                strategy=strategy,
                max_memory_mb=int(self.max_memory_bytes / 1024**2),
                target_chunk_size=chunk_size,
                min_chunk_size=max(500, chunk_size // 4),
                max_chunk_size=min(200000, chunk_size * 4),
                overlap_rows=0,  # No overlap by default
                enable_parallel=estimated_total_memory > self.max_memory_bytes
            )
            
        except Exception as e:
            logger.warning(f"Could not determine optimal config, using defaults: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> ChunkingConfig:
        """Get default chunking configuration"""
        return ChunkingConfig(
            strategy=ChunkStrategy.FIXED_SIZE,
            max_memory_mb=int(self.max_memory_bytes / 1024**2),
            target_chunk_size=self.default_chunk_size,
            min_chunk_size=5000,
            max_chunk_size=50000,
            overlap_rows=0,
            enable_parallel=False
        )
    
    def _estimate_total_rows(self, file_path: Path) -> int:
        """
        Estimate total number of rows in a CSV file
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Estimated row count
        """
        try:
            # Quick estimation by counting line breaks in a sample
            with open(file_path, 'rb') as f:
                sample_size = min(1024 * 1024, file_path.stat().st_size)  # 1MB sample
                sample = f.read(sample_size)
                
            line_count = sample.count(b'\n')
            file_size = file_path.stat().st_size
            
            estimated_rows = int((line_count * file_size) / sample_size) - 1  # Subtract header
            return max(1, estimated_rows)
            
        except Exception:
            # Fallback estimation based on file size
            file_size_mb = file_path.stat().st_size / 1024**2
            return int(file_size_mb * 1000)  # Rough estimate: 1000 rows per MB
    
    async def process_file_in_chunks(self, 
                                   file_path: Union[str, Path],
                                   processor_func: callable,
                                   config: Optional[ChunkingConfig] = None,
                                   **processor_kwargs) -> Dict[str, Any]:
        """
        Process a file in chunks using the specified processor function
        
        Args:
            file_path: Path to the data file
            processor_func: Function to process each chunk
            config: Chunking configuration
            **processor_kwargs: Additional arguments for processor function
            
        Returns:
            Processing results summary
        """
        if config is None:
            config = self.get_optimal_chunk_config(file_path)
        
        logger.info(f"Starting chunked processing with strategy: {config.strategy.value}")
        
        start_time = time.time()
        processed_chunks = []
        total_rows_processed = 0
        
        try:
            if config.enable_parallel:
                results = await self._process_chunks_parallel(
                    file_path, processor_func, config, **processor_kwargs
                )
            else:
                results = await self._process_chunks_sequential(
                    file_path, processor_func, config, **processor_kwargs
                )
            
            processed_chunks = results["chunks"]
            total_rows_processed = results["total_rows"]
            
        except Exception as e:
            logger.error(f"Chunked processing failed: {e}")
            raise
        
        processing_time = time.time() - start_time
        
        summary = {
            "total_chunks": len(processed_chunks),
            "total_rows_processed": total_rows_processed,
            "processing_time": processing_time,
            "average_chunk_time": processing_time / max(1, len(processed_chunks)),
            "rows_per_second": total_rows_processed / max(1, processing_time),
            "config_used": config.__dict__,
            "chunk_details": processed_chunks
        }
        
        logger.info(f"Chunked processing completed: {len(processed_chunks)} chunks, "
                   f"{total_rows_processed} rows in {processing_time:.2f}s")
        
        return summary
    
    async def _process_chunks_sequential(self, 
                                       file_path: Union[str, Path],
                                       processor_func: callable,
                                       config: ChunkingConfig,
                                       **processor_kwargs) -> Dict[str, Any]:
        """
        Process chunks sequentially
        
        Args:
            file_path: Path to the data file
            processor_func: Function to process each chunk
            config: Chunking configuration
            **processor_kwargs: Additional arguments for processor function
            
        Returns:
            Processing results
        """
        processed_chunks = []
        total_rows = 0
        chunk_id = 0
        
        chunk_reader = pd.read_csv(file_path, chunksize=config.target_chunk_size)
        
        for chunk_df in chunk_reader:
            start_time = time.time()
            start_row = total_rows
            end_row = total_rows + len(chunk_df)
            
            # Monitor memory before processing
            if self.enable_monitoring:
                memory_before = psutil.virtual_memory().percent
                
            try:
                # Process chunk
                chunk_result = await asyncio.get_event_loop().run_in_executor(
                    None, processor_func, chunk_df, **processor_kwargs
                )
                
                processing_time = time.time() - start_time
                memory_usage = chunk_df.memory_usage(deep=True).sum()
                
                chunk_info = ChunkInfo(
                    chunk_id=chunk_id,
                    start_row=start_row,
                    end_row=end_row,
                    memory_usage=memory_usage,
                    processing_time=processing_time,
                    row_count=len(chunk_df),
                    column_count=len(chunk_df.columns)
                )
                
                processed_chunks.append({
                    "chunk_info": chunk_info.__dict__,
                    "result": chunk_result
                })
                
                total_rows += len(chunk_df)
                chunk_id += 1
                
                # Memory monitoring and cleanup
                if self.enable_monitoring:
                    memory_after = psutil.virtual_memory().percent
                    if memory_after > 80:  # High memory usage warning
                        logger.warning(f"High memory usage: {memory_after:.1f}%")
                        gc.collect()  # Force garbage collection
                
                logger.debug(f"Processed chunk {chunk_id}: {len(chunk_df)} rows in {processing_time:.2f}s")
                
            except Exception as e:
                logger.error(f"Error processing chunk {chunk_id}: {e}")
                raise
            
            finally:
                # Clean up chunk from memory
                del chunk_df
                gc.collect()
        
        return {
            "chunks": processed_chunks,
            "total_rows": total_rows
        }
    
    async def _process_chunks_parallel(self, 
                                     file_path: Union[str, Path],
                                     processor_func: callable,
                                     config: ChunkingConfig,
                                     **processor_kwargs) -> Dict[str, Any]:
        """
        Process chunks in parallel using ThreadPoolExecutor
        
        Args:
            file_path: Path to the data file
            processor_func: Function to process each chunk
            config: Chunking configuration
            **processor_kwargs: Additional arguments for processor function
            
        Returns:
            Processing results
        """
        # Read all chunks first (for parallel processing)
        chunks = []
        chunk_reader = pd.read_csv(file_path, chunksize=config.target_chunk_size)
        
        for chunk_df in chunk_reader:
            chunks.append(chunk_df)
        
        logger.info(f"Loaded {len(chunks)} chunks for parallel processing")
        
        # Determine optimal number of workers
        max_workers = min(len(chunks), psutil.cpu_count(), 4)
        
        processed_chunks = []
        total_rows = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all chunks for processing
            futures = []
            for chunk_id, chunk_df in enumerate(chunks):
                future = executor.submit(
                    self._process_single_chunk,
                    chunk_df, chunk_id, total_rows, processor_func, **processor_kwargs
                )
                futures.append(future)
                total_rows += len(chunk_df)
            
            # Collect results
            for future in asyncio.as_completed([
                asyncio.get_event_loop().run_in_executor(None, f.result) for f in futures
            ]):
                try:
                    result = await future
                    processed_chunks.append(result)
                except Exception as e:
                    logger.error(f"Parallel chunk processing failed: {e}")
                    raise
        
        # Clean up
        del chunks
        gc.collect()
        
        return {
            "chunks": processed_chunks,
            "total_rows": total_rows
        }
    
    def _process_single_chunk(self, 
                            chunk_df: pd.DataFrame,
                            chunk_id: int,
                            start_row: int,
                            processor_func: callable,
                            **processor_kwargs) -> Dict[str, Any]:
        """
        Process a single chunk (for parallel execution)
        
        Args:
            chunk_df: DataFrame chunk to process
            chunk_id: Unique chunk identifier
            start_row: Starting row number
            processor_func: Function to process the chunk
            **processor_kwargs: Additional arguments
            
        Returns:
            Processed chunk result
        """
        start_time = time.time()
        end_row = start_row + len(chunk_df)
        
        try:
            # Process chunk
            chunk_result = processor_func(chunk_df, **processor_kwargs)
            
            processing_time = time.time() - start_time
            memory_usage = chunk_df.memory_usage(deep=True).sum()
            
            chunk_info = ChunkInfo(
                chunk_id=chunk_id,
                start_row=start_row,
                end_row=end_row,
                memory_usage=memory_usage,
                processing_time=processing_time,
                row_count=len(chunk_df),
                column_count=len(chunk_df.columns)
            )
            
            return {
                "chunk_info": chunk_info.__dict__,
                "result": chunk_result
            }
            
        except Exception as e:
            logger.error(f"Error processing chunk {chunk_id}: {e}")
            raise
    
    async def stream_chunks(self, 
                          file_path: Union[str, Path],
                          config: Optional[ChunkingConfig] = None) -> AsyncIterator[Tuple[ChunkInfo, pd.DataFrame]]:
        """
        Stream chunks as an async iterator
        
        Args:
            file_path: Path to the data file
            config: Chunking configuration
            
        Yields:
            Tuple of (chunk_info, chunk_dataframe)
        """
        if config is None:
            config = self.get_optimal_chunk_config(file_path)
        
        chunk_reader = pd.read_csv(file_path, chunksize=config.target_chunk_size)
        total_rows = 0
        chunk_id = 0
        
        for chunk_df in chunk_reader:
            start_time = time.time()
            start_row = total_rows
            end_row = total_rows + len(chunk_df)
            
            memory_usage = chunk_df.memory_usage(deep=True).sum()
            processing_time = time.time() - start_time
            
            chunk_info = ChunkInfo(
                chunk_id=chunk_id,
                start_row=start_row,
                end_row=end_row,
                memory_usage=memory_usage,
                processing_time=processing_time,
                row_count=len(chunk_df),
                column_count=len(chunk_df.columns)
            )
            
            yield chunk_info, chunk_df
            
            total_rows += len(chunk_df)
            chunk_id += 1
            
            # Memory cleanup
            if self.enable_monitoring and chunk_id % 10 == 0:
                gc.collect()
    
    def combine_chunk_results(self, 
                            processed_chunks: List[Dict[str, Any]],
                            combine_strategy: str = "concatenate") -> Any:
        """
        Combine results from multiple chunks
        
        Args:
            processed_chunks: List of processed chunk results
            combine_strategy: Strategy for combining results
            
        Returns:
            Combined result
        """
        if not processed_chunks:
            return None
        
        logger.info(f"Combining {len(processed_chunks)} chunk results using {combine_strategy}")
        
        if combine_strategy == "concatenate":
            # Concatenate DataFrames
            results = [chunk["result"] for chunk in processed_chunks if isinstance(chunk["result"], pd.DataFrame)]
            if results:
                return pd.concat(results, ignore_index=True)
        
        elif combine_strategy == "aggregate":
            # Aggregate numeric results
            results = [chunk["result"] for chunk in processed_chunks if isinstance(chunk["result"], (int, float, dict))]
            if results:
                if isinstance(results[0], dict):
                    # Combine dictionaries
                    combined = {}
                    for result in results:
                        for key, value in result.items():
                            if key in combined:
                                if isinstance(value, (int, float)):
                                    combined[key] += value
                                elif isinstance(value, list):
                                    combined[key].extend(value)
                            else:
                                combined[key] = value
                    return combined
                else:
                    # Sum numeric values
                    return sum(results)
        
        elif combine_strategy == "custom":
            # Return all results for custom processing
            return [chunk["result"] for chunk in processed_chunks]
        
        return processed_chunks
    
    def get_chunking_stats(self) -> Dict[str, Any]:
        """
        Get statistics about chunking performance
        
        Returns:
            Chunking performance statistics
        """
        if not self.chunk_stats:
            return {"message": "No chunking statistics available"}
        
        processing_times = [chunk.processing_time for chunk in self.chunk_stats]
        memory_usages = [chunk.memory_usage for chunk in self.chunk_stats]
        row_counts = [chunk.row_count for chunk in self.chunk_stats]
        
        return {
            "total_chunks_processed": len(self.chunk_stats),
            "average_processing_time": np.mean(processing_times),
            "total_processing_time": sum(processing_times),
            "average_memory_usage": np.mean(memory_usages),
            "peak_memory_usage": max(memory_usages),
            "average_rows_per_chunk": np.mean(row_counts),
            "total_rows_processed": sum(row_counts),
            "processing_efficiency": sum(row_counts) / sum(processing_times)  # rows per second
        }
    
    def optimize_chunk_size(self, 
                          file_path: Union[str, Path],
                          target_processing_time: float = 5.0) -> int:
        """
        Optimize chunk size based on target processing time
        
        Args:
            file_path: Path to the data file
            target_processing_time: Target time per chunk in seconds
            
        Returns:
            Optimized chunk size
        """
        # Start with default size and adjust based on performance
        test_sizes = [self.default_chunk_size // 2, self.default_chunk_size, self.default_chunk_size * 2]
        best_size = self.default_chunk_size
        best_efficiency = 0
        
        for size in test_sizes:
            try:
                # Test with small sample
                test_df = pd.read_csv(file_path, nrows=size)
                start_time = time.time()
                
                # Simulate processing (basic operations)
                _ = test_df.describe()
                _ = test_df.isnull().sum()
                
                processing_time = time.time() - start_time
                efficiency = len(test_df) / processing_time
                
                if abs(processing_time - target_processing_time) < abs(best_efficiency - target_processing_time):
                    best_size = size
                    best_efficiency = efficiency
                    
            except Exception as e:
                logger.warning(f"Could not test chunk size {size}: {e}")
        
        logger.info(f"Optimized chunk size: {best_size} (efficiency: {best_efficiency:.2f} rows/sec)")
        return best_size