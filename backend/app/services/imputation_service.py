"""
File: imputation_service.py

Overview:
Imputation service using research_pipeline for consistency.

Purpose:
Provides imputation methods through research_pipeline integration.

Dependencies:
- research_pipeline: Core imputation functionality
- pandas: Data manipulation
- numpy: Numerical operations

Last Modified: 2025-08-15
Author: Claude
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from datetime import datetime
import json

# Import research_pipeline
try:
    from app.core.research_pipeline_integration import FeatureImputer, EDA
except ImportError:
    import sys
    sys.path.insert(0, '/Users/johndixon/AI_Hub/research_pipeline')
    from research_pipeline.feature_imputer import FeatureImputer
    from research_pipeline.eda import EDA

logger = logging.getLogger(__name__)


class ImputationStrategy(Enum):
    """Available imputation strategies"""
    MEAN = "mean"
    MEDIAN = "median"
    MODE = "mode"
    FORWARD_FILL = "forward_fill"
    BACKWARD_FILL = "backward_fill"
    INTERPOLATION = "interpolation"
    KNN = "knn"
    RANDOM_FOREST = "random_forest"
    MICE = "mice"  # Multivariate Imputation by Chained Equations
    CONSTANT = "constant"
    DROP = "drop"


@dataclass
class ImputationConfig:
    """Configuration for imputation"""
    strategy: ImputationStrategy
    columns: List[str]
    parameters: Dict[str, Any]
    validate: bool = True
    preview_rows: int = 100


@dataclass
class ImputationResult:
    """Result of imputation operation"""
    strategy: str
    columns_imputed: List[str]
    values_imputed: int
    quality_metrics: Dict[str, float]
    preview_data: Optional[pd.DataFrame]
    execution_time: float
    warnings: List[str]


class ImputationService:
    """
    Main service for data imputation with multiple strategies
    """
    
    def __init__(self):
        """Initialize imputation service"""
        self.imputation_history: List[ImputationResult] = []
        self.supported_strategies = list(ImputationStrategy)
    
    def _classify_columns(self, df: pd.DataFrame) -> Tuple[List[str], List[str], List[str]]:
        """
        Classify columns into numeric, binary, and categorical.
        
        Returns:
            Tuple of (numeric_columns, binary_columns, categorical_columns)
        """
        numeric_columns = []
        binary_columns = []
        categorical_columns = []
        
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                unique_vals = df[col].dropna().unique()
                if len(unique_vals) <= 2 and set(unique_vals).issubset({0, 1}):
                    binary_columns.append(col)
                else:
                    numeric_columns.append(col)
            else:
                categorical_columns.append(col)
        
        return numeric_columns, binary_columns, categorical_columns
    
    def impute_dataset(
        self,
        df: pd.DataFrame,
        config: ImputationConfig
    ) -> Tuple[pd.DataFrame, ImputationResult]:
        """
        Perform imputation on dataset
        
        Args:
            df: DataFrame with missing values
            config: Imputation configuration
            
        Returns:
            Tuple of (imputed DataFrame, imputation result)
        """
        start_time = datetime.now()
        warnings = []
        
        try:
            # Validate configuration
            if config.validate:
                validation_warnings = self._validate_config(df, config)
                warnings.extend(validation_warnings)
            
            # Map our strategies to research_pipeline methods
            if config.strategy in [ImputationStrategy.MEAN, ImputationStrategy.MEDIAN, 
                                  ImputationStrategy.MODE]:
                # Use research_pipeline's basic imputation
                imputed_df = self._impute_using_research_pipeline(
                    df, config.columns, 'basic', config.strategy
                )
            elif config.strategy == ImputationStrategy.KNN:
                # Use research_pipeline's KNN imputation
                imputed_df = self._impute_using_research_pipeline(
                    df, config.columns, 'knn', config.strategy, config.parameters
                )
            elif config.strategy in [ImputationStrategy.RANDOM_FOREST, ImputationStrategy.MICE]:
                # Map to research_pipeline's advanced methods
                method = 'missforest' if config.strategy == ImputationStrategy.RANDOM_FOREST else 'mice'
                imputed_df = self._impute_using_research_pipeline(
                    df, config.columns, method, config.strategy, config.parameters
                )
            elif config.strategy == ImputationStrategy.FORWARD_FILL:
                imputed_df = self._impute_forward_fill(df, config.columns)
            elif config.strategy == ImputationStrategy.BACKWARD_FILL:
                imputed_df = self._impute_backward_fill(df, config.columns)
            elif config.strategy == ImputationStrategy.INTERPOLATION:
                imputed_df = self._impute_interpolation(df, config.columns, config.parameters)
            elif config.strategy == ImputationStrategy.CONSTANT:
                imputed_df = self._impute_constant(df, config.columns, config.parameters)
            elif config.strategy == ImputationStrategy.DROP:
                imputed_df = self._drop_missing(df, config.columns)
            else:
                raise ValueError(f"Unsupported imputation strategy: {config.strategy}")
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(df, imputed_df, config.columns)
            
            # Count imputed values
            values_imputed = self._count_imputed_values(df, imputed_df, config.columns)
            
            # Create preview if requested
            preview_data = None
            if config.preview_rows > 0:
                preview_data = imputed_df.head(config.preview_rows)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Create result
            result = ImputationResult(
                strategy=config.strategy.value,
                columns_imputed=config.columns,
                values_imputed=values_imputed,
                quality_metrics=quality_metrics,
                preview_data=preview_data,
                execution_time=execution_time,
                warnings=warnings
            )
            
            # Store in history
            self.imputation_history.append(result)
            
            return imputed_df, result
            
        except Exception as e:
            logger.error(f"Imputation failed: {e}")
            raise
    
    def _validate_config(self, df: pd.DataFrame, config: ImputationConfig) -> List[str]:
        """Validate imputation configuration"""
        warnings = []
        
        # Check if columns exist
        missing_cols = set(config.columns) - set(df.columns)
        if missing_cols:
            warnings.append(f"Columns not found in dataset: {missing_cols}")
        
        # Check data types for numeric strategies
        numeric_strategies = [
            ImputationStrategy.MEAN,
            ImputationStrategy.MEDIAN,
            ImputationStrategy.INTERPOLATION,
            ImputationStrategy.KNN,
            ImputationStrategy.RANDOM_FOREST,
            ImputationStrategy.MICE
        ]
        
        if config.strategy in numeric_strategies:
            non_numeric = []
            for col in config.columns:
                if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
                    non_numeric.append(col)
            if non_numeric:
                warnings.append(f"Non-numeric columns for numeric strategy: {non_numeric}")
        
        return warnings
    
    def _impute_using_research_pipeline(
        self, 
        df: pd.DataFrame, 
        columns: List[str], 
        method: str,
        strategy: ImputationStrategy,
        parameters: Optional[Dict] = None
    ) -> pd.DataFrame:
        """
        Use research_pipeline's FeatureImputer for imputation.
        Uses the unified impute_data method from research_pipeline.
        """
        # Classify columns
        numeric_cols, binary_cols, categorical_cols = self._classify_columns(df)
        
        # Filter columns to impute based on config
        if columns:
            numeric_cols = [c for c in numeric_cols if c in columns]
            binary_cols = [c for c in binary_cols if c in columns]
            categorical_cols = [c for c in categorical_cols if c in columns]
        
        # Initialize FeatureImputer
        imputer = FeatureImputer(
            data=df,
            numeric_columns=numeric_cols,
            binary_columns=binary_cols,
            categorical_columns=categorical_cols
        )
        
        # Map strategy to research_pipeline parameters
        numeric_strategy = 'mean'
        if strategy == ImputationStrategy.MEDIAN:
            numeric_strategy = 'median'
        elif strategy == ImputationStrategy.MODE:
            numeric_strategy = 'mode'
        
        # Apply imputation using the unified impute_data method
        try:
            if method == 'basic':
                # Use basic imputation strategy
                imputed_df = imputer.impute_data(
                    imputation_strategy='basic',
                    numeric_strategy=numeric_strategy,
                    is_training=True,
                    revert_label_encoding=True
                )
            elif method == 'knn':
                # Use KNN imputation
                n_neighbors = parameters.get('n_neighbors', 5) if parameters else 5
                imputed_df = imputer.impute_data(
                    imputation_strategy='knn',
                    n_neighbors=n_neighbors,
                    is_training=True,
                    revert_label_encoding=True
                )
            elif method == 'mice':
                # Use MICE imputation
                max_iter = parameters.get('max_iter', 10) if parameters else 10
                imputed_df = imputer.impute_data(
                    imputation_strategy='mice',
                    mice_iterations=max_iter,
                    cat_encoding='label',
                    is_training=True,
                    revert_label_encoding=True
                )
            elif method == 'missforest':
                # Use MissForest imputation
                max_iter = parameters.get('max_iter', 10) if parameters else 10
                imputed_df = imputer.impute_data(
                    imputation_strategy='missforest',
                    mf_max_iter=max_iter,
                    cat_encoding='label',
                    is_training=True,
                    revert_label_encoding=True
                )
            else:
                raise ValueError(f"Unknown research_pipeline method: {method}")
                
            return imputed_df
            
        except Exception as e:
            logger.warning(f"Research pipeline imputation failed: {e}. Falling back to simple imputation.")
            # Fallback to simple imputation
            df_copy = df.copy()
            for col in columns:
                if col in df_copy.columns:
                    if strategy == ImputationStrategy.MEAN:
                        df_copy[col].fillna(df_copy[col].mean(), inplace=True)
                    elif strategy == ImputationStrategy.MEDIAN:
                        df_copy[col].fillna(df_copy[col].median(), inplace=True)
                    elif strategy == ImputationStrategy.MODE:
                        mode_val = df_copy[col].mode()
                        if len(mode_val) > 0:
                            df_copy[col].fillna(mode_val[0], inplace=True)
            return df_copy
    
    def _impute_forward_fill(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Forward fill imputation"""
        df_copy = df.copy()
        for col in columns:
            if col in df_copy.columns:
                df_copy[col].fillna(method='ffill', inplace=True)
        return df_copy
    
    def _impute_backward_fill(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Backward fill imputation"""
        df_copy = df.copy()
        for col in columns:
            if col in df_copy.columns:
                df_copy[col].fillna(method='bfill', inplace=True)
        return df_copy
    
    def _impute_interpolation(self, df: pd.DataFrame, columns: List[str], 
                             parameters: Dict[str, Any]) -> pd.DataFrame:
        """Interpolation imputation"""
        df_copy = df.copy()
        method = parameters.get('method', 'linear')
        
        for col in columns:
            if col in df_copy.columns:
                df_copy[col] = df_copy[col].interpolate(method=method)
        return df_copy
    
    # These methods are now handled by _impute_using_research_pipeline
    # Keep them as fallbacks for compatibility
    
    def _impute_constant(self, df: pd.DataFrame, columns: List[str],
                        parameters: Dict[str, Any]) -> pd.DataFrame:
        """Constant value imputation"""
        df_copy = df.copy()
        fill_value = parameters.get('value', 0)
        
        for col in columns:
            if col in df_copy.columns:
                df_copy[col].fillna(fill_value, inplace=True)
        
        return df_copy
    
    def _drop_missing(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Drop rows with missing values"""
        df_copy = df.copy()
        
        if columns:
            return df_copy.dropna(subset=columns)
        else:
            return df_copy.dropna()
    
    def _count_imputed_values(self, original_df: pd.DataFrame, 
                            imputed_df: pd.DataFrame,
                            columns: List[str]) -> int:
        """Count number of values imputed"""
        count = 0
        for col in columns:
            if col in original_df.columns:
                original_missing = original_df[col].isnull().sum()
                imputed_missing = imputed_df[col].isnull().sum()
                count += (original_missing - imputed_missing)
        return count
    
    def _calculate_quality_metrics(self, original_df: pd.DataFrame,
                                  imputed_df: pd.DataFrame,
                                  columns: List[str]) -> Dict[str, float]:
        """Calculate imputation quality metrics"""
        metrics = {}
        
        # Completeness score
        original_missing = original_df[columns].isnull().sum().sum()
        imputed_missing = imputed_df[columns].isnull().sum().sum()
        
        if original_missing > 0:
            completeness = 1 - (imputed_missing / original_missing)
        else:
            completeness = 1.0
        
        metrics['completeness'] = completeness
        
        # Distribution preservation (for numeric columns)
        numeric_cols = [col for col in columns 
                        if col in original_df.columns and 
                        pd.api.types.is_numeric_dtype(original_df[col])]
        
        if numeric_cols:
            # Calculate KL divergence for distribution similarity
            kl_scores = []
            for col in numeric_cols:
                original_values = original_df[col].dropna()
                imputed_values = imputed_df[col].dropna()
                
                if len(original_values) > 0 and len(imputed_values) > 0:
                    # Simple distribution comparison using mean and std
                    original_mean = original_values.mean()
                    original_std = original_values.std()
                    imputed_mean = imputed_values.mean()
                    imputed_std = imputed_values.std()
                    
                    # Calculate relative difference
                    mean_diff = abs(original_mean - imputed_mean) / (abs(original_mean) + 1e-10)
                    std_diff = abs(original_std - imputed_std) / (original_std + 1e-10)
                    
                    # Distribution preservation score (1 = perfect, 0 = poor)
                    preservation_score = 1 - min(1, (mean_diff + std_diff) / 2)
                    kl_scores.append(preservation_score)
            
            if kl_scores:
                metrics['distribution_preservation'] = np.mean(kl_scores)
        
        # Variance preservation
        if numeric_cols:
            variance_ratios = []
            for col in numeric_cols:
                original_var = original_df[col].var()
                imputed_var = imputed_df[col].var()
                if original_var > 0:
                    ratio = min(imputed_var / original_var, original_var / imputed_var)
                    variance_ratios.append(ratio)
            
            if variance_ratios:
                metrics['variance_preservation'] = np.mean(variance_ratios)
        
        return metrics
    
    def get_imputation_strategies(self, df: pd.DataFrame, 
                                column: str) -> List[Dict[str, Any]]:
        """Get recommended imputation strategies for a column"""
        strategies = []
        
        if column not in df.columns:
            return strategies
        
        dtype = df[column].dtype
        missing_count = df[column].isnull().sum()
        missing_percentage = (missing_count / len(df)) * 100
        
        # Numeric columns
        if pd.api.types.is_numeric_dtype(dtype):
            # Low missing percentage - simple strategies
            if missing_percentage < 5:
                strategies.append({
                    'strategy': ImputationStrategy.MEAN.value,
                    'recommended': True,
                    'reason': 'Low missing percentage, mean imputation is efficient'
                })
                strategies.append({
                    'strategy': ImputationStrategy.MEDIAN.value,
                    'recommended': True,
                    'reason': 'Robust to outliers'
                })
            
            # Moderate missing percentage
            elif missing_percentage < 20:
                strategies.append({
                    'strategy': ImputationStrategy.KNN.value,
                    'recommended': True,
                    'reason': 'Moderate missing data, KNN can capture local patterns'
                })
                strategies.append({
                    'strategy': ImputationStrategy.MICE.value,
                    'recommended': True,
                    'reason': 'Multivariate approach for complex relationships'
                })
            
            # High missing percentage
            else:
                strategies.append({
                    'strategy': ImputationStrategy.RANDOM_FOREST.value,
                    'recommended': True,
                    'reason': 'High missing data, ML-based approach recommended'
                })
                strategies.append({
                    'strategy': ImputationStrategy.DROP.value,
                    'recommended': False,
                    'reason': 'Consider dropping if too much data is missing'
                })
        
        # Categorical columns
        else:
            strategies.append({
                'strategy': ImputationStrategy.MODE.value,
                'recommended': True,
                'reason': 'Most frequent value for categorical data'
            })
            strategies.append({
                'strategy': ImputationStrategy.CONSTANT.value,
                'recommended': True,
                'reason': 'Use specific category like "Unknown"'
            })
            
            if missing_percentage > 30:
                strategies.append({
                    'strategy': ImputationStrategy.DROP.value,
                    'recommended': False,
                    'reason': 'High missing percentage in categorical column'
                })
        
        # Time series data
        if 'date' in column.lower() or 'time' in column.lower():
            strategies.append({
                'strategy': ImputationStrategy.FORWARD_FILL.value,
                'recommended': True,
                'reason': 'Time series data - forward fill maintains temporal patterns'
            })
            strategies.append({
                'strategy': ImputationStrategy.INTERPOLATION.value,
                'recommended': True,
                'reason': 'Smooth interpolation for time series'
            })
        
        return strategies
    
    def compare_strategies(self, df: pd.DataFrame,
                          columns: List[str],
                          strategies: List[ImputationStrategy]) -> pd.DataFrame:
        """Compare multiple imputation strategies"""
        results = []
        
        for strategy in strategies:
            config = ImputationConfig(
                strategy=strategy,
                columns=columns,
                parameters={},
                validate=True,
                preview_rows=0
            )
            
            try:
                _, result = self.impute_dataset(df, config)
                results.append({
                    'strategy': strategy.value,
                    'completeness': result.quality_metrics.get('completeness', 0),
                    'distribution_preservation': result.quality_metrics.get('distribution_preservation', 0),
                    'variance_preservation': result.quality_metrics.get('variance_preservation', 0),
                    'execution_time': result.execution_time,
                    'values_imputed': result.values_imputed
                })
            except Exception as e:
                logger.warning(f"Strategy {strategy.value} failed: {e}")
                results.append({
                    'strategy': strategy.value,
                    'completeness': 0,
                    'distribution_preservation': 0,
                    'variance_preservation': 0,
                    'execution_time': 0,
                    'values_imputed': 0
                })
        
        return pd.DataFrame(results)