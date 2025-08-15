"""
File: report_service.py

Overview:
Comprehensive report generation service for ML analysis results.

Purpose:
Generates detailed markdown reports, visualizations, and metadata documentation.

Dependencies:
- pandas: Data manipulation
- matplotlib/plotly: Visualizations
- markdown: Report formatting

Last Modified: 2025-08-15
Author: Claude
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objs as go
import plotly.io as pio
from enum import Enum
import logging
import hashlib
import uuid

logger = logging.getLogger(__name__)

# Set matplotlib style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class ReportSection(Enum):
    """Available report sections"""
    EXECUTIVE_SUMMARY = "executive_summary"
    DATA_OVERVIEW = "data_overview"
    MISSING_DATA_ANALYSIS = "missing_data_analysis"
    IMPUTATION_DETAILS = "imputation_details"
    CORRELATION_ANALYSIS = "correlation_analysis"
    QUALITY_METRICS = "quality_metrics"
    RECOMMENDATIONS = "recommendations"
    TECHNICAL_DETAILS = "technical_details"


@dataclass
class ReportConfig:
    """Configuration for report generation"""
    title: str
    sections: List[ReportSection]
    include_visualizations: bool = True
    include_metadata: bool = True
    include_code_snippets: bool = False
    export_format: str = "markdown"  # markdown, html, pdf
    custom_template: Optional[str] = None


@dataclass
class ReportData:
    """Data container for report generation"""
    original_data: pd.DataFrame
    imputed_data: Optional[pd.DataFrame]
    correlation_matrix: Optional[pd.DataFrame]
    imputation_config: Optional[Dict[str, Any]]
    quality_metrics: Optional[Dict[str, float]]
    ai_recommendations: Optional[List[Dict[str, Any]]]
    transformation_history: Optional[List[Dict[str, Any]]]
    dataset_metadata: Dict[str, Any]


class ReportGeneratorService:
    """
    Service for generating comprehensive analysis reports
    """
    
    def __init__(self, output_dir: str = "reports"):
        """Initialize report generator"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.report_id = None
        self.visualizations = []
        
    def generate_report(
        self,
        data: ReportData,
        config: ReportConfig
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate comprehensive report
        
        Args:
            data: Report data container
            config: Report configuration
            
        Returns:
            Tuple of (report content, metadata)
        """
        self.report_id = str(uuid.uuid4())[:8]
        report_content = []
        metadata = {
            "report_id": self.report_id,
            "generated_at": datetime.now().isoformat(),
            "title": config.title,
            "sections": [s.value for s in config.sections]
        }
        
        # Add report header
        report_content.append(self._generate_header(config.title))
        
        # Generate each requested section
        for section in config.sections:
            if section == ReportSection.EXECUTIVE_SUMMARY:
                content = self._generate_executive_summary(data)
            elif section == ReportSection.DATA_OVERVIEW:
                content = self._generate_data_overview(data)
            elif section == ReportSection.MISSING_DATA_ANALYSIS:
                content = self._generate_missing_data_analysis(data)
            elif section == ReportSection.IMPUTATION_DETAILS:
                content = self._generate_imputation_details(data)
            elif section == ReportSection.CORRELATION_ANALYSIS:
                content = self._generate_correlation_analysis(data)
            elif section == ReportSection.QUALITY_METRICS:
                content = self._generate_quality_metrics(data)
            elif section == ReportSection.RECOMMENDATIONS:
                content = self._generate_recommendations(data)
            elif section == ReportSection.TECHNICAL_DETAILS:
                content = self._generate_technical_details(data)
            else:
                continue
            
            report_content.append(content)
        
        # Add visualizations if requested
        if config.include_visualizations and self.visualizations:
            report_content.append(self._generate_visualizations_section())
        
        # Add metadata if requested
        if config.include_metadata:
            report_content.append(self._generate_metadata_section(data, metadata))
        
        # Add footer
        report_content.append(self._generate_footer())
        
        # Combine all sections
        final_report = "\n\n".join(report_content)
        
        # Save report
        report_path = self._save_report(final_report, config.export_format)
        metadata["report_path"] = str(report_path)
        
        return final_report, metadata
    
    def _generate_header(self, title: str) -> str:
        """Generate report header"""
        return f"""# {title}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Report ID:** {self.report_id}  
**Tool:** AI Hub AI/ML Wrangler

---"""
    
    def _generate_executive_summary(self, data: ReportData) -> str:
        """Generate executive summary section"""
        total_missing = data.original_data.isnull().sum().sum()
        total_cells = data.original_data.size
        missing_percentage = (total_missing / total_cells) * 100
        
        summary = f"""## Executive Summary

### Key Findings
- **Dataset Size:** {len(data.original_data):,} rows × {len(data.original_data.columns)} columns
- **Total Missing Values:** {total_missing:,} ({missing_percentage:.2f}% of all data)
- **Columns with Missing Data:** {data.original_data.isnull().any().sum()} out of {len(data.original_data.columns)}"""
        
        if data.imputed_data is not None:
            remaining_missing = data.imputed_data.isnull().sum().sum()
            imputed_count = total_missing - remaining_missing
            summary += f"""
- **Values Imputed:** {imputed_count:,}
- **Imputation Success Rate:** {(imputed_count/total_missing*100):.1f}%"""
        
        if data.quality_metrics:
            summary += f"""
- **Data Quality Score:** {data.quality_metrics.get('overall_score', 0):.2f}/100"""
        
        if data.correlation_matrix is not None:
            high_corr_count = self._count_high_correlations(data.correlation_matrix)
            summary += f"""
- **High Correlations (>0.8):** {high_corr_count} pairs identified"""
        
        return summary
    
    def _generate_data_overview(self, data: ReportData) -> str:
        """Generate data overview section"""
        df = data.original_data
        
        # Column type distribution
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime']).columns.tolist()
        
        overview = f"""## Data Overview

### Dataset Characteristics
- **Total Records:** {len(df):,}
- **Total Features:** {len(df.columns)}
- **Memory Usage:** {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB

### Column Types
- **Numeric:** {len(numeric_cols)} columns
- **Categorical:** {len(categorical_cols)} columns
- **Datetime:** {len(datetime_cols)} columns

### Numeric Features Summary
"""
        
        if numeric_cols:
            # Create summary statistics table
            summary_stats = df[numeric_cols].describe().round(2)
            overview += self._dataframe_to_markdown(summary_stats.T)
        
        if categorical_cols and len(categorical_cols) <= 10:
            overview += "\n### Categorical Features Summary\n"
            for col in categorical_cols[:5]:  # Limit to first 5
                unique_count = df[col].nunique()
                mode_value = df[col].mode()[0] if not df[col].mode().empty else "N/A"
                overview += f"- **{col}:** {unique_count} unique values, mode = '{mode_value}'\n"
        
        # Add visualization
        if len(numeric_cols) > 0:
            self._create_distribution_plot(df[numeric_cols[:6]])  # Plot first 6 numeric columns
        
        return overview
    
    def _generate_missing_data_analysis(self, data: ReportData) -> str:
        """Generate missing data analysis section"""
        df = data.original_data
        
        missing_counts = df.isnull().sum()
        missing_pcts = (missing_counts / len(df)) * 100
        
        # Create missing data summary
        missing_summary = pd.DataFrame({
            'Column': missing_counts.index,
            'Missing_Count': missing_counts.values,
            'Missing_Percentage': missing_pcts.values
        })
        missing_summary = missing_summary[missing_summary['Missing_Count'] > 0]
        missing_summary = missing_summary.sort_values('Missing_Percentage', ascending=False)
        
        analysis = f"""## Missing Data Analysis

### Overall Missing Data Pattern
- **Total Missing Cells:** {missing_counts.sum():,}
- **Columns with Missing Data:** {(missing_counts > 0).sum()}
- **Complete Columns:** {(missing_counts == 0).sum()}

### Missing Data by Column
"""
        
        if not missing_summary.empty:
            analysis += self._dataframe_to_markdown(missing_summary.head(20))
            
            # Categorize missing patterns
            low_missing = missing_summary[missing_summary['Missing_Percentage'] < 5]
            moderate_missing = missing_summary[(missing_summary['Missing_Percentage'] >= 5) & 
                                             (missing_summary['Missing_Percentage'] < 20)]
            high_missing = missing_summary[missing_summary['Missing_Percentage'] >= 20]
            
            analysis += f"""
### Missing Data Categories
- **Low (<5% missing):** {len(low_missing)} columns
- **Moderate (5-20% missing):** {len(moderate_missing)} columns
- **High (>20% missing):** {len(high_missing)} columns"""
            
            # Add missing data heatmap
            self._create_missing_data_heatmap(df)
        
        return analysis
    
    def _generate_imputation_details(self, data: ReportData) -> str:
        """Generate imputation details section"""
        if not data.imputation_config:
            return "## Imputation Details\n\n*No imputation performed*"
        
        details = """## Imputation Details

### Imputation Strategy Summary
"""
        
        # Group strategies by type
        strategies_used = {}
        for col_config in data.imputation_config.get('columns', []):
            strategy = col_config.get('strategy', 'unknown')
            if strategy not in strategies_used:
                strategies_used[strategy] = []
            strategies_used[strategy].append(col_config.get('column', ''))
        
        for strategy, columns in strategies_used.items():
            details += f"\n**{strategy.upper()} Imputation:**\n"
            for col in columns[:10]:  # Limit to first 10
                details += f"- {col}\n"
            if len(columns) > 10:
                details += f"- ... and {len(columns) - 10} more columns\n"
        
        # Add quality metrics if available
        if data.quality_metrics:
            details += "\n### Imputation Quality Metrics\n"
            for metric, value in data.quality_metrics.items():
                if isinstance(value, (int, float)):
                    details += f"- **{metric.replace('_', ' ').title()}:** {value:.3f}\n"
        
        return details
    
    def _generate_correlation_analysis(self, data: ReportData) -> str:
        """Generate correlation analysis section"""
        if data.correlation_matrix is None:
            return "## Correlation Analysis\n\n*No correlation analysis performed*"
        
        corr_matrix = data.correlation_matrix
        
        # Find high correlations
        high_corrs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.8:
                    high_corrs.append({
                        'Variable_1': corr_matrix.columns[i],
                        'Variable_2': corr_matrix.columns[j],
                        'Correlation': round(corr_value, 3)
                    })
        
        analysis = f"""## Correlation Analysis

### Correlation Matrix Overview
- **Variables Analyzed:** {len(corr_matrix.columns)}
- **High Correlations (|r| > 0.8):** {len(high_corrs)} pairs
- **Correlation Method:** Pearson correlation coefficient"""
        
        if high_corrs:
            analysis += "\n\n### High Correlation Pairs\n"
            high_corr_df = pd.DataFrame(high_corrs).sort_values('Correlation', 
                                                                key=abs, 
                                                                ascending=False)
            analysis += self._dataframe_to_markdown(high_corr_df.head(15))
            
            analysis += "\n\n### Multicollinearity Warnings\n"
            for _, row in high_corr_df.head(5).iterrows():
                analysis += f"- **{row['Variable_1']}** and **{row['Variable_2']}**: "
                analysis += f"r = {row['Correlation']} - Consider removing one variable\n"
        
        # Add correlation heatmap
        self._create_correlation_heatmap(corr_matrix)
        
        return analysis
    
    def _generate_quality_metrics(self, data: ReportData) -> str:
        """Generate quality metrics section"""
        metrics = """## Data Quality Metrics

### Quality Assessment
"""
        
        df = data.imputed_data if data.imputed_data is not None else data.original_data
        
        # Calculate various quality metrics
        quality_scores = {}
        
        # Completeness
        completeness = 1 - (df.isnull().sum().sum() / df.size)
        quality_scores['Completeness'] = completeness
        
        # Uniqueness (for non-numeric columns)
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            uniqueness_scores = []
            for col in categorical_cols:
                unique_ratio = df[col].nunique() / len(df[col])
                uniqueness_scores.append(unique_ratio)
            quality_scores['Uniqueness'] = np.mean(uniqueness_scores)
        
        # Consistency (check for outliers in numeric columns)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            outlier_scores = []
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
                outlier_ratio = 1 - (outliers / len(df))
                outlier_scores.append(outlier_ratio)
            quality_scores['Consistency'] = np.mean(outlier_scores)
        
        # Overall quality score
        overall_score = np.mean(list(quality_scores.values())) * 100
        
        metrics += f"**Overall Data Quality Score: {overall_score:.1f}/100**\n\n"
        
        for metric, score in quality_scores.items():
            metrics += f"- **{metric}:** {score:.3f} ({score*100:.1f}%)\n"
        
        # Add quality issues if any
        if overall_score < 80:
            metrics += "\n### Quality Issues Detected\n"
            if completeness < 0.95:
                metrics += "- ⚠️ Data completeness below 95%\n"
            if 'Consistency' in quality_scores and quality_scores['Consistency'] < 0.95:
                metrics += "- ⚠️ Potential outliers detected in numeric columns\n"
            if 'Uniqueness' in quality_scores and quality_scores['Uniqueness'] < 0.1:
                metrics += "- ⚠️ Low cardinality in categorical columns\n"
        
        return metrics
    
    def _generate_recommendations(self, data: ReportData) -> str:
        """Generate recommendations section"""
        recommendations = """## Recommendations

### Data Quality Improvements
"""
        
        df = data.original_data
        
        # Check for various issues and provide recommendations
        issues_found = []
        
        # Missing data recommendations
        missing_pcts = (df.isnull().sum() / len(df)) * 100
        high_missing = missing_pcts[missing_pcts > 30]
        if len(high_missing) > 0:
            issues_found.append(f"- **High Missing Data:** Consider removing columns {', '.join(high_missing.index[:3].tolist())} with >30% missing values")
        
        # Correlation recommendations
        if data.correlation_matrix is not None:
            high_corr_count = self._count_high_correlations(data.correlation_matrix)
            if high_corr_count > 0:
                issues_found.append(f"- **Multicollinearity:** {high_corr_count} variable pairs show high correlation (>0.8). Consider feature selection or PCA")
        
        # Cardinality recommendations
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if df[col].nunique() > 50:
                issues_found.append(f"- **High Cardinality:** Column '{col}' has {df[col].nunique()} unique values. Consider encoding strategies or grouping")
                break
        
        # Add AI recommendations if available
        if data.ai_recommendations:
            recommendations += "\n### AI-Powered Suggestions\n"
            for i, rec in enumerate(data.ai_recommendations[:5], 1):
                recommendations += f"\n**{i}. {rec.get('strategy', 'Recommendation')}**\n"
                recommendations += f"- **Confidence:** {rec.get('confidence', 0):.1%}\n"
                recommendations += f"- **Reasoning:** {rec.get('reasoning', 'N/A')}\n"
        
        if issues_found:
            recommendations += "\n### Specific Action Items\n"
            for issue in issues_found:
                recommendations += issue + "\n"
        
        # Add next steps
        recommendations += """
### Next Steps
1. Review and apply recommended imputation strategies
2. Address high correlation pairs to reduce multicollinearity
3. Validate imputation results with domain expertise
4. Consider feature engineering for improved model performance
5. Document all transformations for reproducibility"""
        
        return recommendations
    
    def _generate_technical_details(self, data: ReportData) -> str:
        """Generate technical details section"""
        details = """## Technical Details

### Processing Information
"""
        
        # Add metadata
        if data.dataset_metadata:
            details += f"""- **Source File:** {data.dataset_metadata.get('filename', 'Unknown')}
- **File Size:** {data.dataset_metadata.get('file_size_mb', 0):.2f} MB
- **Processing Time:** {data.dataset_metadata.get('processing_time', 0):.2f} seconds
- **Memory Usage:** {data.dataset_metadata.get('memory_usage_mb', 0):.2f} MB"""
        
        details += """

### Environment
- **Platform:** AI Hub AI/ML Wrangler
- **Python Version:** 3.10+
- **Key Libraries:** pandas, scikit-learn, numpy, plotly
- **Report Generated:** """ + datetime.now().isoformat()
        
        # Add transformation history if available
        if data.transformation_history:
            details += "\n\n### Transformation History\n"
            for i, transform in enumerate(data.transformation_history[:10], 1):
                details += f"{i}. {transform.get('action', 'Unknown')} - {transform.get('timestamp', '')}\n"
        
        return details
    
    def _generate_visualizations_section(self) -> str:
        """Generate visualizations section"""
        section = """## Visualizations

The following visualizations have been generated as part of this analysis:

"""
        for viz in self.visualizations:
            section += f"- {viz['title']}: `{viz['filename']}`\n"
        
        return section
    
    def _generate_metadata_section(self, data: ReportData, metadata: Dict) -> str:
        """Generate metadata section"""
        return f"""## Metadata

### Report Metadata
```json
{json.dumps(metadata, indent=2, default=str)}
```

### Reproducibility Information
To reproduce this analysis, use the following configuration:
- Report ID: {self.report_id}
- Dataset Hash: {self._calculate_dataset_hash(data.original_data)}
- Timestamp: {metadata['generated_at']}
"""
    
    def _generate_footer(self) -> str:
        """Generate report footer"""
        return f"""---

*Report generated by AI Hub AI/ML Wrangler*  
*Report ID: {self.report_id}*  
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"""
    
    # Helper methods
    
    def _dataframe_to_markdown(self, df: pd.DataFrame, max_rows: int = 20) -> str:
        """Convert DataFrame to markdown table"""
        if len(df) > max_rows:
            df = df.head(max_rows)
        
        return df.to_markdown(index=True)
    
    def _count_high_correlations(self, corr_matrix: pd.DataFrame, threshold: float = 0.8) -> int:
        """Count number of high correlation pairs"""
        count = 0
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i, j]) > threshold:
                    count += 1
        return count
    
    def _calculate_dataset_hash(self, df: pd.DataFrame) -> str:
        """Calculate hash of dataset for reproducibility"""
        # Use shape and column names for hash
        hash_input = f"{df.shape}_{','.join(df.columns.tolist())}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:8]
    
    def _create_distribution_plot(self, df: pd.DataFrame):
        """Create distribution plots for numeric columns"""
        n_cols = len(df.columns)
        if n_cols == 0:
            return
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()
        
        for i, col in enumerate(df.columns[:6]):
            df[col].hist(ax=axes[i], bins=30, edgecolor='black')
            axes[i].set_title(f'Distribution of {col}')
            axes[i].set_xlabel(col)
            axes[i].set_ylabel('Frequency')
        
        # Hide unused subplots
        for i in range(n_cols, 6):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        filename = f"distribution_plot_{self.report_id}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        self.visualizations.append({
            'title': 'Distribution Plots',
            'filename': filename,
            'type': 'histogram'
        })
    
    def _create_missing_data_heatmap(self, df: pd.DataFrame):
        """Create missing data heatmap"""
        # Select columns with missing data
        missing_cols = df.columns[df.isnull().any()].tolist()
        if not missing_cols:
            return
        
        # Limit to top 30 columns with most missing data
        if len(missing_cols) > 30:
            missing_counts = df[missing_cols].isnull().sum()
            missing_cols = missing_counts.nlargest(30).index.tolist()
        
        # Create binary matrix (1 for missing, 0 for present)
        missing_matrix = df[missing_cols].isnull().astype(int)
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(missing_matrix.T, cmap='RdYlBu', cbar_kws={'label': 'Missing (1) vs Present (0)'})
        plt.title('Missing Data Pattern')
        plt.xlabel('Row Index')
        plt.ylabel('Columns')
        plt.tight_layout()
        
        filename = f"missing_data_heatmap_{self.report_id}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        self.visualizations.append({
            'title': 'Missing Data Heatmap',
            'filename': filename,
            'type': 'heatmap'
        })
    
    def _create_correlation_heatmap(self, corr_matrix: pd.DataFrame):
        """Create correlation heatmap"""
        # Limit to top 20 variables if too many
        if len(corr_matrix.columns) > 20:
            # Select variables with highest average correlation
            avg_corr = corr_matrix.abs().mean()
            top_vars = avg_corr.nlargest(20).index
            corr_matrix = corr_matrix.loc[top_vars, top_vars]
        
        plt.figure(figsize=(12, 10))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f', 
                   cmap='coolwarm', center=0, vmin=-1, vmax=1,
                   square=True, linewidths=0.5)
        plt.title('Correlation Matrix Heatmap')
        plt.tight_layout()
        
        filename = f"correlation_heatmap_{self.report_id}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        self.visualizations.append({
            'title': 'Correlation Heatmap',
            'filename': filename,
            'type': 'heatmap'
        })
    
    def _save_report(self, content: str, format: str) -> Path:
        """Save report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"ml_analysis_report_{timestamp}_{self.report_id}.{format}"
        filepath = self.output_dir / filename
        
        if format == "markdown" or format == "md":
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        elif format == "html":
            # Convert markdown to HTML (requires markdown library)
            import markdown
            html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"<html><body>{html_content}</body></html>")
        else:
            # Default to markdown
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        logger.info(f"Report saved to {filepath}")
        return filepath
    
    def export_metadata(self, data: ReportData, metadata: Dict) -> Path:
        """Export complete metadata as JSON"""
        full_metadata = {
            **metadata,
            "dataset": {
                "rows": len(data.original_data),
                "columns": len(data.original_data.columns),
                "column_names": data.original_data.columns.tolist(),
                "dtypes": {col: str(dtype) for col, dtype in data.original_data.dtypes.items()}
            },
            "missing_data": {
                col: float(pct) for col, pct in 
                ((data.original_data.isnull().sum() / len(data.original_data)) * 100).items()
            },
            "imputation": data.imputation_config,
            "quality_metrics": data.quality_metrics,
            "visualizations": self.visualizations
        }
        
        filename = f"ml_analysis_metadata_{self.report_id}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(full_metadata, f, indent=2, default=str)
        
        logger.info(f"Metadata exported to {filepath}")
        return filepath