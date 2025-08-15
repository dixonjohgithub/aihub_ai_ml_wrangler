"""
File: type_detection.py

Overview:
Advanced column type detection algorithm that automatically identifies data types
including numeric, categorical, binary, datetime, and text columns with high accuracy

Purpose:
Provides intelligent data type detection beyond pandas' basic inference,
including semantic type detection and data format recognition

Dependencies:
- pandas: Data manipulation and basic type inference
- numpy: Numerical operations and array handling
- re: Regular expression pattern matching
- dateutil: Advanced date parsing capabilities

Last Modified: 2025-08-15
Author: Claude
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from dateutil import parser as date_parser
import logging

logger = logging.getLogger(__name__)

class DataType(Enum):
    """Enumeration of detected data types"""
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    CATEGORICAL = "categorical"
    BINARY = "binary"
    DATETIME = "datetime"
    TEXT = "text"
    EMAIL = "email"
    URL = "url"
    PHONE = "phone"
    IDENTIFIER = "identifier"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    UNKNOWN = "unknown"

@dataclass
class TypeDetectionResult:
    """Result of type detection for a column"""
    column_name: str
    detected_type: DataType
    confidence: float
    pandas_dtype: str
    suggested_dtype: str
    metadata: Dict[str, Any]
    issues: List[str]

class ColumnTypeDetector:
    """
    Advanced column type detection with semantic analysis
    """
    
    def __init__(self, confidence_threshold: float = 0.8, sample_size: int = 1000):
        """
        Initialize type detector
        
        Args:
            confidence_threshold: Minimum confidence for type detection
            sample_size: Number of samples to analyze for large datasets
        """
        self.confidence_threshold = confidence_threshold
        self.sample_size = sample_size
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, re.Pattern]:
        """
        Initialize regex patterns for semantic type detection
        
        Returns:
            Dictionary of compiled regex patterns
        """
        return {
            'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            'url': re.compile(r'^https?://[^\s/$.?#].[^\s]*$', re.IGNORECASE),
            'phone': re.compile(r'^[\+]?[1-9]?[\d\s\-\(\)\.]{7,15}$'),
            'currency': re.compile(r'^[\$\€\£\¥]?[\d,]+\.?\d*$'),
            'percentage': re.compile(r'^\d+\.?\d*%$'),
            'identifier': re.compile(r'^[A-Z0-9]{8,}$|^\d{8,}$'),
            'date_iso': re.compile(r'^\d{4}-\d{2}-\d{2}'),
            'date_us': re.compile(r'^\d{1,2}/\d{1,2}/\d{4}'),
            'date_eu': re.compile(r'^\d{1,2}\.\d{1,2}\.\d{4}'),
            'time': re.compile(r'^\d{1,2}:\d{2}(:\d{2})?')
        }
    
    def detect_column_types(self, df: pd.DataFrame) -> Dict[str, TypeDetectionResult]:
        """
        Detect types for all columns in a DataFrame
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary mapping column names to detection results
        """
        logger.info(f"Starting type detection for {len(df.columns)} columns")
        
        results = {}
        
        for column in df.columns:
            try:
                result = self.detect_single_column_type(df[column], column)
                results[column] = result
                logger.debug(f"Column '{column}': {result.detected_type.value} (confidence: {result.confidence:.3f})")
            except Exception as e:
                logger.error(f"Type detection failed for column '{column}': {e}")
                results[column] = TypeDetectionResult(
                    column_name=column,
                    detected_type=DataType.UNKNOWN,
                    confidence=0.0,
                    pandas_dtype=str(df[column].dtype),
                    suggested_dtype="object",
                    metadata={"error": str(e)},
                    issues=[f"Type detection failed: {e}"]
                )
        
        logger.info("Type detection completed")
        return results
    
    def detect_single_column_type(self, series: pd.Series, column_name: str) -> TypeDetectionResult:
        """
        Detect type for a single column
        
        Args:
            series: Pandas Series to analyze
            column_name: Name of the column
            
        Returns:
            Type detection result
        """
        # Get sample for analysis
        sample = self._get_sample(series)
        
        # Initialize result
        result = TypeDetectionResult(
            column_name=column_name,
            detected_type=DataType.UNKNOWN,
            confidence=0.0,
            pandas_dtype=str(series.dtype),
            suggested_dtype=str(series.dtype),
            metadata={},
            issues=[]
        )
        
        # Basic statistics
        total_count = len(sample)
        non_null_count = sample.count()
        null_count = total_count - non_null_count
        
        if non_null_count == 0:
            result.detected_type = DataType.UNKNOWN
            result.issues.append("Column contains only null values")
            return result
        
        # Remove null values for analysis
        clean_sample = sample.dropna()
        
        # Calculate basic metrics
        unique_count = clean_sample.nunique()
        unique_ratio = unique_count / non_null_count
        
        result.metadata.update({
            "total_count": total_count,
            "non_null_count": non_null_count,
            "null_count": null_count,
            "unique_count": unique_count,
            "unique_ratio": unique_ratio
        })
        
        # Start type detection pipeline
        detection_results = []
        
        # 1. Check for boolean type
        bool_result = self._detect_boolean(clean_sample, result.metadata)
        detection_results.append(bool_result)
        
        # 2. Check for binary categorical
        binary_result = self._detect_binary_categorical(clean_sample, result.metadata)
        detection_results.append(binary_result)
        
        # 3. Check for numeric types
        numeric_result = self._detect_numeric(clean_sample, result.metadata)
        detection_results.append(numeric_result)
        
        # 4. Check for datetime
        datetime_result = self._detect_datetime(clean_sample, result.metadata)
        detection_results.append(datetime_result)
        
        # 5. Check for semantic types (email, URL, etc.)
        semantic_result = self._detect_semantic_types(clean_sample, result.metadata)
        detection_results.append(semantic_result)
        
        # 6. Check for categorical
        categorical_result = self._detect_categorical(clean_sample, result.metadata)
        detection_results.append(categorical_result)
        
        # 7. Default to text
        text_result = self._detect_text(clean_sample, result.metadata)
        detection_results.append(text_result)
        
        # Select best result
        best_result = max(detection_results, key=lambda x: x[1])
        detected_type, confidence, suggested_dtype, type_metadata = best_result
        
        result.detected_type = detected_type
        result.confidence = confidence
        result.suggested_dtype = suggested_dtype
        result.metadata.update(type_metadata)
        
        # Add quality warnings
        if confidence < self.confidence_threshold:
            result.issues.append(f"Low confidence in type detection: {confidence:.3f}")
        
        if unique_ratio > 0.95 and detected_type != DataType.IDENTIFIER:
            result.issues.append("High cardinality detected - consider if this should be an identifier")
        
        return result
    
    def _get_sample(self, series: pd.Series) -> pd.Series:
        """
        Get a representative sample of the series
        
        Args:
            series: Series to sample
            
        Returns:
            Sample series
        """
        if len(series) <= self.sample_size:
            return series
        
        # Use stratified sampling to maintain distribution
        return series.sample(n=self.sample_size, random_state=42)
    
    def _detect_boolean(self, series: pd.Series, metadata: Dict[str, Any]) -> Tuple[DataType, float, str, Dict[str, Any]]:
        """
        Detect boolean type
        
        Args:
            series: Series to analyze
            metadata: Existing metadata
            
        Returns:
            Tuple of (type, confidence, suggested_dtype, type_metadata)
        """
        type_metadata = {}
        
        # Check pandas boolean dtype
        if pd.api.types.is_bool_dtype(series):
            return DataType.BOOLEAN, 1.0, "bool", type_metadata
        
        # Check for boolean-like values
        unique_values = set(str(val).lower().strip() for val in series.unique())
        
        boolean_patterns = [
            {'true', 'false'},
            {'1', '0'},
            {'yes', 'no'},
            {'y', 'n'},
            {'on', 'off'},
            {'enabled', 'disabled'},
            {'active', 'inactive'}
        ]
        
        for pattern in boolean_patterns:
            if unique_values == pattern:
                type_metadata['boolean_pattern'] = pattern
                return DataType.BOOLEAN, 0.9, "bool", type_metadata
        
        return DataType.UNKNOWN, 0.0, "object", type_metadata
    
    def _detect_binary_categorical(self, series: pd.Series, metadata: Dict[str, Any]) -> Tuple[DataType, float, str, Dict[str, Any]]:
        """
        Detect binary categorical type
        
        Args:
            series: Series to analyze
            metadata: Existing metadata
            
        Returns:
            Tuple of (type, confidence, suggested_dtype, type_metadata)
        """
        type_metadata = {}
        
        unique_count = series.nunique()
        
        if unique_count == 2:
            values = series.unique()
            type_metadata['categories'] = values.tolist()
            
            # Check if it's numeric binary
            if all(pd.api.types.is_numeric_dtype(type(val)) for val in values):
                return DataType.BINARY, 0.8, "category", type_metadata
            else:
                return DataType.BINARY, 0.9, "category", type_metadata
        
        return DataType.UNKNOWN, 0.0, "object", type_metadata
    
    def _detect_numeric(self, series: pd.Series, metadata: Dict[str, Any]) -> Tuple[DataType, float, str, Dict[str, Any]]:
        """
        Detect numeric types (integer/float)
        
        Args:
            series: Series to analyze
            metadata: Existing metadata
            
        Returns:
            Tuple of (type, confidence, suggested_dtype, type_metadata)
        """
        type_metadata = {}
        
        # Check if already numeric
        if pd.api.types.is_integer_dtype(series):
            type_metadata['numeric_subtype'] = 'integer'
            return DataType.INTEGER, 1.0, "int64", type_metadata
        
        if pd.api.types.is_float_dtype(series):
            # Check if it's actually integer values stored as float
            if series.dropna().apply(lambda x: float(x).is_integer()).all():
                type_metadata['numeric_subtype'] = 'integer_as_float'
                return DataType.INTEGER, 0.9, "int64", type_metadata
            else:
                type_metadata['numeric_subtype'] = 'float'
                return DataType.FLOAT, 1.0, "float64", type_metadata
        
        # Try to convert string to numeric
        try:
            # Clean common numeric formatting
            cleaned = series.astype(str).str.replace(',', '').str.replace('$', '').str.strip()
            numeric_series = pd.to_numeric(cleaned, errors='coerce')
            
            conversion_rate = numeric_series.count() / len(series)
            
            if conversion_rate >= 0.95:  # 95% conversion rate
                # Check if integers
                if numeric_series.dropna().apply(lambda x: float(x).is_integer()).all():
                    type_metadata['numeric_subtype'] = 'string_integer'
                    return DataType.INTEGER, conversion_rate, "int64", type_metadata
                else:
                    type_metadata['numeric_subtype'] = 'string_float'
                    return DataType.FLOAT, conversion_rate, "float64", type_metadata
        
        except Exception:
            pass
        
        return DataType.UNKNOWN, 0.0, "object", type_metadata
    
    def _detect_datetime(self, series: pd.Series, metadata: Dict[str, Any]) -> Tuple[DataType, float, str, Dict[str, Any]]:
        """
        Detect datetime type
        
        Args:
            series: Series to analyze
            metadata: Existing metadata
            
        Returns:
            Tuple of (type, confidence, suggested_dtype, type_metadata)
        """
        type_metadata = {}
        
        # Check if already datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            return DataType.DATETIME, 1.0, "datetime64[ns]", type_metadata
        
        # Check for common date patterns
        sample_values = series.astype(str).head(20)
        
        pattern_matches = 0
        total_patterns = len(self.patterns['date_iso'].pattern) + len(self.patterns['date_us'].pattern) + len(self.patterns['date_eu'].pattern)
        
        for value in sample_values:
            if (self.patterns['date_iso'].match(value) or 
                self.patterns['date_us'].match(value) or 
                self.patterns['date_eu'].match(value)):
                pattern_matches += 1
        
        pattern_confidence = pattern_matches / len(sample_values) if len(sample_values) > 0 else 0
        
        # Try parsing with dateutil
        parse_successes = 0
        for value in series.head(20):
            try:
                date_parser.parse(str(value))
                parse_successes += 1
            except:
                continue
        
        parse_confidence = parse_successes / min(20, len(series))
        
        confidence = max(pattern_confidence, parse_confidence)
        
        if confidence >= 0.8:
            type_metadata['datetime_patterns'] = {
                'pattern_confidence': pattern_confidence,
                'parse_confidence': parse_confidence
            }
            return DataType.DATETIME, confidence, "datetime64[ns]", type_metadata
        
        return DataType.UNKNOWN, 0.0, "object", type_metadata
    
    def _detect_semantic_types(self, series: pd.Series, metadata: Dict[str, Any]) -> Tuple[DataType, float, str, Dict[str, Any]]:
        """
        Detect semantic types (email, URL, phone, etc.)
        
        Args:
            series: Series to analyze
            metadata: Existing metadata
            
        Returns:
            Tuple of (type, confidence, suggested_dtype, type_metadata)
        """
        type_metadata = {}
        
        sample_values = series.astype(str).head(50)
        
        # Check each semantic type
        semantic_checks = [
            (DataType.EMAIL, self.patterns['email']),
            (DataType.URL, self.patterns['url']),
            (DataType.PHONE, self.patterns['phone']),
            (DataType.CURRENCY, self.patterns['currency']),
            (DataType.PERCENTAGE, self.patterns['percentage']),
            (DataType.IDENTIFIER, self.patterns['identifier'])
        ]
        
        for data_type, pattern in semantic_checks:
            matches = sum(1 for val in sample_values if pattern.match(str(val).strip()))
            confidence = matches / len(sample_values) if len(sample_values) > 0 else 0
            
            if confidence >= 0.8:
                type_metadata[f'{data_type.value}_confidence'] = confidence
                return data_type, confidence, "object", type_metadata
        
        return DataType.UNKNOWN, 0.0, "object", type_metadata
    
    def _detect_categorical(self, series: pd.Series, metadata: Dict[str, Any]) -> Tuple[DataType, float, str, Dict[str, Any]]:
        """
        Detect categorical type
        
        Args:
            series: Series to analyze
            metadata: Existing metadata
            
        Returns:
            Tuple of (type, confidence, suggested_dtype, type_metadata)
        """
        type_metadata = {}
        
        unique_ratio = metadata.get('unique_ratio', series.nunique() / len(series))
        
        # Categorical if low unique ratio and reasonable number of categories
        if unique_ratio <= 0.1 and series.nunique() <= 50:
            categories = series.value_counts()
            type_metadata['categories'] = categories.to_dict()
            type_metadata['category_count'] = len(categories)
            
            confidence = 1.0 - unique_ratio  # Higher confidence for lower unique ratio
            return DataType.CATEGORICAL, confidence, "category", type_metadata
        
        return DataType.UNKNOWN, 0.0, "object", type_metadata
    
    def _detect_text(self, series: pd.Series, metadata: Dict[str, Any]) -> Tuple[DataType, float, str, Dict[str, Any]]:
        """
        Detect text type (fallback)
        
        Args:
            series: Series to analyze
            metadata: Existing metadata
            
        Returns:
            Tuple of (type, confidence, suggested_dtype, type_metadata)
        """
        type_metadata = {}
        
        # Calculate text characteristics
        text_series = series.astype(str)
        lengths = text_series.str.len()
        
        type_metadata['text_stats'] = {
            'avg_length': float(lengths.mean()),
            'max_length': int(lengths.max()),
            'min_length': int(lengths.min()),
            'std_length': float(lengths.std())
        }
        
        # Text is the fallback type
        return DataType.TEXT, 0.5, "object", type_metadata
    
    def optimize_dtypes(self, df: pd.DataFrame, 
                       detection_results: Dict[str, TypeDetectionResult]) -> pd.DataFrame:
        """
        Optimize DataFrame dtypes based on detection results
        
        Args:
            df: Original DataFrame
            detection_results: Type detection results
            
        Returns:
            DataFrame with optimized dtypes
        """
        logger.info("Optimizing DataFrame dtypes based on detection results")
        
        optimized_df = df.copy()
        conversions_applied = []
        
        for column, result in detection_results.items():
            if result.confidence >= self.confidence_threshold:
                try:
                    if result.detected_type == DataType.INTEGER:
                        optimized_df[column] = pd.to_numeric(optimized_df[column], errors='coerce').astype('Int64')
                        conversions_applied.append(f"{column}: {result.detected_type.value}")
                    
                    elif result.detected_type == DataType.FLOAT:
                        optimized_df[column] = pd.to_numeric(optimized_df[column], errors='coerce')
                        conversions_applied.append(f"{column}: {result.detected_type.value}")
                    
                    elif result.detected_type == DataType.BOOLEAN:
                        optimized_df[column] = optimized_df[column].map({'true': True, 'false': False, '1': True, '0': False})
                        conversions_applied.append(f"{column}: {result.detected_type.value}")
                    
                    elif result.detected_type in [DataType.CATEGORICAL, DataType.BINARY]:
                        optimized_df[column] = optimized_df[column].astype('category')
                        conversions_applied.append(f"{column}: {result.detected_type.value}")
                    
                    elif result.detected_type == DataType.DATETIME:
                        optimized_df[column] = pd.to_datetime(optimized_df[column], errors='coerce')
                        conversions_applied.append(f"{column}: {result.detected_type.value}")
                
                except Exception as e:
                    logger.warning(f"Failed to convert column '{column}' to {result.detected_type.value}: {e}")
        
        logger.info(f"Applied {len(conversions_applied)} dtype conversions: {conversions_applied}")
        return optimized_df
    
    def generate_type_report(self, detection_results: Dict[str, TypeDetectionResult]) -> Dict[str, Any]:
        """
        Generate a comprehensive type detection report
        
        Args:
            detection_results: Type detection results
            
        Returns:
            Type detection report
        """
        report = {
            "summary": {
                "total_columns": len(detection_results),
                "high_confidence_detections": 0,
                "low_confidence_detections": 0,
                "type_distribution": {}
            },
            "column_details": {},
            "recommendations": []
        }
        
        for column, result in detection_results.items():
            # Update summary
            if result.confidence >= self.confidence_threshold:
                report["summary"]["high_confidence_detections"] += 1
            else:
                report["summary"]["low_confidence_detections"] += 1
            
            detected_type = result.detected_type.value
            report["summary"]["type_distribution"][detected_type] = (
                report["summary"]["type_distribution"].get(detected_type, 0) + 1
            )
            
            # Add column details
            report["column_details"][column] = {
                "detected_type": detected_type,
                "confidence": result.confidence,
                "current_dtype": result.pandas_dtype,
                "suggested_dtype": result.suggested_dtype,
                "issues": result.issues,
                "metadata": result.metadata
            }
        
        # Generate recommendations
        low_confidence_columns = [
            col for col, result in detection_results.items()
            if result.confidence < self.confidence_threshold
        ]
        
        if low_confidence_columns:
            report["recommendations"].append(
                f"Review columns with low confidence detection: {low_confidence_columns}"
            )
        
        high_cardinality_columns = [
            col for col, result in detection_results.items()
            if result.metadata.get('unique_ratio', 0) > 0.95
        ]
        
        if high_cardinality_columns:
            report["recommendations"].append(
                f"Consider if high cardinality columns should be identifiers: {high_cardinality_columns}"
            )
        
        return report