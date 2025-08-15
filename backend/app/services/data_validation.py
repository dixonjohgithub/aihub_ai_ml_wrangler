"""
File: data_validation.py

Overview:
Comprehensive data validation service for detecting quality issues, inconsistencies,
and data integrity problems in datasets

Purpose:
Provides robust validation capabilities including schema validation, data quality checks,
statistical outlier detection, and business rule validation

Dependencies:
- pandas: Data manipulation and analysis
- numpy: Numerical operations and statistical functions
- scipy: Advanced statistical functions
- re: Regular expression pattern matching

Last Modified: 2025-08-15
Author: Claude
"""

import pandas as pd
import numpy as np
from scipy import stats
import re
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ValidationIssue:
    """Data class for validation issues"""
    issue_type: str
    severity: ValidationSeverity
    column: Optional[str]
    description: str
    affected_rows: Optional[List[int]] = None
    suggested_action: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DataValidationService:
    """
    Comprehensive data validation service with multiple validation strategies
    """
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize data validation service
        
        Args:
            strict_mode: If True, applies stricter validation rules
        """
        self.strict_mode = strict_mode
        self.validation_rules = self._initialize_validation_rules()
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """
        Initialize default validation rules
        
        Returns:
            Dictionary of validation rules and thresholds
        """
        return {
            "missing_data_threshold": 0.5 if not self.strict_mode else 0.3,
            "outlier_threshold": 3.0,  # Standard deviations for outlier detection
            "duplicate_threshold": 0.1,  # Maximum allowed duplicate percentage
            "cardinality_threshold": 0.95,  # High cardinality threshold
            "low_cardinality_threshold": 0.01,  # Low cardinality threshold
            "string_length_variance_threshold": 10.0,  # Coefficient of variation
            "date_range_years": 100,  # Reasonable date range in years
            "numeric_precision_threshold": 15  # Maximum precision for floating point
        }
    
    def validate_dataset(self, df: pd.DataFrame, 
                        metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive dataset validation
        
        Args:
            df: DataFrame to validate
            metadata: Optional metadata for enhanced validation
            
        Returns:
            Comprehensive validation report
        """
        logger.info(f"Starting validation for dataset with shape {df.shape}")
        
        validation_report = {
            "dataset_info": {
                "shape": df.shape,
                "memory_usage": df.memory_usage(deep=True).sum(),
                "validation_timestamp": datetime.now().isoformat()
            },
            "issues": [],
            "summary": {},
            "column_reports": {},
            "recommendations": []
        }
        
        try:
            # Basic structural validation
            self._validate_structure(df, validation_report)
            
            # Column-level validation
            for column in df.columns:
                column_report = self._validate_column(df, column, metadata)
                validation_report["column_reports"][column] = column_report
                validation_report["issues"].extend(column_report["issues"])
            
            # Cross-column validation
            self._validate_relationships(df, validation_report)
            
            # Data quality scoring
            validation_report["quality_score"] = self._calculate_quality_score(validation_report)
            
            # Generate summary
            validation_report["summary"] = self._generate_summary(validation_report)
            
            # Generate recommendations
            validation_report["recommendations"] = self._generate_recommendations(
                validation_report, df
            )
            
            logger.info("Dataset validation completed successfully")
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            validation_report["issues"].append(
                ValidationIssue(
                    issue_type="validation_error",
                    severity=ValidationSeverity.CRITICAL,
                    column=None,
                    description=f"Validation process failed: {e}"
                ).__dict__
            )
        
        return validation_report
    
    def _validate_structure(self, df: pd.DataFrame, report: Dict[str, Any]) -> None:
        """
        Validate basic dataset structure
        
        Args:
            df: DataFrame to validate
            report: Validation report to update
        """
        issues = []
        
        # Check for empty dataset
        if df.empty:
            issues.append(ValidationIssue(
                issue_type="empty_dataset",
                severity=ValidationSeverity.CRITICAL,
                column=None,
                description="Dataset is empty",
                suggested_action="Verify data source and loading process"
            ))
        
        # Check for duplicate column names
        duplicate_columns = df.columns[df.columns.duplicated()].tolist()
        if duplicate_columns:
            issues.append(ValidationIssue(
                issue_type="duplicate_columns",
                severity=ValidationSeverity.ERROR,
                column=None,
                description=f"Duplicate column names found: {duplicate_columns}",
                suggested_action="Rename duplicate columns with unique identifiers"
            ))
        
        # Check for completely empty rows
        empty_rows = df.index[df.isnull().all(axis=1)].tolist()
        if empty_rows:
            issues.append(ValidationIssue(
                issue_type="empty_rows",
                severity=ValidationSeverity.WARNING,
                column=None,
                description=f"Found {len(empty_rows)} completely empty rows",
                affected_rows=empty_rows[:100],  # Limit for performance
                suggested_action="Remove empty rows or investigate data source"
            ))
        
        # Check for duplicate rows
        duplicate_rows = df.index[df.duplicated()].tolist()
        if duplicate_rows:
            duplicate_percentage = (len(duplicate_rows) / len(df)) * 100
            severity = (ValidationSeverity.ERROR if duplicate_percentage > 
                       self.validation_rules["duplicate_threshold"] * 100 
                       else ValidationSeverity.WARNING)
            
            issues.append(ValidationIssue(
                issue_type="duplicate_rows",
                severity=severity,
                column=None,
                description=f"Found {len(duplicate_rows)} duplicate rows ({duplicate_percentage:.2f}%)",
                affected_rows=duplicate_rows[:100],
                suggested_action="Remove duplicates or investigate if duplicates are valid"
            ))
        
        # Add issues to report
        report["issues"].extend([issue.__dict__ for issue in issues])
    
    def _validate_column(self, df: pd.DataFrame, column: str, 
                        metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate individual column
        
        Args:
            df: DataFrame containing the column
            column: Column name to validate
            metadata: Optional column metadata
            
        Returns:
            Column validation report
        """
        series = df[column]
        column_report = {
            "column_name": column,
            "data_type": str(series.dtype),
            "statistics": self._calculate_column_statistics(series),
            "issues": []
        }
        
        issues = []
        
        # Missing data validation
        missing_count = series.isnull().sum()
        missing_percentage = (missing_count / len(series)) * 100
        
        if missing_percentage > self.validation_rules["missing_data_threshold"] * 100:
            issues.append(ValidationIssue(
                issue_type="high_missing_data",
                severity=ValidationSeverity.WARNING,
                column=column,
                description=f"High missing data: {missing_percentage:.2f}%",
                suggested_action="Consider imputation strategies or investigate data collection"
            ))
        
        # Data type specific validation
        if pd.api.types.is_numeric_dtype(series):
            issues.extend(self._validate_numeric_column(series, column))
        elif pd.api.types.is_string_dtype(series) or series.dtype == 'object':
            issues.extend(self._validate_string_column(series, column))
        elif pd.api.types.is_datetime64_any_dtype(series):
            issues.extend(self._validate_datetime_column(series, column))
        elif pd.api.types.is_bool_dtype(series):
            issues.extend(self._validate_boolean_column(series, column))
        
        # Cardinality validation
        issues.extend(self._validate_cardinality(series, column))
        
        # Metadata validation if provided
        if metadata:
            issues.extend(self._validate_against_metadata(series, column, metadata))
        
        column_report["issues"] = [issue.__dict__ for issue in issues]
        return column_report
    
    def _validate_numeric_column(self, series: pd.Series, column: str) -> List[ValidationIssue]:
        """
        Validate numeric column
        
        Args:
            series: Numeric series to validate
            column: Column name
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Remove NaN values for validation
        clean_series = series.dropna()
        
        if len(clean_series) == 0:
            return issues
        
        # Outlier detection using Z-score
        z_scores = np.abs(stats.zscore(clean_series))
        outliers = clean_series[z_scores > self.validation_rules["outlier_threshold"]]
        
        if len(outliers) > 0:
            outlier_percentage = (len(outliers) / len(clean_series)) * 100
            issues.append(ValidationIssue(
                issue_type="outliers_detected",
                severity=ValidationSeverity.WARNING,
                column=column,
                description=f"Found {len(outliers)} outliers ({outlier_percentage:.2f}%)",
                metadata={"outlier_values": outliers.tolist()[:10]},
                suggested_action="Investigate outliers for data entry errors or valid extreme values"
            ))
        
        # Check for infinite values
        infinite_count = np.isinf(clean_series).sum()
        if infinite_count > 0:
            issues.append(ValidationIssue(
                issue_type="infinite_values",
                severity=ValidationSeverity.ERROR,
                column=column,
                description=f"Found {infinite_count} infinite values",
                suggested_action="Replace infinite values with appropriate substitutes"
            ))
        
        # Check for extremely large precision (potential data quality issue)
        if series.dtype == 'float64':
            decimal_places = clean_series.apply(lambda x: len(str(x).split('.')[-1]) if '.' in str(x) else 0)
            max_precision = decimal_places.max()
            
            if max_precision > self.validation_rules["numeric_precision_threshold"]:
                issues.append(ValidationIssue(
                    issue_type="high_precision",
                    severity=ValidationSeverity.INFO,
                    column=column,
                    description=f"Maximum decimal precision: {max_precision} digits",
                    suggested_action="Consider rounding to appropriate precision"
                ))
        
        # Check for constant values
        if clean_series.nunique() == 1:
            issues.append(ValidationIssue(
                issue_type="constant_column",
                severity=ValidationSeverity.WARNING,
                column=column,
                description="Column contains only one unique value",
                suggested_action="Consider removing constant columns"
            ))
        
        return issues
    
    def _validate_string_column(self, series: pd.Series, column: str) -> List[ValidationIssue]:
        """
        Validate string column
        
        Args:
            series: String series to validate
            column: Column name
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Remove NaN values for validation
        clean_series = series.dropna().astype(str)
        
        if len(clean_series) == 0:
            return issues
        
        # Check string length consistency
        string_lengths = clean_series.str.len()
        length_cv = string_lengths.std() / string_lengths.mean() if string_lengths.mean() > 0 else 0
        
        if length_cv > self.validation_rules["string_length_variance_threshold"]:
            issues.append(ValidationIssue(
                issue_type="inconsistent_string_lengths",
                severity=ValidationSeverity.INFO,
                column=column,
                description=f"High string length variation (CV: {length_cv:.2f})",
                metadata={"min_length": int(string_lengths.min()), "max_length": int(string_lengths.max())},
                suggested_action="Investigate if varying lengths are expected"
            ))
        
        # Check for leading/trailing whitespace
        whitespace_issues = clean_series[
            (clean_series != clean_series.str.strip())
        ]
        
        if len(whitespace_issues) > 0:
            issues.append(ValidationIssue(
                issue_type="whitespace_issues",
                severity=ValidationSeverity.WARNING,
                column=column,
                description=f"Found {len(whitespace_issues)} values with leading/trailing whitespace",
                suggested_action="Trim whitespace from string values"
            ))
        
        # Check for empty strings
        empty_strings = clean_series[clean_series == '']
        if len(empty_strings) > 0:
            issues.append(ValidationIssue(
                issue_type="empty_strings",
                severity=ValidationSeverity.WARNING,
                column=column,
                description=f"Found {len(empty_strings)} empty strings",
                suggested_action="Consider treating empty strings as missing values"
            ))
        
        # Check for special characters or encoding issues
        special_char_pattern = re.compile(r'[^\x00-\x7F]')
        special_chars = clean_series[clean_series.str.contains(special_char_pattern, na=False)]
        
        if len(special_chars) > 0:
            issues.append(ValidationIssue(
                issue_type="special_characters",
                severity=ValidationSeverity.INFO,
                column=column,
                description=f"Found {len(special_chars)} values with non-ASCII characters",
                suggested_action="Verify encoding and character handling requirements"
            ))
        
        return issues
    
    def _validate_datetime_column(self, series: pd.Series, column: str) -> List[ValidationIssue]:
        """
        Validate datetime column
        
        Args:
            series: Datetime series to validate
            column: Column name
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Remove NaN values for validation
        clean_series = series.dropna()
        
        if len(clean_series) == 0:
            return issues
        
        # Check for reasonable date range
        min_date = clean_series.min()
        max_date = clean_series.max()
        date_range_years = (max_date - min_date).days / 365.25
        
        if date_range_years > self.validation_rules["date_range_years"]:
            issues.append(ValidationIssue(
                issue_type="wide_date_range",
                severity=ValidationSeverity.WARNING,
                column=column,
                description=f"Date range spans {date_range_years:.1f} years",
                metadata={"min_date": str(min_date), "max_date": str(max_date)},
                suggested_action="Verify if wide date range is expected"
            ))
        
        # Check for future dates (if current context suggests they shouldn't exist)
        future_dates = clean_series[clean_series > pd.Timestamp.now()]
        if len(future_dates) > 0:
            issues.append(ValidationIssue(
                issue_type="future_dates",
                severity=ValidationSeverity.INFO,
                column=column,
                description=f"Found {len(future_dates)} future dates",
                suggested_action="Verify if future dates are valid for this context"
            ))
        
        return issues
    
    def _validate_boolean_column(self, series: pd.Series, column: str) -> List[ValidationIssue]:
        """
        Validate boolean column
        
        Args:
            series: Boolean series to validate
            column: Column name
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Check for imbalanced boolean distribution
        value_counts = series.value_counts(dropna=True)
        if len(value_counts) == 2:
            balance_ratio = min(value_counts) / max(value_counts)
            if balance_ratio < 0.1:  # Less than 10% balance
                issues.append(ValidationIssue(
                    issue_type="imbalanced_boolean",
                    severity=ValidationSeverity.INFO,
                    column=column,
                    description=f"Imbalanced boolean distribution (ratio: {balance_ratio:.3f})",
                    metadata={"value_counts": value_counts.to_dict()},
                    suggested_action="Consider if imbalance is expected for this variable"
                ))
        
        return issues
    
    def _validate_cardinality(self, series: pd.Series, column: str) -> List[ValidationIssue]:
        """
        Validate column cardinality
        
        Args:
            series: Series to validate
            column: Column name
            
        Returns:
            List of validation issues
        """
        issues = []
        
        unique_count = series.nunique()
        total_count = len(series.dropna())
        
        if total_count == 0:
            return issues
        
        cardinality_ratio = unique_count / total_count
        
        # High cardinality check
        if cardinality_ratio > self.validation_rules["cardinality_threshold"]:
            issues.append(ValidationIssue(
                issue_type="high_cardinality",
                severity=ValidationSeverity.INFO,
                column=column,
                description=f"High cardinality: {unique_count}/{total_count} unique values",
                suggested_action="Consider if high cardinality is appropriate or if grouping is needed"
            ))
        
        # Low cardinality check (potential categorical)
        elif cardinality_ratio < self.validation_rules["low_cardinality_threshold"]:
            issues.append(ValidationIssue(
                issue_type="low_cardinality",
                severity=ValidationSeverity.INFO,
                column=column,
                description=f"Low cardinality: {unique_count} unique values",
                suggested_action="Consider converting to categorical data type"
            ))
        
        return issues
    
    def _validate_against_metadata(self, series: pd.Series, column: str, 
                                 metadata: Dict[str, Any]) -> List[ValidationIssue]:
        """
        Validate column against provided metadata
        
        Args:
            series: Series to validate
            column: Column name
            metadata: Metadata to validate against
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # This would be expanded based on the specific metadata schema
        # For now, implementing basic checks
        
        if 'expected_type' in metadata:
            expected_type = metadata['expected_type']
            actual_type = str(series.dtype)
            
            if expected_type != actual_type:
                issues.append(ValidationIssue(
                    issue_type="type_mismatch",
                    severity=ValidationSeverity.WARNING,
                    column=column,
                    description=f"Type mismatch: expected {expected_type}, got {actual_type}",
                    suggested_action="Verify data type conversion or metadata accuracy"
                ))
        
        return issues
    
    def _validate_relationships(self, df: pd.DataFrame, report: Dict[str, Any]) -> None:
        """
        Validate relationships between columns
        
        Args:
            df: DataFrame to validate
            report: Validation report to update
        """
        issues = []
        
        # Check for potential ID columns that might have referential integrity issues
        potential_id_columns = [
            col for col in df.columns 
            if 'id' in col.lower() and df[col].dtype in ['int64', 'object']
        ]
        
        for col in potential_id_columns:
            # Check for missing references (if this looks like a foreign key)
            if df[col].isnull().any():
                null_count = df[col].isnull().sum()
                issues.append(ValidationIssue(
                    issue_type="missing_references",
                    severity=ValidationSeverity.WARNING,
                    column=col,
                    description=f"Potential ID column has {null_count} missing values",
                    suggested_action="Investigate missing references in ID column"
                ))
        
        # Add cross-column validation issues
        report["issues"].extend([issue.__dict__ for issue in issues])
    
    def _calculate_column_statistics(self, series: pd.Series) -> Dict[str, Any]:
        """
        Calculate comprehensive statistics for a column
        
        Args:
            series: Series to analyze
            
        Returns:
            Dictionary of statistics
        """
        stats = {
            "count": len(series),
            "non_null_count": series.count(),
            "null_count": series.isnull().sum(),
            "null_percentage": (series.isnull().sum() / len(series)) * 100,
            "unique_count": series.nunique(),
            "unique_percentage": (series.nunique() / len(series)) * 100
        }
        
        # Add type-specific statistics
        if pd.api.types.is_numeric_dtype(series):
            clean_series = series.dropna()
            if len(clean_series) > 0:
                stats.update({
                    "mean": float(clean_series.mean()),
                    "median": float(clean_series.median()),
                    "std": float(clean_series.std()),
                    "min": float(clean_series.min()),
                    "max": float(clean_series.max()),
                    "q25": float(clean_series.quantile(0.25)),
                    "q75": float(clean_series.quantile(0.75))
                })
        
        return stats
    
    def _calculate_quality_score(self, report: Dict[str, Any]) -> float:
        """
        Calculate overall data quality score
        
        Args:
            report: Validation report
            
        Returns:
            Quality score between 0 and 1
        """
        total_issues = len(report["issues"])
        
        # Weight issues by severity
        severity_weights = {
            ValidationSeverity.INFO.value: 0.1,
            ValidationSeverity.WARNING.value: 0.3,
            ValidationSeverity.ERROR.value: 0.7,
            ValidationSeverity.CRITICAL.value: 1.0
        }
        
        weighted_issues = sum(
            severity_weights.get(issue["severity"], 0.5) 
            for issue in report["issues"]
        )
        
        # Calculate score (higher is better)
        max_possible_score = 100
        penalty = min(weighted_issues * 5, max_possible_score)  # Cap penalty
        score = max(0, (max_possible_score - penalty) / max_possible_score)
        
        return round(score, 3)
    
    def _generate_summary(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate validation summary
        
        Args:
            report: Validation report
            
        Returns:
            Summary statistics
        """
        issues_by_severity = {}
        issues_by_type = {}
        
        for issue in report["issues"]:
            severity = issue["severity"]
            issue_type = issue["issue_type"]
            
            issues_by_severity[severity] = issues_by_severity.get(severity, 0) + 1
            issues_by_type[issue_type] = issues_by_type.get(issue_type, 0) + 1
        
        return {
            "total_issues": len(report["issues"]),
            "issues_by_severity": issues_by_severity,
            "issues_by_type": issues_by_type,
            "columns_with_issues": len([
                col for col, col_report in report["column_reports"].items()
                if col_report["issues"]
            ]),
            "quality_score": report.get("quality_score", 0)
        }
    
    def _generate_recommendations(self, report: Dict[str, Any], 
                                df: pd.DataFrame) -> List[str]:
        """
        Generate actionable recommendations based on validation results
        
        Args:
            report: Validation report
            df: Original DataFrame
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Analyze issues and generate specific recommendations
        severity_counts = report["summary"]["issues_by_severity"]
        
        if severity_counts.get("critical", 0) > 0:
            recommendations.append(
                "Critical issues detected. Address these before proceeding with analysis."
            )
        
        if severity_counts.get("error", 0) > 0:
            recommendations.append(
                "Data errors found. Consider data cleaning and validation processes."
            )
        
        # Missing data recommendations
        high_missing_columns = [
            col for col, col_report in report["column_reports"].items()
            if any(issue["issue_type"] == "high_missing_data" for issue in col_report["issues"])
        ]
        
        if high_missing_columns:
            recommendations.append(
                f"Consider imputation strategies for columns with high missing data: {high_missing_columns}"
            )
        
        # Data type recommendations
        if report["summary"]["quality_score"] < 0.8:
            recommendations.append(
                "Overall data quality is below recommended threshold. "
                "Implement comprehensive data cleaning pipeline."
            )
        
        return recommendations