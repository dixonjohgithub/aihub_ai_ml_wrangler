"""
File: correlation_service.py

Overview:
Comprehensive correlation analysis service with multiple correlation methods
and advanced analytics capabilities.

Purpose:
Provides correlation analysis, high correlation detection, and feature
relationship insights for data preprocessing.

Dependencies:
- pandas: Data manipulation
- numpy: Numerical operations
- scipy: Statistical functions
- networkx: Network analysis for correlation graphs

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
from scipy import stats
from scipy.cluster import hierarchy
import networkx as nx
import json

logger = logging.getLogger(__name__)


class CorrelationType(Enum):
    """Types of correlation methods"""
    PEARSON = "pearson"
    SPEARMAN = "spearman"
    KENDALL = "kendall"
    CRAMERS_V = "cramers_v"  # For categorical variables
    POINT_BISERIAL = "point_biserial"  # For binary vs continuous


@dataclass
class CorrelationConfig:
    """Configuration for correlation analysis"""
    method: CorrelationType
    threshold: float = 0.7
    min_periods: int = 10
    handle_missing: str = "pairwise"  # or "listwise"
    include_categorical: bool = False


@dataclass
class CorrelationResult:
    """Result of correlation analysis"""
    correlation_matrix: pd.DataFrame
    high_correlations: List[Tuple[str, str, float]]
    feature_importance: Dict[str, float]
    clustering: Optional[Dict[str, List[str]]]
    recommendations: List[str]
    metadata: Dict[str, Any]


class CorrelationAnalyzer:
    """
    Main class for correlation analysis and feature relationship detection
    """
    
    def __init__(self):
        """Initialize correlation analyzer"""
        self.analysis_history: List[CorrelationResult] = []
    
    def analyze_correlations(
        self,
        df: pd.DataFrame,
        config: CorrelationConfig,
        target_column: Optional[str] = None
    ) -> CorrelationResult:
        """
        Perform comprehensive correlation analysis
        
        Args:
            df: DataFrame to analyze
            config: Correlation configuration
            target_column: Optional target for supervised analysis
            
        Returns:
            Correlation analysis result
        """
        try:
            # Calculate correlation matrix
            if config.method == CorrelationType.PEARSON:
                corr_matrix = self._pearson_correlation(df, config)
            elif config.method == CorrelationType.SPEARMAN:
                corr_matrix = self._spearman_correlation(df, config)
            elif config.method == CorrelationType.KENDALL:
                corr_matrix = self._kendall_correlation(df, config)
            else:
                corr_matrix = self._pearson_correlation(df, config)
            
            # Find high correlations
            high_correlations = self._find_high_correlations(corr_matrix, config.threshold)
            
            # Calculate feature importance if target provided
            feature_importance = {}
            if target_column and target_column in df.columns:
                feature_importance = self._calculate_feature_importance(
                    df, target_column, corr_matrix
                )
            
            # Perform hierarchical clustering
            clustering = self._hierarchical_clustering(corr_matrix, config.threshold)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                high_correlations, feature_importance, clustering
            )
            
            # Create metadata
            metadata = {
                'n_features': len(corr_matrix.columns),
                'n_high_correlations': len(high_correlations),
                'method': config.method.value,
                'threshold': config.threshold,
                'timestamp': datetime.now().isoformat()
            }
            
            # Create result
            result = CorrelationResult(
                correlation_matrix=corr_matrix,
                high_correlations=high_correlations,
                feature_importance=feature_importance,
                clustering=clustering,
                recommendations=recommendations,
                metadata=metadata
            )
            
            # Store in history
            self.analysis_history.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Correlation analysis failed: {e}")
            raise
    
    def _pearson_correlation(self, df: pd.DataFrame, config: CorrelationConfig) -> pd.DataFrame:
        """Calculate Pearson correlation"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if config.handle_missing == "pairwise":
            return numeric_df.corr(method='pearson', min_periods=config.min_periods)
        else:
            return numeric_df.dropna().corr(method='pearson')
    
    def _spearman_correlation(self, df: pd.DataFrame, config: CorrelationConfig) -> pd.DataFrame:
        """Calculate Spearman correlation"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if config.handle_missing == "pairwise":
            return numeric_df.corr(method='spearman', min_periods=config.min_periods)
        else:
            return numeric_df.dropna().corr(method='spearman')
    
    def _kendall_correlation(self, df: pd.DataFrame, config: CorrelationConfig) -> pd.DataFrame:
        """Calculate Kendall correlation"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if config.handle_missing == "pairwise":
            return numeric_df.corr(method='kendall', min_periods=config.min_periods)
        else:
            return numeric_df.dropna().corr(method='kendall')
    
    def _find_high_correlations(
        self,
        corr_matrix: pd.DataFrame,
        threshold: float
    ) -> List[Tuple[str, str, float]]:
        """Find pairs of features with high correlation"""
        high_corr = []
        
        # Get upper triangle of correlation matrix
        upper_triangle = np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
        upper_corr = corr_matrix.where(upper_triangle)
        
        # Find high correlations
        for i in range(len(upper_corr.columns)):
            for j in range(i + 1, len(upper_corr.columns)):
                corr_value = upper_corr.iloc[i, j]
                if abs(corr_value) >= threshold:
                    high_corr.append((
                        upper_corr.columns[i],
                        upper_corr.columns[j],
                        float(corr_value)
                    ))
        
        # Sort by absolute correlation value
        high_corr.sort(key=lambda x: abs(x[2]), reverse=True)
        
        return high_corr
    
    def _calculate_feature_importance(
        self,
        df: pd.DataFrame,
        target_column: str,
        corr_matrix: pd.DataFrame
    ) -> Dict[str, float]:
        """Calculate feature importance based on correlation with target"""
        importance = {}
        
        if target_column in corr_matrix.columns:
            target_corr = corr_matrix[target_column].abs()
            
            for col in corr_matrix.columns:
                if col != target_column:
                    importance[col] = float(target_corr[col])
        
        # Sort by importance
        return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
    
    def _hierarchical_clustering(
        self,
        corr_matrix: pd.DataFrame,
        threshold: float
    ) -> Dict[str, List[str]]:
        """Perform hierarchical clustering on features"""
        try:
            # Convert correlation to distance
            distance_matrix = 1 - abs(corr_matrix)
            
            # Perform hierarchical clustering
            condensed_distance = hierarchy.distance.squareform(distance_matrix)
            linkage_matrix = hierarchy.linkage(condensed_distance, method='average')
            
            # Form clusters
            clusters = hierarchy.fcluster(linkage_matrix, 1 - threshold, criterion='distance')
            
            # Group features by cluster
            cluster_groups = {}
            for i, cluster_id in enumerate(clusters):
                cluster_key = f"cluster_{cluster_id}"
                if cluster_key not in cluster_groups:
                    cluster_groups[cluster_key] = []
                cluster_groups[cluster_key].append(corr_matrix.columns[i])
            
            # Filter out single-feature clusters
            cluster_groups = {k: v for k, v in cluster_groups.items() if len(v) > 1}
            
            return cluster_groups
            
        except Exception as e:
            logger.warning(f"Clustering failed: {e}")
            return {}
    
    def _generate_recommendations(
        self,
        high_correlations: List[Tuple[str, str, float]],
        feature_importance: Dict[str, float],
        clustering: Dict[str, List[str]]
    ) -> List[str]:
        """Generate recommendations based on correlation analysis"""
        recommendations = []
        
        # High correlation recommendations
        if high_correlations:
            recommendations.append(
                f"Found {len(high_correlations)} pairs of highly correlated features. "
                "Consider removing one feature from each pair to reduce multicollinearity."
            )
            
            # Suggest specific features to drop
            features_to_consider = set()
            for feat1, feat2, corr in high_correlations[:5]:  # Top 5
                # Suggest dropping the less important feature
                if feature_importance:
                    imp1 = feature_importance.get(feat1, 0)
                    imp2 = feature_importance.get(feat2, 0)
                    if imp1 < imp2:
                        features_to_consider.add(feat1)
                    else:
                        features_to_consider.add(feat2)
                else:
                    features_to_consider.add(feat2)
            
            if features_to_consider:
                recommendations.append(
                    f"Consider removing these features: {', '.join(list(features_to_consider)[:5])}"
                )
        
        # Clustering recommendations
        if clustering:
            recommendations.append(
                f"Features can be grouped into {len(clustering)} clusters based on correlation patterns. "
                "Consider selecting representative features from each cluster."
            )
        
        # Feature importance recommendations
        if feature_importance:
            low_importance = [k for k, v in feature_importance.items() if v < 0.1]
            if low_importance:
                recommendations.append(
                    f"Features with very low correlation to target (<0.1): {', '.join(low_importance[:5])}. "
                    "Consider removing these features."
                )
        
        return recommendations
    
    def create_correlation_network(
        self,
        corr_matrix: pd.DataFrame,
        threshold: float = 0.5
    ) -> nx.Graph:
        """Create network graph from correlation matrix"""
        G = nx.Graph()
        
        # Add nodes
        for col in corr_matrix.columns:
            G.add_node(col)
        
        # Add edges for correlations above threshold
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) >= threshold:
                    G.add_edge(
                        corr_matrix.columns[i],
                        corr_matrix.columns[j],
                        weight=float(corr_value)
                    )
        
        return G
    
    def detect_multicollinearity(
        self,
        df: pd.DataFrame,
        threshold: float = 0.9
    ) -> Dict[str, Any]:
        """Detect multicollinearity issues"""
        numeric_df = df.select_dtypes(include=[np.number])
        corr_matrix = numeric_df.corr()
        
        # Find highly correlated pairs
        high_corr_pairs = self._find_high_correlations(corr_matrix, threshold)
        
        # Calculate VIF (Variance Inflation Factor) for each feature
        from statsmodels.stats.outliers_influence import variance_inflation_factor
        
        vif_data = pd.DataFrame()
        vif_data["Feature"] = numeric_df.columns
        
        try:
            vif_data["VIF"] = [
                variance_inflation_factor(numeric_df.values, i)
                for i in range(numeric_df.shape[1])
            ]
            
            # Features with VIF > 10 indicate multicollinearity
            problematic_features = vif_data[vif_data["VIF"] > 10]["Feature"].tolist()
        except:
            vif_data = pd.DataFrame()
            problematic_features = []
        
        return {
            'high_correlation_pairs': high_corr_pairs,
            'vif_analysis': vif_data.to_dict('records') if not vif_data.empty else [],
            'problematic_features': problematic_features,
            'recommendation': self._get_multicollinearity_recommendation(
                high_corr_pairs, problematic_features
            )
        }
    
    def _get_multicollinearity_recommendation(
        self,
        high_corr_pairs: List[Tuple[str, str, float]],
        problematic_features: List[str]
    ) -> str:
        """Generate multicollinearity recommendation"""
        if not high_corr_pairs and not problematic_features:
            return "No significant multicollinearity detected."
        
        recommendation = "Multicollinearity detected. "
        
        if high_corr_pairs:
            recommendation += f"Found {len(high_corr_pairs)} pairs with correlation > 0.9. "
        
        if problematic_features:
            recommendation += f"Features with high VIF (>10): {', '.join(problematic_features[:5])}. "
        
        recommendation += "Consider removing redundant features or using dimensionality reduction."
        
        return recommendation
    
    def correlation_change_analysis(
        self,
        df_before: pd.DataFrame,
        df_after: pd.DataFrame,
        threshold: float = 0.1
    ) -> Dict[str, Any]:
        """Analyze changes in correlation structure"""
        # Calculate correlation matrices
        corr_before = df_before.select_dtypes(include=[np.number]).corr()
        corr_after = df_after.select_dtypes(include=[np.number]).corr()
        
        # Find common columns
        common_cols = list(set(corr_before.columns) & set(corr_after.columns))
        
        if not common_cols:
            return {'error': 'No common columns found'}
        
        # Calculate correlation difference
        corr_diff = corr_after[common_cols].loc[common_cols] - corr_before[common_cols].loc[common_cols]
        
        # Find significant changes
        significant_changes = []
        for i in range(len(common_cols)):
            for j in range(i + 1, len(common_cols)):
                diff = corr_diff.iloc[i, j]
                if abs(diff) >= threshold:
                    significant_changes.append({
                        'feature1': common_cols[i],
                        'feature2': common_cols[j],
                        'before': float(corr_before.loc[common_cols[i], common_cols[j]]),
                        'after': float(corr_after.loc[common_cols[i], common_cols[j]]),
                        'change': float(diff)
                    })
        
        # Sort by absolute change
        significant_changes.sort(key=lambda x: abs(x['change']), reverse=True)
        
        return {
            'significant_changes': significant_changes[:20],  # Top 20 changes
            'max_change': max(abs(corr_diff.values.flatten())) if len(corr_diff) > 0 else 0,
            'mean_change': abs(corr_diff.values.flatten()).mean() if len(corr_diff) > 0 else 0,
            'n_changes': len(significant_changes)
        }
    
    def export_correlation_matrix(
        self,
        corr_matrix: pd.DataFrame,
        format: str = 'csv',
        threshold: Optional[float] = None
    ) -> Union[str, bytes]:
        """Export correlation matrix in specified format"""
        if threshold is not None:
            # Filter by threshold
            mask = abs(corr_matrix) >= threshold
            filtered_matrix = corr_matrix.where(mask)
        else:
            filtered_matrix = corr_matrix
        
        if format == 'csv':
            return filtered_matrix.to_csv()
        elif format == 'json':
            return filtered_matrix.to_json(orient='split')
        elif format == 'html':
            return filtered_matrix.to_html()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_feature_relationships(
        self,
        df: pd.DataFrame,
        feature: str,
        top_n: int = 10
    ) -> Dict[str, Any]:
        """Get relationships for a specific feature"""
        if feature not in df.columns:
            return {'error': f'Feature {feature} not found'}
        
        # Calculate correlations
        numeric_df = df.select_dtypes(include=[np.number])
        
        if feature not in numeric_df.columns:
            return {'error': f'Feature {feature} is not numeric'}
        
        correlations = numeric_df.corr()[feature].abs().sort_values(ascending=False)
        
        # Get top correlated features (excluding self)
        top_correlations = correlations[correlations.index != feature].head(top_n)
        
        # Calculate mutual information if possible
        try:
            from sklearn.feature_selection import mutual_info_regression
            
            X = numeric_df.drop(columns=[feature])
            y = numeric_df[feature]
            
            # Remove rows with NaN
            mask = ~(X.isnull().any(axis=1) | y.isnull())
            X_clean = X[mask]
            y_clean = y[mask]
            
            if len(X_clean) > 0:
                mi_scores = mutual_info_regression(X_clean, y_clean)
                mutual_info = dict(zip(X.columns, mi_scores))
            else:
                mutual_info = {}
        except:
            mutual_info = {}
        
        return {
            'feature': feature,
            'top_correlations': top_correlations.to_dict(),
            'mutual_information': mutual_info,
            'statistics': {
                'mean': float(df[feature].mean()) if pd.api.types.is_numeric_dtype(df[feature]) else None,
                'std': float(df[feature].std()) if pd.api.types.is_numeric_dtype(df[feature]) else None,
                'missing': int(df[feature].isnull().sum()),
                'unique': int(df[feature].nunique())
            }
        }