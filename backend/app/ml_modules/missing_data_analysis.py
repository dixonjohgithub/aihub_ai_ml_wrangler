"""
File: missing_data_analysis.py

Overview:
Advanced missing data pattern analysis for identifying systematic patterns,
missing data mechanisms, and optimal imputation strategies

Purpose:
Analyzes missing data patterns to understand if data is MCAR (Missing Completely at Random),
MAR (Missing at Random), or MNAR (Missing Not at Random) and recommends appropriate strategies

Dependencies:
- pandas: Data manipulation and missing data analysis
- numpy: Numerical operations and statistical calculations
- scipy: Statistical tests and advanced analytics
- seaborn: Statistical data visualization
- matplotlib: Plotting and visualization

Last Modified: 2025-08-15
Author: Claude
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import chi2_contingency
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import logging
import itertools
from collections import defaultdict

logger = logging.getLogger(__name__)

class MissingDataMechanism(Enum):
    """Types of missing data mechanisms"""
    MCAR = "Missing Completely at Random"
    MAR = "Missing at Random" 
    MNAR = "Missing Not at Random"
    UNKNOWN = "Unknown"

class MissingDataPattern(Enum):
    """Common missing data patterns"""
    RANDOM = "random"
    SYSTEMATIC = "systematic"
    MONOTONIC = "monotonic"
    CLUSTERED = "clustered"
    STRUCTURAL = "structural"

@dataclass
class MissingDataInsight:
    """Insight about missing data pattern"""
    pattern_type: MissingDataPattern
    mechanism: MissingDataMechanism
    description: str
    affected_columns: List[str]
    severity: str
    confidence: float
    suggested_actions: List[str]

class MissingDataAnalyzer:
    """
    Comprehensive missing data pattern analysis and mechanism detection
    """
    
    def __init__(self, significance_level: float = 0.05):
        """
        Initialize missing data analyzer
        
        Args:
            significance_level: Statistical significance level for tests
        """
        self.significance_level = significance_level
    
    def analyze_missing_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive missing data pattern analysis
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Comprehensive missing data analysis report
        """
        logger.info(f"Starting missing data analysis for dataset with shape {df.shape}")
        
        analysis_report = {
            "overview": self._calculate_missing_overview(df),
            "column_analysis": self._analyze_column_missingness(df),
            "pattern_analysis": self._analyze_missing_patterns(df),
            "mechanism_analysis": self._analyze_missing_mechanisms(df),
            "correlation_analysis": self._analyze_missing_correlations(df),
            "insights": [],
            "recommendations": []
        }
        
        # Generate insights
        analysis_report["insights"] = self._generate_insights(df, analysis_report)
        
        # Generate recommendations
        analysis_report["recommendations"] = self._generate_recommendations(analysis_report)
        
        logger.info("Missing data analysis completed")
        return analysis_report
    
    def _calculate_missing_overview(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate overall missing data statistics
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Overview statistics
        """
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        missing_percentage = (missing_cells / total_cells) * 100
        
        columns_with_missing = (df.isnull().sum() > 0).sum()
        rows_with_missing = (df.isnull().sum(axis=1) > 0).sum()
        
        # Calculate completeness score
        completeness_score = ((total_cells - missing_cells) / total_cells) * 100
        
        return {
            "total_cells": total_cells,
            "missing_cells": missing_cells,
            "missing_percentage": round(missing_percentage, 2),
            "completeness_score": round(completeness_score, 2),
            "columns_with_missing": columns_with_missing,
            "rows_with_missing": rows_with_missing,
            "complete_rows": len(df) - rows_with_missing,
            "complete_columns": len(df.columns) - columns_with_missing
        }
    
    def _analyze_column_missingness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze missingness for each column
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Column-level missing data analysis
        """
        column_analysis = {}
        
        for column in df.columns:
            missing_count = df[column].isnull().sum()
            missing_percentage = (missing_count / len(df)) * 100
            
            # Calculate missing data run lengths (consecutive missing values)
            is_missing = df[column].isnull()
            run_lengths = []
            current_run = 0
            
            for missing in is_missing:
                if missing:
                    current_run += 1
                else:
                    if current_run > 0:
                        run_lengths.append(current_run)
                        current_run = 0
            
            if current_run > 0:  # Handle case where series ends with missing values
                run_lengths.append(current_run)
            
            # Analyze missing data distribution
            missing_positions = df.index[df[column].isnull()].tolist()
            
            column_analysis[column] = {
                "missing_count": missing_count,
                "missing_percentage": round(missing_percentage, 2),
                "missing_positions": missing_positions[:100],  # Limit for performance
                "run_lengths": run_lengths,
                "max_consecutive_missing": max(run_lengths) if run_lengths else 0,
                "missing_runs_count": len(run_lengths),
                "missingness_pattern": self._classify_column_missingness_pattern(
                    missing_positions, len(df)
                )
            }
        
        return column_analysis
    
    def _classify_column_missingness_pattern(self, missing_positions: List[int], 
                                           total_length: int) -> str:
        """
        Classify the missingness pattern for a single column
        
        Args:
            missing_positions: List of positions where data is missing
            total_length: Total length of the series
            
        Returns:
            Pattern classification
        """
        if not missing_positions:
            return "no_missing"
        
        # Check for systematic patterns
        if len(missing_positions) == total_length:
            return "completely_missing"
        
        # Check for regular intervals
        if len(missing_positions) > 1:
            intervals = [missing_positions[i+1] - missing_positions[i] 
                        for i in range(len(missing_positions)-1)]
            
            # Check if intervals are consistent (systematic pattern)
            if len(set(intervals)) == 1:
                return "systematic_interval"
            
            # Check for beginning or end missing (monotonic)
            if missing_positions == list(range(len(missing_positions))):
                return "missing_at_start"
            elif missing_positions == list(range(total_length - len(missing_positions), total_length)):
                return "missing_at_end"
        
        # Check clustering
        if len(missing_positions) > 2:
            gaps = [missing_positions[i+1] - missing_positions[i] 
                   for i in range(len(missing_positions)-1)]
            small_gaps = sum(1 for gap in gaps if gap <= 5)
            
            if small_gaps / len(gaps) > 0.7:
                return "clustered"
        
        return "random"
    
    def _analyze_missing_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze cross-column missing data patterns
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Pattern analysis results
        """
        # Create missing data indicator matrix
        missing_matrix = df.isnull()
        
        # Find unique missing patterns
        pattern_counts = missing_matrix.value_counts()
        
        # Analyze pattern frequency
        total_rows = len(df)
        pattern_analysis = {
            "unique_patterns": len(pattern_counts),
            "most_common_patterns": [],
            "pattern_diversity": self._calculate_pattern_diversity(pattern_counts, total_rows)
        }
        
        # Get top patterns
        for i, (pattern, count) in enumerate(pattern_counts.head(10).items()):
            pattern_dict = dict(zip(df.columns, pattern))
            missing_columns = [col for col, is_missing in pattern_dict.items() if is_missing]
            
            pattern_analysis["most_common_patterns"].append({
                "rank": i + 1,
                "count": count,
                "percentage": round((count / total_rows) * 100, 2),
                "missing_columns": missing_columns,
                "pattern": pattern_dict
            })
        
        # Analyze monotonic missingness
        pattern_analysis["monotonic_analysis"] = self._analyze_monotonic_patterns(df)
        
        return pattern_analysis
    
    def _calculate_pattern_diversity(self, pattern_counts: pd.Series, total_rows: int) -> Dict[str, float]:
        """
        Calculate diversity metrics for missing patterns
        
        Args:
            pattern_counts: Series with pattern frequencies
            total_rows: Total number of rows
            
        Returns:
            Diversity metrics
        """
        # Shannon entropy
        probabilities = pattern_counts / total_rows
        shannon_entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        
        # Normalized entropy (0 = all same pattern, 1 = all different patterns)
        max_entropy = np.log2(len(pattern_counts))
        normalized_entropy = shannon_entropy / max_entropy if max_entropy > 0 else 0
        
        return {
            "shannon_entropy": round(shannon_entropy, 3),
            "normalized_entropy": round(normalized_entropy, 3),
            "unique_pattern_ratio": round(len(pattern_counts) / total_rows, 3)
        }
    
    def _analyze_monotonic_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze monotonic missing patterns (where missingness follows an order)
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Monotonic pattern analysis
        """
        missing_counts = df.isnull().sum().sort_values(ascending=False)
        
        # Check if there's a monotonic pattern
        # (columns with more missing data are subsets of those with less)
        monotonic_pairs = []
        
        columns_by_missingness = missing_counts.index.tolist()
        
        for i, col1 in enumerate(columns_by_missingness[:-1]):
            for col2 in columns_by_missingness[i+1:]:
                # Check if col1's missing values are a superset of col2's
                col1_missing = df[col1].isnull()
                col2_missing = df[col2].isnull()
                
                # col2 missing should be a subset of col1 missing for monotonic pattern
                subset_check = (~col2_missing | col1_missing).all()
                
                if subset_check:
                    overlap_ratio = (col1_missing & col2_missing).sum() / col2_missing.sum()
                    monotonic_pairs.append({
                        "superset_column": col1,
                        "subset_column": col2,
                        "overlap_ratio": round(overlap_ratio, 3)
                    })
        
        return {
            "is_monotonic": len(monotonic_pairs) > 0,
            "monotonic_pairs": monotonic_pairs,
            "monotonic_strength": len(monotonic_pairs) / (len(df.columns) * (len(df.columns) - 1) / 2)
        }
    
    def _analyze_missing_mechanisms(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze missing data mechanisms using statistical tests
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Mechanism analysis results
        """
        mechanism_analysis = {
            "little_mcar_test": self._little_mcar_test(df),
            "dependency_tests": self._test_missing_dependencies(df),
            "randomness_tests": self._test_missing_randomness(df)
        }
        
        # Determine overall mechanism
        mechanism_analysis["overall_mechanism"] = self._determine_overall_mechanism(mechanism_analysis)
        
        return mechanism_analysis
    
    def _little_mcar_test(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform Little's MCAR test (simplified version)
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            MCAR test results
        """
        # This is a simplified implementation
        # Full Little's MCAR test requires more complex implementation
        
        missing_matrix = df.isnull()
        
        # Calculate pattern frequencies
        pattern_counts = missing_matrix.value_counts()
        
        # Simple chi-square test for randomness
        observed = pattern_counts.values
        expected = np.full_like(observed, np.mean(observed))
        
        try:
            chi2_stat, p_value = stats.chisquare(observed, expected)
            
            return {
                "test_name": "Simplified MCAR Test",
                "chi2_statistic": round(chi2_stat, 4),
                "p_value": round(p_value, 4),
                "is_mcar": p_value > self.significance_level,
                "interpretation": "MCAR" if p_value > self.significance_level else "Not MCAR"
            }
        except Exception as e:
            logger.warning(f"MCAR test failed: {e}")
            return {
                "test_name": "Simplified MCAR Test",
                "error": str(e),
                "is_mcar": None,
                "interpretation": "Test failed"
            }
    
    def _test_missing_dependencies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Test for dependencies between missing patterns in different columns
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            List of dependency test results
        """
        dependency_tests = []
        columns_with_missing = df.columns[df.isnull().sum() > 0].tolist()
        
        # Test pairwise dependencies
        for col1, col2 in itertools.combinations(columns_with_missing, 2):
            missing1 = df[col1].isnull()
            missing2 = df[col2].isnull()
            
            # Create contingency table
            contingency_table = pd.crosstab(missing1, missing2)
            
            try:
                chi2_stat, p_value, dof, expected = chi2_contingency(contingency_table)
                
                dependency_tests.append({
                    "column1": col1,
                    "column2": col2,
                    "chi2_statistic": round(chi2_stat, 4),
                    "p_value": round(p_value, 4),
                    "is_dependent": p_value < self.significance_level,
                    "cramers_v": self._calculate_cramers_v(contingency_table, chi2_stat)
                })
            except Exception as e:
                logger.warning(f"Dependency test failed for {col1}-{col2}: {e}")
        
        return dependency_tests
    
    def _calculate_cramers_v(self, contingency_table: pd.DataFrame, chi2_stat: float) -> float:
        """
        Calculate Cramer's V for association strength
        
        Args:
            contingency_table: Contingency table
            chi2_stat: Chi-square statistic
            
        Returns:
            Cramer's V value
        """
        n = contingency_table.sum().sum()
        min_dim = min(contingency_table.shape) - 1
        
        if min_dim == 0:
            return 0
        
        cramers_v = np.sqrt(chi2_stat / (n * min_dim))
        return round(cramers_v, 3)
    
    def _test_missing_randomness(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Test for randomness of missing data patterns
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            List of randomness test results
        """
        randomness_tests = []
        
        for column in df.columns:
            if df[column].isnull().sum() == 0:
                continue
            
            missing_indicator = df[column].isnull().astype(int)
            
            # Runs test for randomness
            runs_test_result = self._runs_test(missing_indicator)
            randomness_tests.append({
                "column": column,
                "test": "Runs Test",
                **runs_test_result
            })
        
        return randomness_tests
    
    def _runs_test(self, sequence: pd.Series) -> Dict[str, Any]:
        """
        Perform runs test for randomness
        
        Args:
            sequence: Binary sequence to test
            
        Returns:
            Runs test results
        """
        n = len(sequence)
        n1 = sequence.sum()  # Number of 1s
        n0 = n - n1  # Number of 0s
        
        if n1 == 0 or n0 == 0:
            return {
                "runs": 0,
                "expected_runs": 0,
                "p_value": 1.0,
                "is_random": True,
                "note": "All values are the same"
            }
        
        # Count runs
        runs = 1
        for i in range(1, n):
            if sequence.iloc[i] != sequence.iloc[i-1]:
                runs += 1
        
        # Expected runs and variance under null hypothesis
        expected_runs = (2 * n1 * n0) / n + 1
        variance = (2 * n1 * n0 * (2 * n1 * n0 - n)) / (n**2 * (n - 1))
        
        if variance <= 0:
            return {
                "runs": runs,
                "expected_runs": expected_runs,
                "p_value": 1.0,
                "is_random": True,
                "note": "Insufficient variance for test"
            }
        
        # Z-score
        z_score = (runs - expected_runs) / np.sqrt(variance)
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
        
        return {
            "runs": runs,
            "expected_runs": round(expected_runs, 2),
            "z_score": round(z_score, 4),
            "p_value": round(p_value, 4),
            "is_random": p_value > self.significance_level
        }
    
    def _determine_overall_mechanism(self, mechanism_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine overall missing data mechanism
        
        Args:
            mechanism_analysis: Results from mechanism tests
            
        Returns:
            Overall mechanism determination
        """
        # Simple heuristic based on test results
        mcar_test = mechanism_analysis.get("little_mcar_test", {})
        dependency_tests = mechanism_analysis.get("dependency_tests", [])
        randomness_tests = mechanism_analysis.get("randomness_tests", [])
        
        # Count evidence for each mechanism
        mcar_evidence = 0
        mar_evidence = 0
        mnar_evidence = 0
        
        # MCAR test evidence
        if mcar_test.get("is_mcar", False):
            mcar_evidence += 2
        
        # Dependency test evidence
        dependent_pairs = sum(1 for test in dependency_tests if test.get("is_dependent", False))
        if dependent_pairs > 0:
            mar_evidence += dependent_pairs
        
        # Randomness test evidence
        non_random_columns = sum(1 for test in randomness_tests if not test.get("is_random", True))
        if non_random_columns > 0:
            mnar_evidence += non_random_columns
        
        # Determine mechanism
        evidence_scores = {
            MissingDataMechanism.MCAR: mcar_evidence,
            MissingDataMechanism.MAR: mar_evidence,
            MissingDataMechanism.MNAR: mnar_evidence
        }
        
        likely_mechanism = max(evidence_scores.items(), key=lambda x: x[1])
        
        return {
            "likely_mechanism": likely_mechanism[0],
            "confidence": likely_mechanism[1] / (sum(evidence_scores.values()) + 1),
            "evidence_scores": evidence_scores
        }
    
    def _analyze_missing_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze correlations between missing patterns and observed values
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Correlation analysis results
        """
        correlation_analysis = {}
        
        # Create missing indicator matrix
        missing_matrix = df.isnull().astype(int)
        
        # Correlations between missing indicators
        missing_corr = missing_matrix.corr()
        
        # Find strong correlations (absolute value > 0.3)
        strong_correlations = []
        
        for i in range(len(missing_corr.columns)):
            for j in range(i+1, len(missing_corr.columns)):
                corr_value = missing_corr.iloc[i, j]
                if abs(corr_value) > 0.3:
                    strong_correlations.append({
                        "column1": missing_corr.columns[i],
                        "column2": missing_corr.columns[j],
                        "correlation": round(corr_value, 3),
                        "strength": "strong" if abs(corr_value) > 0.7 else "moderate"
                    })
        
        correlation_analysis["missing_correlations"] = {
            "correlation_matrix": missing_corr.round(3).to_dict(),
            "strong_correlations": strong_correlations
        }
        
        # Analyze correlations between missingness and observed values
        value_correlations = []
        
        for col_missing in missing_matrix.columns:
            for col_value in df.select_dtypes(include=[np.number]).columns:
                if col_missing != col_value:
                    try:
                        corr = df[col_value].corr(missing_matrix[col_missing])
                        if abs(corr) > 0.2:  # Threshold for meaningful correlation
                            value_correlations.append({
                                "missing_column": col_missing,
                                "value_column": col_value,
                                "correlation": round(corr, 3)
                            })
                    except Exception:
                        continue
        
        correlation_analysis["value_correlations"] = value_correlations
        
        return correlation_analysis
    
    def _generate_insights(self, df: pd.DataFrame, analysis_report: Dict[str, Any]) -> List[MissingDataInsight]:
        """
        Generate actionable insights from missing data analysis
        
        Args:
            df: Original DataFrame
            analysis_report: Analysis results
            
        Returns:
            List of insights
        """
        insights = []
        
        overview = analysis_report["overview"]
        column_analysis = analysis_report["column_analysis"]
        pattern_analysis = analysis_report["pattern_analysis"]
        mechanism_analysis = analysis_report["mechanism_analysis"]
        
        # High missing data insight
        if overview["missing_percentage"] > 20:
            insights.append(MissingDataInsight(
                pattern_type=MissingDataPattern.SYSTEMATIC,
                mechanism=MissingDataMechanism.UNKNOWN,
                description=f"Dataset has high overall missing data ({overview['missing_percentage']:.1f}%)",
                affected_columns=list(df.columns),
                severity="high",
                confidence=0.9,
                suggested_actions=[
                    "Investigate data collection process",
                    "Consider data quality improvement initiatives",
                    "Evaluate if dataset is suitable for analysis"
                ]
            ))
        
        # Columns with excessive missing data
        high_missing_columns = [
            col for col, analysis in column_analysis.items()
            if analysis["missing_percentage"] > 50
        ]
        
        if high_missing_columns:
            insights.append(MissingDataInsight(
                pattern_type=MissingDataPattern.SYSTEMATIC,
                mechanism=MissingDataMechanism.MNAR,
                description=f"Columns with >50% missing data: {high_missing_columns}",
                affected_columns=high_missing_columns,
                severity="high",
                confidence=0.8,
                suggested_actions=[
                    "Consider removing columns with excessive missing data",
                    "Investigate reasons for high missingness",
                    "Evaluate imputation feasibility"
                ]
            ))
        
        # Monotonic pattern insight
        if pattern_analysis["monotonic_analysis"]["is_monotonic"]:
            monotonic_strength = pattern_analysis["monotonic_analysis"]["monotonic_strength"]
            insights.append(MissingDataInsight(
                pattern_type=MissingDataPattern.MONOTONIC,
                mechanism=MissingDataMechanism.MAR,
                description=f"Monotonic missing pattern detected (strength: {monotonic_strength:.2f})",
                affected_columns=list(df.columns),
                severity="medium",
                confidence=monotonic_strength,
                suggested_actions=[
                    "Consider multiple imputation strategies",
                    "Use forward/backward fill for time series",
                    "Investigate systematic data collection issues"
                ]
            ))
        
        # Strong correlations insight
        correlation_analysis = analysis_report["correlation_analysis"]
        strong_corr = correlation_analysis["missing_correlations"]["strong_correlations"]
        
        if strong_corr:
            affected_cols = list(set([item["column1"] for item in strong_corr] + 
                                   [item["column2"] for item in strong_corr]))
            insights.append(MissingDataInsight(
                pattern_type=MissingDataPattern.CLUSTERED,
                mechanism=MissingDataMechanism.MAR,
                description=f"Strong correlations found between missing patterns in {len(strong_corr)} column pairs",
                affected_columns=affected_cols,
                severity="medium",
                confidence=0.7,
                suggested_actions=[
                    "Use multivariate imputation methods",
                    "Consider joint modeling of correlated missingness",
                    "Investigate common causes of missingness"
                ]
            ))
        
        return insights
    
    def _generate_recommendations(self, analysis_report: Dict[str, Any]) -> List[str]:
        """
        Generate actionable recommendations based on analysis
        
        Args:
            analysis_report: Complete analysis report
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        overview = analysis_report["overview"]
        mechanism = analysis_report["mechanism_analysis"]["overall_mechanism"]["likely_mechanism"]
        
        # General recommendations based on missing percentage
        if overview["missing_percentage"] < 5:
            recommendations.append("Low missing data detected. Consider listwise deletion or simple imputation.")
        elif overview["missing_percentage"] < 15:
            recommendations.append("Moderate missing data. Use multiple imputation or advanced single imputation.")
        else:
            recommendations.append("High missing data. Carefully evaluate data quality and consider collection improvements.")
        
        # Mechanism-specific recommendations
        if mechanism == MissingDataMechanism.MCAR:
            recommendations.extend([
                "MCAR mechanism detected - simple imputation methods should work well",
                "Consider mean/median imputation for numeric variables",
                "Mode imputation acceptable for categorical variables"
            ])
        elif mechanism == MissingDataMechanism.MAR:
            recommendations.extend([
                "MAR mechanism detected - use methods that account for relationships",
                "Consider multiple imputation (MICE, chained equations)",
                "Use predictive models for imputation"
            ])
        elif mechanism == MissingDataMechanism.MNAR:
            recommendations.extend([
                "MNAR mechanism suspected - missing data is informative",
                "Consider pattern-mixture models or selection models",
                "Investigate reasons for missingness before imputation"
            ])
        
        # Pattern-specific recommendations
        insights = analysis_report["insights"]
        for insight in insights:
            recommendations.extend(insight.suggested_actions)
        
        return list(set(recommendations))  # Remove duplicates