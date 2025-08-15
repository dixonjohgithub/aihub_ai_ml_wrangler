"""
File: type_detection.py

Overview:
Advanced column type detection algorithm with confidence scoring
for numeric, categorical, binary, datetime, and special data types.

Purpose:
Automatically detects and classifies column data types with high accuracy
to enable appropriate processing and analysis strategies.

Dependencies:
- pandas for data analysis
- numpy for numerical operations
- re for pattern matching
- typing for type hints

Last Modified: 2025-08-15
Author: Claude
"""

import asyncio
import re
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
import numpy as np
from datetime import datetime

class TypeDetector:
    """Advanced column type detection with confidence scoring."""
    
    def __init__(self):
        self.type_patterns = {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'url': r'^https?://[^\s/$.?#].[^\s]*$',
            'phone': r'^[\+]?[1-9][\d\-\(\)\s]{7,}$',
            'ip_address': r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
            'credit_card': r'^\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}$',
            'social_security': r'^\d{3}-\d{2}-\d{4}$',
            'zip_code': r'^\d{5}(-\d{4})?$',
            'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        }
        
        self.date_formats = [
            '%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S',
            '%d-%m-%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ',
            '%m/%d/%Y', '%m-%d-%Y', '%B %d, %Y', '%b %d, %Y'
        ]
    
    async def detect_column_types(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect types for all columns in the dataframe."""
        try:
            results = {
                'timestamp': datetime.now().isoformat(),
                'total_columns': len(df.columns),
                'columns': {},
                'summary': {
                    'numeric': [],
                    'categorical': [],
                    'binary': [],
                    'datetime': [],
                    'text': [],
                    'special': [],
                    'unknown': []
                }
            }
            
            for col in df.columns:
                col_analysis = await self.analyze_column(df[col], col)
                results['columns'][col] = col_analysis
                
                # Add to appropriate summary category
                primary_type = col_analysis['primary_type']
                if primary_type in results['summary']:
                    results['summary'][primary_type].append(col)
                else:
                    results['summary']['unknown'].append(col)
            
            # Add type distribution
            results['type_distribution'] = {
                type_name: len(columns) 
                for type_name, columns in results['summary'].items()
            }
            
            return {
                'success': True,
                'type_detection': results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'type_detection': None
            }
    
    async def analyze_column(self, series: pd.Series, column_name: str) -> Dict[str, Any]:
        """Analyze a single column to determine its data type."""
        # Basic statistics
        total_count = len(series)
        non_null_count = series.count()
        null_count = total_count - non_null_count
        null_percentage = (null_count / total_count) * 100 if total_count > 0 else 0
        
        # Remove null values for analysis
        non_null_series = series.dropna()
        
        if len(non_null_series) == 0:
            return {
                'primary_type': 'unknown',
                'confidence': 0.0,
                'null_percentage': 100.0,
                'details': {'reason': 'All values are null'}
            }
        
        # Type detection results
        type_scores = {}
        
        # Check numeric types
        numeric_score = await self.check_numeric_type(non_null_series)
        if numeric_score > 0:
            type_scores['numeric'] = numeric_score
        
        # Check binary type
        binary_score = await self.check_binary_type(non_null_series)
        if binary_score > 0:
            type_scores['binary'] = binary_score
        
        # Check datetime type
        datetime_score = await self.check_datetime_type(non_null_series)
        if datetime_score > 0:
            type_scores['datetime'] = datetime_score
        
        # Check categorical type
        categorical_score = await self.check_categorical_type(non_null_series)
        if categorical_score > 0:
            type_scores['categorical'] = categorical_score
        
        # Check special types (email, URL, etc.)
        special_type, special_score = await self.check_special_types(non_null_series)
        if special_score > 0:
            type_scores['special'] = special_score
        
        # Check text type
        text_score = await self.check_text_type(non_null_series)
        if text_score > 0:
            type_scores['text'] = text_score
        
        # Determine primary type and confidence
        if type_scores:
            primary_type = max(type_scores, key=type_scores.get)
            confidence = type_scores[primary_type]
        else:
            primary_type = 'unknown'
            confidence = 0.0
        
        # Generate detailed analysis
        details = await self.generate_type_details(
            non_null_series, primary_type, column_name
        )
        
        return {
            'primary_type': primary_type,
            'confidence': round(confidence, 2),
            'null_percentage': round(null_percentage, 2),
            'type_scores': {k: round(v, 2) for k, v in type_scores.items()},
            'details': details,
            'sample_values': non_null_series.head(5).tolist(),
            'unique_count': non_null_series.nunique(),
            'most_common': non_null_series.value_counts().head(3).to_dict()
        }
    
    async def check_numeric_type(self, series: pd.Series) -> float:
        """Check if column contains numeric data."""
        try:
            # Try converting to numeric
            numeric_series = pd.to_numeric(series, errors='coerce')
            valid_numeric_count = numeric_series.count()
            total_count = len(series)
            
            if valid_numeric_count == 0:
                return 0.0
            
            numeric_percentage = valid_numeric_count / total_count
            
            # Additional checks for numeric confidence
            confidence_boost = 0.0
            
            # Check if already numeric type
            if series.dtype in [np.int64, np.float64, np.int32, np.float32]:
                confidence_boost += 0.2
            
            # Check for reasonable numeric ranges
            if valid_numeric_count > 0:
                numeric_values = numeric_series.dropna()
                if len(numeric_values) > 0:
                    # Check if values are within reasonable ranges
                    min_val, max_val = numeric_values.min(), numeric_values.max()
                    if abs(min_val) < 1e10 and abs(max_val) < 1e10:
                        confidence_boost += 0.1
            
            return min(1.0, numeric_percentage + confidence_boost)
            
        except Exception:
            return 0.0
    
    async def check_binary_type(self, series: pd.Series) -> float:
        """Check if column contains binary data."""
        unique_values = set(series.astype(str).str.lower())
        
        # Common binary patterns
        binary_patterns = [
            {'yes', 'no'},
            {'true', 'false'},
            {'1', '0'},
            {'y', 'n'},
            {'t', 'f'},
            {'on', 'off'},
            {'active', 'inactive'},
            {'enabled', 'disabled'},
            {'male', 'female'},
            {'m', 'f'}
        ]
        
        # Check for exact binary matches
        for pattern in binary_patterns:
            if unique_values == pattern:
                return 1.0
        
        # Check for two unique values (potential binary)
        if len(unique_values) == 2:
            return 0.8
        
        # Check for mostly binary with some noise
        if len(unique_values) <= 3:
            most_common_2 = series.value_counts().head(2).sum()
            coverage = most_common_2 / len(series)
            if coverage > 0.9:
                return 0.6
        
        return 0.0
    
    async def check_datetime_type(self, series: pd.Series) -> float:
        """Check if column contains datetime data."""
        try:
            # First check if column name suggests datetime
            col_keywords = ['date', 'time', 'timestamp', 'created', 'updated', 'modified']
            name_suggests_date = any(keyword in series.name.lower() for keyword in col_keywords) if series.name else False
            
            # Try pandas datetime conversion
            datetime_series = pd.to_datetime(series, errors='coerce')
            valid_datetime_count = datetime_series.count()
            total_count = len(series)
            
            if valid_datetime_count == 0:
                return 0.0
            
            datetime_percentage = valid_datetime_count / total_count
            
            # Check specific date patterns
            sample_values = series.astype(str).head(20)
            pattern_matches = 0
            
            for value in sample_values:
                for pattern in self.date_formats:
                    try:
                        datetime.strptime(value, pattern)
                        pattern_matches += 1
                        break
                    except ValueError:
                        continue
            
            pattern_score = pattern_matches / len(sample_values) if sample_values.size > 0 else 0
            
            # Combine scores
            base_score = datetime_percentage
            if name_suggests_date:
                base_score += 0.2
            if pattern_score > 0.5:
                base_score += 0.2
            
            return min(1.0, base_score)
            
        except Exception:
            return 0.0
    
    async def check_categorical_type(self, series: pd.Series) -> float:
        """Check if column is categorical."""
        unique_count = series.nunique()
        total_count = len(series)
        
        if unique_count == 0:
            return 0.0
        
        # Calculate uniqueness ratio
        uniqueness_ratio = unique_count / total_count
        
        # Categorical indicators
        if uniqueness_ratio < 0.05:  # Very few unique values
            return 0.9
        elif uniqueness_ratio < 0.1:
            return 0.8
        elif uniqueness_ratio < 0.2:
            return 0.7
        elif uniqueness_ratio < 0.5:
            return 0.5
        else:
            # High cardinality, might still be categorical if text-based
            if series.dtype == 'object':
                # Check if values look like categories
                sample_values = series.astype(str).head(10)
                avg_length = sample_values.str.len().mean()
                
                # Short strings are more likely to be categorical
                if avg_length < 20:
                    return 0.3
                elif avg_length < 50:
                    return 0.2
            
            return 0.1
    
    async def check_special_types(self, series: pd.Series) -> Tuple[str, float]:
        """Check for special data types (email, URL, phone, etc.)."""
        sample_values = series.astype(str).head(50)
        
        best_match = None
        best_score = 0.0
        
        for type_name, pattern in self.type_patterns.items():
            matches = sum(1 for value in sample_values if re.match(pattern, value, re.IGNORECASE))
            match_percentage = matches / len(sample_values) if len(sample_values) > 0 else 0
            
            if match_percentage > best_score:
                best_score = match_percentage
                best_match = type_name
        
        # Only return if confidence is high enough
        if best_score > 0.7:
            return best_match, best_score
        
        return None, 0.0
    
    async def check_text_type(self, series: pd.Series) -> float:
        """Check if column contains text data."""
        if series.dtype != 'object':
            return 0.0
        
        # Convert to string and analyze
        str_series = series.astype(str)
        
        # Check average length
        avg_length = str_series.str.len().mean()
        
        # Check for text characteristics
        has_spaces = str_series.str.contains(' ').sum() / len(str_series)
        has_punctuation = str_series.str.contains(r'[.!?,:;]').sum() / len(str_series)
        
        # Text indicators
        text_score = 0.0
        
        if avg_length > 50:  # Long strings
            text_score += 0.4
        elif avg_length > 20:
            text_score += 0.2
        
        if has_spaces > 0.5:  # Contains spaces
            text_score += 0.3
        
        if has_punctuation > 0.2:  # Contains punctuation
            text_score += 0.2
        
        # High cardinality suggests text
        uniqueness_ratio = series.nunique() / len(series)
        if uniqueness_ratio > 0.8:
            text_score += 0.3
        
        return min(1.0, text_score)
    
    async def generate_type_details(self, series: pd.Series, primary_type: str, column_name: str) -> Dict[str, Any]:
        """Generate detailed information about the detected type."""
        details = {
            'inferred_type': primary_type,
            'pandas_dtype': str(series.dtype),
            'memory_usage': series.memory_usage(deep=True)
        }
        
        if primary_type == 'numeric':
            numeric_series = pd.to_numeric(series, errors='coerce').dropna()
            if len(numeric_series) > 0:
                details.update({
                    'min_value': float(numeric_series.min()),
                    'max_value': float(numeric_series.max()),
                    'mean': float(numeric_series.mean()),
                    'std': float(numeric_series.std()),
                    'is_integer': bool(numeric_series.apply(lambda x: x.is_integer()).all())
                })
        
        elif primary_type == 'categorical':
            details.update({
                'unique_values': series.nunique(),
                'top_categories': series.value_counts().head(5).to_dict(),
                'cardinality': 'low' if series.nunique() < 10 else 'high'
            })
        
        elif primary_type == 'datetime':
            datetime_series = pd.to_datetime(series, errors='coerce').dropna()
            if len(datetime_series) > 0:
                details.update({
                    'earliest_date': datetime_series.min().isoformat(),
                    'latest_date': datetime_series.max().isoformat(),
                    'date_range_days': (datetime_series.max() - datetime_series.min()).days
                })
        
        elif primary_type == 'binary':
            details.update({
                'binary_values': sorted(series.unique()),
                'value_distribution': series.value_counts().to_dict()
            })
        
        elif primary_type == 'text':
            str_series = series.astype(str)
            details.update({
                'avg_length': round(str_series.str.len().mean(), 2),
                'max_length': int(str_series.str.len().max()),
                'contains_spaces': bool(str_series.str.contains(' ').any()),
                'language_detected': 'unknown'  # Could add language detection
            })
        
        return details