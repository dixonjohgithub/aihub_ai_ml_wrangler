"""
File: missing_data_analysis.py

Overview:
Advanced missing data pattern analysis with MCAR/MAR/MNAR detection
and statistical testing for missing data mechanisms.

Purpose:
Analyzes missing data patterns to understand the underlying mechanisms
and recommend appropriate imputation strategies.

Dependencies:
- pandas for data analysis
- numpy for numerical operations
- scipy for statistical tests
- typing for type hints

Last Modified: 2025-08-15
Author: Claude
"""

import asyncio
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import chi2_contingency
import warnings
warnings.filterwarnings('ignore')

class MissingDataAnalyzer:
    """Advanced missing data pattern analysis with mechanism detection."""
    
    def __init__(self):
        self.missing_mechanisms = {
            'MCAR': 'Missing Completely at Random',
            'MAR': 'Missing at Random',
            'MNAR': 'Missing Not at Random'
        }
        
    async def analyze_missing_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive missing data pattern analysis."""
        try:
            results = {
                'timestamp': pd.Timestamp.now().isoformat(),
                'total_observations': len(df),
                'total_variables': len(df.columns),
                'missing_overview': await self.get_missing_overview(df),
                'missing_patterns': await self.identify_missing_patterns(df),
                'mechanism_analysis': await self.analyze_missing_mechanisms(df),
                'correlation_analysis': await self.missing_correlation_analysis(df),
                'recommendations': []
            }
            
            # Generate recommendations based on analysis
            results['recommendations'] = await self.generate_missing_data_recommendations(results)
            
            return {
                'success': True,
                'missing_analysis': results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'missing_analysis': None
            }
    
    async def get_missing_overview(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get overall missing data statistics."""
        missing_counts = df.isnull().sum()
        missing_percentages = (missing_counts / len(df)) * 100
        
        # Complete case analysis
        complete_cases = df.dropna()
        complete_case_percentage = (len(complete_cases) / len(df)) * 100
        
        # Missing data by column
        columns_with_missing = missing_counts[missing_counts > 0]
        
        return {
            'total_missing_values': int(missing_counts.sum()),
            'missing_percentage': round((missing_counts.sum() / (len(df) * len(df.columns))) * 100, 2),
            'complete_cases': len(complete_cases),
            'complete_case_percentage': round(complete_case_percentage, 2),
            'columns_with_missing': len(columns_with_missing),
            'columns_missing_counts': missing_counts.to_dict(),
            'columns_missing_percentages': missing_percentages.round(2).to_dict(),
            'severity_classification': await self.classify_missing_severity(missing_percentages)
        }
    
    async def classify_missing_severity(self, missing_percentages: pd.Series) -> Dict[str, List[str]]:
        """Classify missing data severity by column."""
        classification = {
            'minimal': [],      # < 5%
            'moderate': [],     # 5-15%
            'substantial': [],  # 15-50%
            'severe': []        # > 50%
        }
        
        for col, percentage in missing_percentages.items():
            if percentage < 5:
                classification['minimal'].append(col)
            elif percentage < 15:
                classification['moderate'].append(col)
            elif percentage < 50:
                classification['substantial'].append(col)
            else:
                classification['severe'].append(col)
        
        return classification
    
    async def identify_missing_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify and analyze missing data patterns."""
        # Create missing indicator matrix
        missing_matrix = df.isnull().astype(int)
        
        # Find unique missing patterns
        pattern_counts = missing_matrix.value_counts()
        total_patterns = len(pattern_counts)
        
        # Analyze pattern distribution
        monotone_pattern = await self.check_monotone_pattern(missing_matrix)
        arbitrary_pattern = total_patterns > 10  # Arbitrary threshold
        
        # Most common patterns
        top_patterns = pattern_counts.head(10)
        
        # Pattern analysis
        pattern_analysis = {
            'total_unique_patterns': total_patterns,
            'most_common_patterns': [],
            'monotone_pattern': monotone_pattern,
            'arbitrary_pattern': arbitrary_pattern,
            'pattern_coverage': {}
        }
        
        # Analyze top patterns
        for pattern, count in top_patterns.items():
            pattern_dict = dict(zip(df.columns, pattern))
            missing_cols = [col for col, is_missing in pattern_dict.items() if is_missing == 1]
            
            pattern_analysis['most_common_patterns'].append({
                'pattern_id': len(pattern_analysis['most_common_patterns']) + 1,
                'count': int(count),
                'percentage': round((count / len(df)) * 100, 2),
                'missing_columns': missing_cols,
                'complete_columns': [col for col in df.columns if col not in missing_cols]
            })
        
        # Coverage analysis
        cumulative_coverage = 0
        for i, (_, count) in enumerate(top_patterns.items()):
            cumulative_coverage += count
            pattern_analysis['pattern_coverage'][f'top_{i+1}_patterns'] = round((cumulative_coverage / len(df)) * 100, 2)
        
        return pattern_analysis
    
    async def check_monotone_pattern(self, missing_matrix: pd.DataFrame) -> bool:
        """Check if missing data follows a monotone pattern."""
        try:
            # Sort by missing count per row
            sorted_matrix = missing_matrix.loc[missing_matrix.sum(axis=1).sort_values().index]
            
            # Check if pattern is monotone
            for i in range(len(sorted_matrix.columns)):
                col = sorted_matrix.columns[i]
                # For monotone pattern, once a value is missing in a column,
                # all subsequent rows should also be missing in that column
                missing_starts = sorted_matrix[col].idxmax() if sorted_matrix[col].sum() > 0 else None
                if missing_starts is not None:
                    remaining_values = sorted_matrix.loc[missing_starts:, col]
                    if not remaining_values.all():
                        return False
            
            return True
            
        except Exception:
            return False
    
    async def analyze_missing_mechanisms(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze missing data mechanisms (MCAR, MAR, MNAR)."""
        mechanism_results = {
            'mcar_test': await self.test_mcar(df),
            'mar_analysis': await self.analyze_mar(df),
            'mnar_indicators': await self.identify_mnar_indicators(df),
            'overall_mechanism': None,
            'confidence': 0.0
        }
        
        # Determine overall likely mechanism
        mechanism_results['overall_mechanism'] = await self.determine_primary_mechanism(mechanism_results)
        
        return mechanism_results
    
    async def test_mcar(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Test for MCAR using Little's MCAR test approximation."""
        try:
            missing_matrix = df.isnull()
            
            # Simplified MCAR test - compare missing patterns to expected random patterns
            # This is a simplified version of Little's MCAR test
            
            observed_patterns = missing_matrix.value_counts()
            total_observations = len(df)
            
            # Calculate expected frequencies under MCAR assumption
            missing_props = missing_matrix.mean()
            
            # Chi-square test for independence of missing patterns
            if len(observed_patterns) > 1:
                # Create contingency table for top patterns
                top_patterns = observed_patterns.head(min(10, len(observed_patterns)))
                
                # Simplified test statistic
                expected_equal = total_observations / len(top_patterns)
                chi_square = sum((obs - expected_equal)**2 / expected_equal for obs in top_patterns.values)
                degrees_freedom = len(top_patterns) - 1
                
                p_value = 1 - stats.chi2.cdf(chi_square, degrees_freedom) if degrees_freedom > 0 else 1.0
                
                return {
                    'test_statistic': round(chi_square, 4),
                    'p_value': round(p_value, 4),
                    'degrees_freedom': degrees_freedom,
                    'mcar_likely': p_value > 0.05,
                    'interpretation': 'MCAR likely' if p_value > 0.05 else 'MCAR unlikely'
                }
            else:
                return {
                    'test_statistic': 0.0,
                    'p_value': 1.0,
                    'degrees_freedom': 0,
                    'mcar_likely': True,
                    'interpretation': 'Insufficient patterns for testing'
                }
                
        except Exception as e:
            return {
                'test_statistic': None,
                'p_value': None,
                'degrees_freedom': None,
                'mcar_likely': None,
                'interpretation': f'Test failed: {str(e)}'
            }
    
    async def analyze_mar(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze potential MAR patterns."""
        mar_evidence = []
        
        # Check for correlations between missingness and observed values
        missing_matrix = df.isnull().astype(int)
        
        for col_with_missing in missing_matrix.columns[missing_matrix.sum() > 0]:
            missing_indicator = missing_matrix[col_with_missing]
            
            # Check correlation with other observed variables
            for other_col in df.columns:
                if other_col != col_with_missing and df[other_col].dtype in ['int64', 'float64']:
                    try:
                        # Calculate correlation between missingness and other variable
                        correlation = missing_indicator.corr(df[other_col])
                        
                        if abs(correlation) > 0.3:  # Significant correlation
                            mar_evidence.append({
                                'missing_variable': col_with_missing,
                                'related_variable': other_col,
                                'correlation': round(correlation, 4),
                                'strength': 'strong' if abs(correlation) > 0.5 else 'moderate'
                            })
                    except Exception:
                        continue
        
        return {
            'mar_relationships': mar_evidence,
            'mar_likely': len(mar_evidence) > 0,
            'strong_mar_evidence': len([e for e in mar_evidence if e['strength'] == 'strong'])
        }
    
    async def identify_mnar_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify potential MNAR indicators."""
        mnar_indicators = []
        
        # Look for patterns that suggest MNAR
        missing_matrix = df.isnull()
        
        for col in df.columns:
            col_missing = missing_matrix[col].sum()
            
            if col_missing > 0:
                # Check for systematic patterns that might indicate MNAR
                indicators = []
                
                # High missing rate might indicate sensitive/optional questions
                missing_rate = col_missing / len(df)
                if missing_rate > 0.3:
                    indicators.append('high_missing_rate')
                
                # Check column name for MNAR indicators
                col_lower = col.lower()
                sensitive_keywords = ['income', 'salary', 'age', 'weight', 'personal', 'private']
                if any(keyword in col_lower for keyword in sensitive_keywords):
                    indicators.append('sensitive_variable')
                
                # Check for extreme values before missingness (truncation)
                if df[col].dtype in ['int64', 'float64']:
                    non_missing_values = df[col].dropna()
                    if len(non_missing_values) > 0:
                        # Check if values cluster at boundaries
                        q99 = non_missing_values.quantile(0.99)
                        q01 = non_missing_values.quantile(0.01)
                        
                        boundary_clustering = (
                            (non_missing_values >= q99).sum() / len(non_missing_values) > 0.05 or
                            (non_missing_values <= q01).sum() / len(non_missing_values) > 0.05
                        )
                        
                        if boundary_clustering:
                            indicators.append('boundary_clustering')
                
                if indicators:
                    mnar_indicators.append({
                        'variable': col,
                        'indicators': indicators,
                        'missing_rate': round(missing_rate, 4),
                        'mnar_likelihood': 'high' if len(indicators) > 1 else 'moderate'
                    })
        
        return {
            'mnar_variables': mnar_indicators,
            'mnar_likely': len(mnar_indicators) > 0,
            'high_mnar_risk': len([v for v in mnar_indicators if v['mnar_likelihood'] == 'high'])
        }
    
    async def determine_primary_mechanism(self, mechanism_results: Dict[str, Any]) -> str:
        """Determine the most likely missing data mechanism."""
        # Simple scoring system
        mcar_score = 1.0 if mechanism_results['mcar_test']['mcar_likely'] else 0.0
        mar_score = 0.8 if mechanism_results['mar_analysis']['mar_likely'] else 0.0
        mnar_score = 0.9 if mechanism_results['mnar_indicators']['mnar_likely'] else 0.0
        
        scores = {'MCAR': mcar_score, 'MAR': mar_score, 'MNAR': mnar_score}
        
        if max(scores.values()) == 0:
            return 'Unknown'
        
        return max(scores, key=scores.get)
    
    async def missing_correlation_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze correlations between missing patterns."""
        missing_matrix = df.isnull().astype(int)
        
        # Calculate correlation matrix of missing indicators
        missing_correlations = missing_matrix.corr()
        
        # Find strong correlations (> 0.5)
        strong_correlations = []
        for i in range(len(missing_correlations.columns)):
            for j in range(i+1, len(missing_correlations.columns)):
                corr_value = missing_correlations.iloc[i, j]
                if abs(corr_value) > 0.5:
                    strong_correlations.append({
                        'variable1': missing_correlations.columns[i],
                        'variable2': missing_correlations.columns[j],
                        'correlation': round(corr_value, 4),
                        'strength': 'very_strong' if abs(corr_value) > 0.8 else 'strong'
                    })
        
        return {
            'correlation_matrix': missing_correlations.round(4).to_dict(),
            'strong_correlations': strong_correlations,
            'correlated_missing_patterns': len(strong_correlations) > 0
        }
    
    async def generate_missing_data_recommendations(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on missing data analysis."""
        recommendations = []
        
        overview = analysis_results['missing_overview']
        mechanism = analysis_results['mechanism_analysis']['overall_mechanism']
        
        # Recommendations based on missing percentage
        if overview['missing_percentage'] < 5:
            recommendations.append({
                'category': 'low_missing',
                'priority': 'low',
                'recommendation': 'Use listwise deletion or simple imputation methods',
                'rationale': 'Missing data percentage is low (<5%), advanced methods may not be necessary'
            })
        elif overview['missing_percentage'] < 20:
            recommendations.append({
                'category': 'moderate_missing',
                'priority': 'medium',
                'recommendation': 'Consider multiple imputation or advanced single imputation',
                'rationale': 'Moderate missing data (5-20%) requires careful imputation strategy'
            })
        else:
            recommendations.append({
                'category': 'high_missing',
                'priority': 'high',
                'recommendation': 'Use multiple imputation and sensitivity analysis',
                'rationale': 'High missing data (>20%) requires sophisticated handling'
            })
        
        # Recommendations based on mechanism
        if mechanism == 'MCAR':
            recommendations.append({
                'category': 'mcar_handling',
                'priority': 'medium',
                'recommendation': 'Any imputation method is appropriate; simple methods may suffice',
                'rationale': 'Data is Missing Completely at Random'
            })
        elif mechanism == 'MAR':
            recommendations.append({
                'category': 'mar_handling',
                'priority': 'high',
                'recommendation': 'Use multiple imputation incorporating related variables',
                'rationale': 'Data is Missing at Random - use observed data to predict missing values'
            })
        elif mechanism == 'MNAR':
            recommendations.append({
                'category': 'mnar_handling',
                'priority': 'high',
                'recommendation': 'Consider domain expertise and sensitivity analysis',
                'rationale': 'Data is Missing Not at Random - imputation may introduce bias'
            })
        
        # Recommendations based on patterns
        patterns = analysis_results['missing_patterns']
        if patterns['monotone_pattern']:
            recommendations.append({
                'category': 'monotone_pattern',
                'priority': 'medium',
                'recommendation': 'Use sequential imputation methods',
                'rationale': 'Monotone missing pattern allows for efficient sequential imputation'
            })
        
        return recommendations