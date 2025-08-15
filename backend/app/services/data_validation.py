"""
File: data_validation.py

Overview:
Comprehensive data validation service for quality assessment and issue detection
in datasets with detailed reporting and recommendations.

Purpose:
Validates data quality, detects anomalies, and provides actionable insights
for data processing pipeline optimization.

Dependencies:
- pandas for data analysis
- numpy for numerical operations
- typing for type hints
- datetime for timestamp handling

Last Modified: 2025-08-15
Author: Claude
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
import re

class DataValidationService:
    """Comprehensive data validation with quality scoring and recommendations."""
    
    def __init__(self):
        self.validation_rules = {
            'completeness': ['missing_values', 'empty_strings', 'null_patterns'],
            'consistency': ['data_types', 'format_consistency', 'value_ranges'],
            'uniqueness': ['duplicate_rows', 'duplicate_values', 'unique_constraints'],
            'accuracy': ['outliers', 'invalid_formats', 'constraint_violations'],
            'validity': ['domain_values', 'referential_integrity', 'business_rules']
        }
    
    async def validate_dataset(self, df: pd.DataFrame, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform comprehensive dataset validation."""
        try:
            validation_results = {
                'timestamp': datetime.now().isoformat(),
                'dataset_info': await self.get_dataset_info(df),
                'quality_dimensions': {},
                'issues': [],
                'recommendations': [],
                'overall_score': 0.0
            }
            
            # Run validation checks for each quality dimension
            validation_results['quality_dimensions']['completeness'] = await self.check_completeness(df)
            validation_results['quality_dimensions']['consistency'] = await self.check_consistency(df)
            validation_results['quality_dimensions']['uniqueness'] = await self.check_uniqueness(df)
            validation_results['quality_dimensions']['accuracy'] = await self.check_accuracy(df)
            validation_results['quality_dimensions']['validity'] = await self.check_validity(df, metadata)
            
            # Collect all issues
            for dimension, results in validation_results['quality_dimensions'].items():
                validation_results['issues'].extend(results.get('issues', []))
            
            # Generate recommendations
            validation_results['recommendations'] = await self.generate_recommendations(
                validation_results['quality_dimensions'],
                validation_results['issues']
            )
            
            # Calculate overall quality score
            validation_results['overall_score'] = await self.calculate_overall_score(
                validation_results['quality_dimensions']
            )
            
            return {
                'success': True,
                'validation': validation_results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'validation': None
            }
    
    async def get_dataset_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic dataset information."""
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'dtypes': df.dtypes.value_counts().to_dict(),
            'shape': df.shape
        }
    
    async def check_completeness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check data completeness - missing values, empty strings, etc."""
        issues = []
        
        # Missing values analysis
        missing_counts = df.isnull().sum()
        missing_percentages = (missing_counts / len(df)) * 100
        
        # Empty strings analysis
        empty_string_counts = {}
        for col in df.select_dtypes(include=['object']):
            empty_count = (df[col] == '').sum()
            if empty_count > 0:
                empty_string_counts[col] = empty_count
        
        # Identify problematic columns
        high_missing_cols = missing_percentages[missing_percentages > 50].index.tolist()
        if high_missing_cols:
            issues.append({
                'type': 'high_missing_values',
                'severity': 'high',
                'message': f"Columns with >50% missing values: {high_missing_cols}",
                'affected_columns': high_missing_cols
            })
        
        moderate_missing_cols = missing_percentages[
            (missing_percentages > 10) & (missing_percentages <= 50)
        ].index.tolist()
        if moderate_missing_cols:
            issues.append({
                'type': 'moderate_missing_values',
                'severity': 'medium',
                'message': f"Columns with 10-50% missing values: {moderate_missing_cols}",
                'affected_columns': moderate_missing_cols
            })
        
        # Calculate completeness score
        overall_completeness = 100 - (missing_counts.sum() / (len(df) * len(df.columns))) * 100
        
        return {
            'score': round(overall_completeness, 2),
            'missing_values': missing_counts.to_dict(),
            'missing_percentages': missing_percentages.to_dict(),
            'empty_strings': empty_string_counts,
            'issues': issues,
            'total_missing': missing_counts.sum(),
            'completeness_by_column': (100 - missing_percentages).to_dict()
        }
    
    async def check_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check data consistency - types, formats, ranges."""
        issues = []
        
        # Data type consistency
        type_inconsistencies = []
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check for mixed types in object columns
                non_null_values = df[col].dropna()
                if len(non_null_values) > 0:
                    sample_types = set(type(val).__name__ for val in non_null_values.head(100))
                    if len(sample_types) > 1:
                        type_inconsistencies.append({
                            'column': col,
                            'types_found': list(sample_types)
                        })
        
        if type_inconsistencies:
            issues.append({
                'type': 'mixed_data_types',
                'severity': 'medium',
                'message': f"Columns with mixed data types: {[t['column'] for t in type_inconsistencies]}",
                'details': type_inconsistencies
            })
        
        # Format consistency for strings
        format_issues = []
        for col in df.select_dtypes(include=['object']):
            non_null_values = df[col].dropna().astype(str)
            if len(non_null_values) > 0:
                # Check for email format consistency
                if 'email' in col.lower() or 'mail' in col.lower():
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    invalid_emails = non_null_values[~non_null_values.str.match(email_pattern)]
                    if len(invalid_emails) > 0:
                        format_issues.append({
                            'column': col,
                            'type': 'invalid_email_format',
                            'count': len(invalid_emails)
                        })
                
                # Check for phone format consistency
                if 'phone' in col.lower() or 'tel' in col.lower():
                    phone_pattern = r'^[\+]?[1-9][\d\-\(\)\s]+$'
                    invalid_phones = non_null_values[~non_null_values.str.match(phone_pattern)]
                    if len(invalid_phones) > 0:
                        format_issues.append({
                            'column': col,
                            'type': 'invalid_phone_format',
                            'count': len(invalid_phones)
                        })
        
        if format_issues:
            issues.append({
                'type': 'format_inconsistencies',
                'severity': 'low',
                'message': f"Format inconsistencies found in {len(format_issues)} columns",
                'details': format_issues
            })
        
        # Calculate consistency score
        consistency_score = max(0, 100 - (len(type_inconsistencies) * 10) - (len(format_issues) * 5))
        
        return {
            'score': round(consistency_score, 2),
            'type_inconsistencies': type_inconsistencies,
            'format_issues': format_issues,
            'issues': issues
        }
    
    async def check_uniqueness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check uniqueness constraints and duplicate detection."""
        issues = []
        
        # Duplicate rows
        duplicate_rows = df.duplicated().sum()
        if duplicate_rows > 0:
            issues.append({
                'type': 'duplicate_rows',
                'severity': 'medium',
                'message': f"Found {duplicate_rows} duplicate rows",
                'count': duplicate_rows
            })
        
        # Check uniqueness for each column
        uniqueness_stats = {}
        potential_id_columns = []
        
        for col in df.columns:
            unique_count = df[col].nunique()
            total_non_null = df[col].count()
            uniqueness_ratio = unique_count / total_non_null if total_non_null > 0 else 0
            
            uniqueness_stats[col] = {
                'unique_count': unique_count,
                'total_count': total_non_null,
                'uniqueness_ratio': round(uniqueness_ratio, 4),
                'duplicates': total_non_null - unique_count
            }
            
            # Identify potential ID columns (>95% unique)
            if uniqueness_ratio > 0.95:
                potential_id_columns.append(col)
        
        # Calculate uniqueness score
        avg_uniqueness = np.mean([stats['uniqueness_ratio'] for stats in uniqueness_stats.values()])
        uniqueness_penalty = (duplicate_rows / len(df)) * 50 if len(df) > 0 else 0
        uniqueness_score = max(0, (avg_uniqueness * 100) - uniqueness_penalty)
        
        return {
            'score': round(uniqueness_score, 2),
            'duplicate_rows': duplicate_rows,
            'uniqueness_stats': uniqueness_stats,
            'potential_id_columns': potential_id_columns,
            'issues': issues
        }
    
    async def check_accuracy(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check data accuracy - outliers, invalid values, etc."""
        issues = []
        outliers_info = {}
        
        # Outlier detection for numeric columns
        for col in df.select_dtypes(include=[np.number]):
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            outlier_count = len(outliers)
            
            if outlier_count > 0:
                outliers_info[col] = {
                    'count': outlier_count,
                    'percentage': round((outlier_count / len(df)) * 100, 2),
                    'lower_bound': lower_bound,
                    'upper_bound': upper_bound
                }
                
                if outlier_count > len(df) * 0.05:  # More than 5% outliers
                    issues.append({
                        'type': 'high_outlier_count',
                        'severity': 'medium',
                        'message': f"Column '{col}' has {outlier_count} outliers ({round((outlier_count/len(df))*100, 1)}%)",
                        'column': col,
                        'count': outlier_count
                    })
        
        # Invalid values for specific data types
        invalid_values_info = {}
        for col in df.select_dtypes(include=['object']):
            non_null_values = df[col].dropna()
            if len(non_null_values) > 0:
                # Check for obviously invalid values (very long strings, special characters)
                very_long_strings = non_null_values[non_null_values.str.len() > 1000].count()
                if very_long_strings > 0:
                    invalid_values_info[col] = invalid_values_info.get(col, {})
                    invalid_values_info[col]['very_long_strings'] = very_long_strings
        
        # Calculate accuracy score
        total_outliers = sum(info['count'] for info in outliers_info.values())
        outlier_penalty = (total_outliers / len(df)) * 30 if len(df) > 0 else 0
        accuracy_score = max(0, 100 - outlier_penalty)
        
        return {
            'score': round(accuracy_score, 2),
            'outliers': outliers_info,
            'invalid_values': invalid_values_info,
            'issues': issues
        }
    
    async def check_validity(self, df: pd.DataFrame, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Check data validity against domain rules and constraints."""
        issues = []
        validity_checks = {}
        
        # Basic validity checks
        for col in df.columns:
            col_checks = {}
            
            # Check for negative values where they shouldn't be
            if col.lower() in ['age', 'price', 'cost', 'amount', 'quantity', 'count']:
                if df[col].dtype in [np.int64, np.float64]:
                    negative_count = (df[col] < 0).sum()
                    if negative_count > 0:
                        col_checks['negative_values'] = negative_count
                        issues.append({
                            'type': 'negative_values_unexpected',
                            'severity': 'medium',
                            'message': f"Column '{col}' has {negative_count} negative values",
                            'column': col,
                            'count': negative_count
                        })
            
            # Check date validity
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    pd.to_datetime(df[col], errors='coerce')
                    invalid_dates = df[col].isna().sum() - df[col].isna().sum()
                    if invalid_dates > 0:
                        col_checks['invalid_dates'] = invalid_dates
                except Exception:
                    pass
            
            if col_checks:
                validity_checks[col] = col_checks
        
        # Calculate validity score
        total_validity_issues = sum(
            sum(checks.values()) for checks in validity_checks.values()
        )
        validity_penalty = (total_validity_issues / len(df)) * 40 if len(df) > 0 else 0
        validity_score = max(0, 100 - validity_penalty)
        
        return {
            'score': round(validity_score, 2),
            'validity_checks': validity_checks,
            'issues': issues
        }
    
    async def calculate_overall_score(self, quality_dimensions: Dict[str, Dict[str, Any]]) -> float:
        """Calculate overall data quality score."""
        weights = {
            'completeness': 0.25,
            'consistency': 0.20,
            'uniqueness': 0.20,
            'accuracy': 0.20,
            'validity': 0.15
        }
        
        weighted_score = 0.0
        for dimension, weight in weights.items():
            if dimension in quality_dimensions:
                score = quality_dimensions[dimension].get('score', 0)
                weighted_score += score * weight
        
        return round(weighted_score, 2)
    
    async def generate_recommendations(self, quality_dimensions: Dict[str, Any], issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on validation results."""
        recommendations = []
        
        # Completeness recommendations
        completeness_score = quality_dimensions.get('completeness', {}).get('score', 100)
        if completeness_score < 80:
            recommendations.append({
                'type': 'data_completion',
                'priority': 'high',
                'message': 'Consider imputation strategies for missing values',
                'actions': [
                    'Identify missing data patterns',
                    'Choose appropriate imputation methods',
                    'Validate imputation results'
                ]
            })
        
        # Uniqueness recommendations
        duplicate_rows = quality_dimensions.get('uniqueness', {}).get('duplicate_rows', 0)
        if duplicate_rows > 0:
            recommendations.append({
                'type': 'deduplication',
                'priority': 'medium',
                'message': f'Remove {duplicate_rows} duplicate rows',
                'actions': [
                    'Review duplicate records',
                    'Implement deduplication logic',
                    'Verify data integrity after removal'
                ]
            })
        
        # Consistency recommendations
        consistency_score = quality_dimensions.get('consistency', {}).get('score', 100)
        if consistency_score < 70:
            recommendations.append({
                'type': 'data_standardization',
                'priority': 'medium',
                'message': 'Standardize data formats and types',
                'actions': [
                    'Convert data types consistently',
                    'Standardize format patterns',
                    'Validate format compliance'
                ]
            })
        
        # Accuracy recommendations
        outliers_info = quality_dimensions.get('accuracy', {}).get('outliers', {})
        if outliers_info:
            recommendations.append({
                'type': 'outlier_treatment',
                'priority': 'medium',
                'message': 'Review and handle outlier values',
                'actions': [
                    'Investigate outlier causes',
                    'Apply appropriate outlier treatment',
                    'Document outlier handling decisions'
                ]
            })
        
        return recommendations