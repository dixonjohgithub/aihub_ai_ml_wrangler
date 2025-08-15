"""
File: performance_service.py

Overview:
High-performance data processing service for large datasets.

Purpose:
Handles streaming, chunking, parallel processing, and memory optimization for large-scale data operations.

Dependencies:
- dask: Distributed computing
- pyarrow: Memory-efficient data formats
- research_pipeline: Core ML operations

Last Modified: 2025-08-15
Author: Claude
"""

import os
import gc
import psutil
import time
import threading
from typing import Iterator, Optional, Any, Dict, List, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from functools import partial, lru_cache
import warnings

import pandas as pd
import numpy as np
import dask.dataframe as dd
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.compute as pc
from memory_profiler import profile
import joblib

# Import research_pipeline modules
try:
    from app.core.research_pipeline_integration import FeatureImputer, EDA
except ImportError:
    import sys
    sys.path.insert(0, '/Users/johndixon/AI_Hub/research_pipeline')
    from research_pipeline.feature_imputer import FeatureImputer
    from research_pipeline.eda import EDA

logger = logging.getLogger(__name__)


@dataclass
class PerformanceConfig:
    """Configuration for performance optimization"""
    chunk_size: int = 10000
    max_workers: int = 4
    memory_limit_gb: float = 4.0
    use_dask: bool = True
    use_caching: bool = True
    cache_dir: str = ".cache"
    compression: str = "snappy"
    streaming_threshold_mb: int = 100
    enable_profiling: bool = False


@dataclass
class PerformanceMetrics:
    """Performance metrics for operations"""
    operation: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    rows_processed: int = 0
    memory_used_mb: float = 0.0
    cpu_percent: float = 0.0
    chunks_processed: int = 0
    errors: List[str] = field(default_factory=list)
    
    def complete(self):
        """Mark operation as complete"""
        self.end_time = datetime.now()
        self.duration_seconds = (self.end_time - self.start_time).total_seconds()


class StreamingDataProcessor:
    """
    Handles streaming processing for large datasets
    """
    
    def __init__(self, config: PerformanceConfig):
        """Initialize streaming processor"""
        self.config = config
        self.cache_dir = Path(config.cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.metrics: List[PerformanceMetrics] = []
        
    def read_csv_in_chunks(
        self,
        filepath: str,
        chunk_size: Optional[int] = None,
        **kwargs
    ) -> Iterator[pd.DataFrame]:
        """
        Read CSV file in chunks
        
        Args:
            filepath: Path to CSV file
            chunk_size: Rows per chunk
            **kwargs: Additional pandas read_csv arguments
            
        Yields:
            DataFrame chunks
        """
        chunk_size = chunk_size or self.config.chunk_size
        
        # Check file size
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        logger.info(f"Reading {filepath} ({file_size_mb:.2f} MB) in chunks of {chunk_size} rows")
        
        # Create chunk reader
        reader = pd.read_csv(filepath, chunksize=chunk_size, **kwargs)
        
        for i, chunk in enumerate(reader):
            logger.debug(f"Processing chunk {i+1} with {len(chunk)} rows")
            yield chunk
    
    def process_with_dask(
        self,
        filepath: str,
        operation: Callable[[pd.DataFrame], pd.DataFrame],
        output_path: Optional[str] = None,
        **kwargs
    ) -> dd.DataFrame:
        """
        Process large file using Dask
        
        Args:
            filepath: Input file path
            operation: Function to apply to each partition
            output_path: Optional output path
            **kwargs: Additional arguments
            
        Returns:
            Dask DataFrame
        """
        metrics = PerformanceMetrics(operation="dask_processing")
        
        try:
            # Read with Dask
            ddf = dd.read_csv(filepath, blocksize="64MB", **kwargs)
            
            # Apply operation to each partition
            result = ddf.map_partitions(operation)
            
            # Persist in memory if small enough
            if result.memory_usage_per_partition().sum().compute() < self.config.memory_limit_gb * 1024**3:
                result = result.persist()
            
            # Save if output path provided
            if output_path:
                if output_path.endswith('.parquet'):
                    result.to_parquet(output_path, compression=self.config.compression)
                else:
                    result.to_csv(output_path, single_file=True)
            
            metrics.rows_processed = len(result)
            metrics.complete()
            self.metrics.append(metrics)
            
            return result
            
        except Exception as e:
            metrics.errors.append(str(e))
            metrics.complete()
            self.metrics.append(metrics)
            raise
    
    def parallel_apply(
        self,
        df: pd.DataFrame,
        func: Callable,
        axis: int = 0,
        n_workers: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Apply function in parallel using multiple workers
        
        Args:
            df: Input DataFrame
            func: Function to apply
            axis: Axis to apply along (0 for rows, 1 for columns)
            n_workers: Number of workers
            
        Returns:
            Processed DataFrame
        """
        n_workers = n_workers or self.config.max_workers
        
        if axis == 0:
            # Split by rows
            chunks = np.array_split(df, n_workers)
        else:
            # Split by columns
            chunks = [df[cols] for cols in np.array_split(df.columns, n_workers)]
        
        with ProcessPoolExecutor(max_workers=n_workers) as executor:
            futures = [executor.submit(func, chunk) for chunk in chunks]
            results = [future.result() for future in as_completed(futures)]
        
        # Combine results
        if axis == 0:
            return pd.concat(results, ignore_index=True)
        else:
            return pd.concat(results, axis=1)
    
    def optimize_memory(self, df: pd.DataFrame, aggressive: bool = False) -> pd.DataFrame:
        """
        Optimize DataFrame memory usage
        
        Args:
            df: Input DataFrame
            aggressive: Use aggressive optimization
            
        Returns:
            Memory-optimized DataFrame
        """
        initial_memory = df.memory_usage(deep=True).sum() / 1024**2
        logger.info(f"Initial memory usage: {initial_memory:.2f} MB")
        
        # Optimize numeric columns
        for col in df.select_dtypes(include=['int']).columns:
            col_min = df[col].min()
            col_max = df[col].max()
            
            if col_min >= 0:
                if col_max < 255:
                    df[col] = df[col].astype(np.uint8)
                elif col_max < 65535:
                    df[col] = df[col].astype(np.uint16)
                elif col_max < 4294967295:
                    df[col] = df[col].astype(np.uint32)
            else:
                if col_min > np.iinfo(np.int8).min and col_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif col_min > np.iinfo(np.int16).min and col_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif col_min > np.iinfo(np.int32).min and col_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
        
        # Optimize float columns
        for col in df.select_dtypes(include=['float']).columns:
            if aggressive:
                df[col] = df[col].astype(np.float32)
            else:
                col_min = df[col].min()
                col_max = df[col].max()
                if col_min > np.finfo(np.float32).min and col_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
        
        # Convert object columns to category if applicable
        for col in df.select_dtypes(include=['object']).columns:
            num_unique = df[col].nunique()
            num_total = len(df[col])
            if num_unique / num_total < 0.5:  # Less than 50% unique
                df[col] = df[col].astype('category')
        
        final_memory = df.memory_usage(deep=True).sum() / 1024**2
        reduction = (initial_memory - final_memory) / initial_memory * 100
        logger.info(f"Final memory usage: {final_memory:.2f} MB (reduced by {reduction:.1f}%)")
        
        return df
    
    def incremental_computation(
        self,
        filepath: str,
        operations: List[Callable],
        checkpoint_interval: int = 1000
    ) -> pd.DataFrame:
        """
        Perform incremental computation with checkpointing
        
        Args:
            filepath: Input file path
            operations: List of operations to apply
            checkpoint_interval: Rows between checkpoints
            
        Returns:
            Processed DataFrame
        """
        checkpoint_file = self.cache_dir / f"checkpoint_{Path(filepath).stem}.parquet"
        
        # Check if checkpoint exists
        if checkpoint_file.exists():
            logger.info(f"Loading from checkpoint: {checkpoint_file}")
            df = pd.read_parquet(checkpoint_file)
            start_row = len(df)
        else:
            df = pd.DataFrame()
            start_row = 0
        
        # Process incrementally
        for i, chunk in enumerate(self.read_csv_in_chunks(filepath, skiprows=start_row)):
            # Apply operations
            for op in operations:
                chunk = op(chunk)
            
            # Append to result
            df = pd.concat([df, chunk], ignore_index=True)
            
            # Save checkpoint
            if (i + 1) % checkpoint_interval == 0:
                df.to_parquet(checkpoint_file, compression=self.config.compression)
                logger.info(f"Checkpoint saved at row {len(df)}")
        
        # Final save
        df.to_parquet(checkpoint_file, compression=self.config.compression)
        
        return df


class PerformanceMonitor:
    """
    Monitor and track performance metrics
    """
    
    def __init__(self):
        """Initialize performance monitor"""
        self.metrics_history: List[PerformanceMetrics] = []
        self.resource_monitor_thread = None
        self.monitoring = False
        self.current_resources = {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'memory_mb': 0.0,
            'disk_io_read_mb': 0.0,
            'disk_io_write_mb': 0.0
        }
    
    def start_monitoring(self, interval: float = 1.0):
        """Start resource monitoring"""
        self.monitoring = True
        self.resource_monitor_thread = threading.Thread(
            target=self._monitor_resources,
            args=(interval,),
            daemon=True
        )
        self.resource_monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        if self.resource_monitor_thread:
            self.resource_monitor_thread.join(timeout=2)
    
    def _monitor_resources(self, interval: float):
        """Monitor system resources"""
        process = psutil.Process()
        
        while self.monitoring:
            try:
                self.current_resources['cpu_percent'] = process.cpu_percent()
                memory_info = process.memory_info()
                self.current_resources['memory_mb'] = memory_info.rss / 1024**2
                self.current_resources['memory_percent'] = process.memory_percent()
                
                # Disk I/O if available
                try:
                    io_counters = process.io_counters()
                    self.current_resources['disk_io_read_mb'] = io_counters.read_bytes / 1024**2
                    self.current_resources['disk_io_write_mb'] = io_counters.write_bytes / 1024**2
                except:
                    pass
                
            except Exception as e:
                logger.warning(f"Resource monitoring error: {e}")
            
            time.sleep(interval)
    
    def estimate_processing_time(
        self,
        data_size_mb: float,
        operation_type: str = "general"
    ) -> Dict[str, float]:
        """
        Estimate processing time based on data size and operation
        
        Args:
            data_size_mb: Size of data in MB
            operation_type: Type of operation
            
        Returns:
            Time estimates in seconds
        """
        # Simple heuristic-based estimation
        base_rates = {
            'read': 100,  # MB/s
            'write': 80,   # MB/s
            'imputation': 10,  # MB/s
            'correlation': 5,  # MB/s
            'general': 20  # MB/s
        }
        
        rate = base_rates.get(operation_type, base_rates['general'])
        
        estimates = {
            'optimistic': data_size_mb / (rate * 1.5),
            'expected': data_size_mb / rate,
            'pessimistic': data_size_mb / (rate * 0.5)
        }
        
        return estimates
    
    def detect_bottlenecks(self) -> List[Dict[str, Any]]:
        """
        Detect performance bottlenecks
        
        Returns:
            List of detected bottlenecks
        """
        bottlenecks = []
        
        # Check CPU usage
        if self.current_resources['cpu_percent'] > 90:
            bottlenecks.append({
                'type': 'CPU',
                'severity': 'high',
                'value': self.current_resources['cpu_percent'],
                'recommendation': 'Consider using more workers or optimizing algorithms'
            })
        
        # Check memory usage
        if self.current_resources['memory_percent'] > 80:
            bottlenecks.append({
                'type': 'Memory',
                'severity': 'high' if self.current_resources['memory_percent'] > 90 else 'medium',
                'value': self.current_resources['memory_percent'],
                'recommendation': 'Use chunking or streaming for large datasets'
            })
        
        # Check I/O
        if len(self.metrics_history) > 0:
            recent_metrics = self.metrics_history[-5:]
            avg_duration = np.mean([m.duration_seconds for m in recent_metrics])
            avg_rows = np.mean([m.rows_processed for m in recent_metrics])
            
            if avg_rows > 0:
                rows_per_second = avg_rows / avg_duration
                if rows_per_second < 1000:
                    bottlenecks.append({
                        'type': 'I/O',
                        'severity': 'medium',
                        'value': rows_per_second,
                        'recommendation': 'Consider using faster storage or caching'
                    })
        
        return bottlenecks
    
    def create_performance_dashboard(self) -> Dict[str, Any]:
        """
        Create performance dashboard data
        
        Returns:
            Dashboard data dictionary
        """
        dashboard = {
            'current_resources': self.current_resources,
            'bottlenecks': self.detect_bottlenecks(),
            'metrics_summary': {},
            'recommendations': []
        }
        
        if self.metrics_history:
            # Summarize metrics
            total_duration = sum(m.duration_seconds for m in self.metrics_history)
            total_rows = sum(m.rows_processed for m in self.metrics_history)
            
            dashboard['metrics_summary'] = {
                'total_operations': len(self.metrics_history),
                'total_duration_seconds': total_duration,
                'total_rows_processed': total_rows,
                'average_rows_per_second': total_rows / total_duration if total_duration > 0 else 0,
                'total_errors': sum(len(m.errors) for m in self.metrics_history)
            }
            
            # Generate recommendations
            if dashboard['metrics_summary']['average_rows_per_second'] < 1000:
                dashboard['recommendations'].append(
                    "Processing speed is below optimal. Consider parallel processing."
                )
            
            if dashboard['metrics_summary']['total_errors'] > 0:
                dashboard['recommendations'].append(
                    "Errors detected during processing. Review error logs."
                )
        
        return dashboard


class CacheManager:
    """
    Manage caching for expensive operations
    """
    
    def __init__(self, cache_dir: str = ".cache"):
        """Initialize cache manager"""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_index = self._load_cache_index()
    
    def _load_cache_index(self) -> Dict[str, Dict[str, Any]]:
        """Load cache index"""
        index_file = self.cache_dir / "cache_index.json"
        if index_file.exists():
            import json
            with open(index_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_cache_index(self):
        """Save cache index"""
        import json
        index_file = self.cache_dir / "cache_index.json"
        with open(index_file, 'w') as f:
            json.dump(self.cache_index, f, default=str)
    
    def get_cache_key(self, operation: str, params: Dict[str, Any]) -> str:
        """Generate cache key"""
        import hashlib
        key_str = f"{operation}_{str(sorted(params.items()))}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    @lru_cache(maxsize=128)
    def get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get cached result"""
        if cache_key in self.cache_index:
            cache_info = self.cache_index[cache_key]
            cache_file = self.cache_dir / cache_info['filename']
            
            if cache_file.exists():
                # Check if cache is still valid
                if 'expires_at' in cache_info:
                    expires_at = datetime.fromisoformat(cache_info['expires_at'])
                    if datetime.now() > expires_at:
                        return None
                
                # Load cached data
                if cache_file.suffix == '.parquet':
                    return pd.read_parquet(cache_file)
                elif cache_file.suffix == '.pkl':
                    return joblib.load(cache_file)
                elif cache_file.suffix == '.npy':
                    return np.load(cache_file)
        
        return None
    
    def cache_result(
        self,
        cache_key: str,
        result: Any,
        operation: str,
        ttl_hours: Optional[int] = 24
    ):
        """Cache result"""
        # Determine file format based on result type
        if isinstance(result, pd.DataFrame):
            filename = f"{cache_key}.parquet"
            filepath = self.cache_dir / filename
            result.to_parquet(filepath, compression='snappy')
        elif isinstance(result, np.ndarray):
            filename = f"{cache_key}.npy"
            filepath = self.cache_dir / filename
            np.save(filepath, result)
        else:
            filename = f"{cache_key}.pkl"
            filepath = self.cache_dir / filename
            joblib.dump(result, filepath)
        
        # Update cache index
        cache_info = {
            'filename': filename,
            'operation': operation,
            'created_at': datetime.now().isoformat(),
            'size_bytes': filepath.stat().st_size
        }
        
        if ttl_hours:
            expires_at = datetime.now() + pd.Timedelta(hours=ttl_hours)
            cache_info['expires_at'] = expires_at.isoformat()
        
        self.cache_index[cache_key] = cache_info
        self._save_cache_index()
    
    def clear_expired_cache(self):
        """Clear expired cache entries"""
        expired_keys = []
        
        for cache_key, cache_info in self.cache_index.items():
            if 'expires_at' in cache_info:
                expires_at = datetime.fromisoformat(cache_info['expires_at'])
                if datetime.now() > expires_at:
                    expired_keys.append(cache_key)
                    # Delete file
                    cache_file = self.cache_dir / cache_info['filename']
                    if cache_file.exists():
                        cache_file.unlink()
        
        # Remove from index
        for key in expired_keys:
            del self.cache_index[key]
        
        self._save_cache_index()
        logger.info(f"Cleared {len(expired_keys)} expired cache entries")


class PerformanceOptimizer:
    """
    Main performance optimization service integrating all components
    """
    
    def __init__(self, config: Optional[PerformanceConfig] = None):
        """Initialize performance optimizer"""
        self.config = config or PerformanceConfig()
        self.processor = StreamingDataProcessor(self.config)
        self.monitor = PerformanceMonitor()
        self.cache = CacheManager(self.config.cache_dir)
        
        # Start monitoring
        self.monitor.start_monitoring()
    
    def process_large_dataset(
        self,
        filepath: str,
        operations: List[Callable],
        output_path: Optional[str] = None,
        use_research_pipeline: bool = True
    ) -> pd.DataFrame:
        """
        Process large dataset with optimizations
        
        Args:
            filepath: Input file path
            operations: List of operations to apply
            output_path: Optional output path
            use_research_pipeline: Use research_pipeline for ML operations
            
        Returns:
            Processed DataFrame
        """
        file_size_mb = os.path.getsize(filepath) / (1024**2)
        logger.info(f"Processing {filepath} ({file_size_mb:.2f} MB)")
        
        # Estimate processing time
        estimates = self.monitor.estimate_processing_time(file_size_mb, 'general')
        logger.info(f"Estimated processing time: {estimates['expected']:.1f} seconds")
        
        # Check cache
        cache_key = self.cache.get_cache_key('process_dataset', {
            'filepath': filepath,
            'operations': str(operations)
        })
        cached_result = self.cache.get_cached_result(cache_key)
        if cached_result is not None:
            logger.info("Using cached result")
            return cached_result
        
        # Decide processing strategy
        if file_size_mb > self.config.streaming_threshold_mb:
            if self.config.use_dask:
                # Use Dask for very large files
                logger.info("Using Dask for processing")
                
                # Create composite operation
                def composite_op(df):
                    for op in operations:
                        df = op(df)
                    return df
                
                result = self.processor.process_with_dask(
                    filepath, composite_op, output_path
                )
                
                # Convert to pandas if small enough
                if file_size_mb < self.config.memory_limit_gb * 1024:
                    result = result.compute()
            else:
                # Use streaming
                logger.info("Using streaming processing")
                result = self.processor.incremental_computation(
                    filepath, operations
                )
        else:
            # Process normally with memory optimization
            logger.info("Processing in memory")
            df = pd.read_csv(filepath)
            df = self.processor.optimize_memory(df)
            
            for op in operations:
                if use_research_pipeline and hasattr(op, '__name__'):
                    # Check if this is an imputation operation
                    if 'imput' in op.__name__.lower():
                        imputer = FeatureImputer(df)
                        df = imputer.impute_data()
                    # Check if this is an EDA operation
                    elif 'eda' in op.__name__.lower() or 'corr' in op.__name__.lower():
                        eda = EDA(df)
                        # Apply EDA operation
                        df = op(df)
                    else:
                        df = op(df)
                else:
                    df = op(df)
            
            result = df
        
        # Cache result
        self.cache.cache_result(cache_key, result, 'process_dataset')
        
        # Save if output path provided
        if output_path and isinstance(result, pd.DataFrame):
            if output_path.endswith('.parquet'):
                result.to_parquet(output_path, compression=self.config.compression)
            else:
                result.to_csv(output_path, index=False)
        
        return result
    
    def auto_scale_workers(self) -> int:
        """
        Automatically determine optimal number of workers
        
        Returns:
            Optimal number of workers
        """
        cpu_count = psutil.cpu_count(logical=False)
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        # Check current resource usage
        bottlenecks = self.monitor.detect_bottlenecks()
        
        # Adjust based on bottlenecks
        if any(b['type'] == 'CPU' for b in bottlenecks):
            # CPU bottleneck - don't increase workers
            return min(2, cpu_count)
        elif any(b['type'] == 'Memory' for b in bottlenecks):
            # Memory bottleneck - reduce workers
            return max(1, cpu_count // 2)
        else:
            # No bottlenecks - use more workers
            return min(cpu_count, int(memory_gb))
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        Get comprehensive performance report
        
        Returns:
            Performance report dictionary
        """
        dashboard = self.monitor.create_performance_dashboard()
        
        # Add cache statistics
        cache_stats = {
            'cache_entries': len(self.cache.cache_index),
            'cache_size_mb': sum(
                (self.cache.cache_dir / info['filename']).stat().st_size / (1024**2)
                for info in self.cache.cache_index.values()
                if (self.cache.cache_dir / info['filename']).exists()
            )
        }
        
        # Add optimization suggestions
        suggestions = []
        
        if dashboard['current_resources']['memory_percent'] > 70:
            suggestions.append("Consider using Dask or chunking for large datasets")
        
        if dashboard['current_resources']['cpu_percent'] < 50:
            suggestions.append("CPU underutilized - consider increasing parallel workers")
        
        if cache_stats['cache_entries'] > 100:
            suggestions.append("Cache size growing - consider clearing old entries")
        
        return {
            **dashboard,
            'cache_statistics': cache_stats,
            'optimization_suggestions': suggestions,
            'config': {
                'chunk_size': self.config.chunk_size,
                'max_workers': self.config.max_workers,
                'memory_limit_gb': self.config.memory_limit_gb,
                'optimal_workers': self.auto_scale_workers()
            }
        }
    
    def cleanup(self):
        """Cleanup resources"""
        self.monitor.stop_monitoring()
        self.cache.clear_expired_cache()
        gc.collect()