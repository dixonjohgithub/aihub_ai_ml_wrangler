"""
File: tasks/imputation_tasks.py

Overview:
Celery tasks for data imputation and analysis processing.

Purpose:
Defines background tasks for dataset analysis, missing data imputation,
and correlation matrix generation using Celery.

Dependencies:
- celery: Task queue framework
- pandas: Data manipulation
- numpy: Numerical operations
- sqlalchemy: Database operations

Last Modified: 2025-08-15
Author: Claude
"""

import logging
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

from celery import current_task
import pandas as pd
import numpy as np

from ..database import db_session
from ..models import Dataset, Job, JobStatus, JobType
from ..services.cache_service import cache_service

# Get Celery app from parent module
from ...celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.imputation_tasks.analyze_dataset_task")
def analyze_dataset_task(self, dataset_id: str, job_id: str) -> Dict[str, Any]:
    """
    Analyze dataset for missing data patterns and generate recommendations.
    
    Args:
        dataset_id: ID of the dataset to analyze
        job_id: ID of the job tracking this task
        
    Returns:
        dict: Analysis results
    """
    try:
        logger.info(f"Starting dataset analysis for dataset {dataset_id}")
        
        with db_session() as db:
            # Get dataset and job
            dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
            job = db.query(Job).filter(Job.id == job_id).first()
            
            if not dataset or not job:
                raise ValueError("Dataset or job not found")
            
            # Update job status
            job.start_job(self.request.id)
            job.update_progress(10)
            db.commit()
            
            # Load dataset
            try:
                df = pd.read_csv(dataset.file_path)
                logger.info(f"Loaded dataset with shape: {df.shape}")
            except Exception as e:
                raise ValueError(f"Failed to load dataset: {str(e)}")
            
            job.update_progress(30)
            db.commit()
            
            # Perform analysis
            analysis_results = {
                "dataset_info": {
                    "shape": df.shape,
                    "columns": list(df.columns),
                    "dtypes": df.dtypes.astype(str).to_dict(),
                    "memory_usage": df.memory_usage(deep=True).sum()
                },
                "missing_data": {
                    "total_missing": int(df.isnull().sum().sum()),
                    "missing_by_column": df.isnull().sum().to_dict(),
                    "missing_percentage_by_column": (df.isnull().sum() / len(df) * 100).to_dict(),
                    "rows_with_missing": int(df.isnull().any(axis=1).sum()),
                    "complete_rows": int(df.dropna().shape[0])
                },
                "statistics": {},
                "recommendations": [],
                "data_types": {
                    "numeric_columns": [],
                    "categorical_columns": [],
                    "datetime_columns": [],
                    "text_columns": []
                }
            }
            
            job.update_progress(50)
            db.commit()
            
            # Analyze each column
            for column in df.columns:
                col_data = df[column]
                col_stats = {
                    "missing_count": int(col_data.isnull().sum()),
                    "missing_percentage": float(col_data.isnull().sum() / len(col_data) * 100),
                    "unique_values": int(col_data.nunique()),
                    "data_type": str(col_data.dtype)
                }
                
                # Categorize column type
                if pd.api.types.is_numeric_dtype(col_data):
                    analysis_results["data_types"]["numeric_columns"].append(column)
                    col_stats.update({
                        "mean": float(col_data.mean()) if not col_data.isnull().all() else None,
                        "median": float(col_data.median()) if not col_data.isnull().all() else None,
                        "std": float(col_data.std()) if not col_data.isnull().all() else None,
                        "min": float(col_data.min()) if not col_data.isnull().all() else None,
                        "max": float(col_data.max()) if not col_data.isnull().all() else None
                    })
                elif pd.api.types.is_datetime64_any_dtype(col_data):
                    analysis_results["data_types"]["datetime_columns"].append(column)
                    if not col_data.isnull().all():
                        col_stats.update({
                            "earliest": col_data.min().isoformat() if pd.notnull(col_data.min()) else None,
                            "latest": col_data.max().isoformat() if pd.notnull(col_data.max()) else None
                        })
                elif col_data.dtype == 'object':
                    if col_data.nunique() / len(col_data) < 0.5:  # Likely categorical
                        analysis_results["data_types"]["categorical_columns"].append(column)
                        col_stats.update({
                            "most_frequent": col_data.mode().iloc[0] if not col_data.mode().empty else None,
                            "frequency_of_most_frequent": int(col_data.value_counts().iloc[0]) if not col_data.value_counts().empty else None
                        })
                    else:  # Likely text
                        analysis_results["data_types"]["text_columns"].append(column)
                        col_stats.update({
                            "avg_length": float(col_data.astype(str).str.len().mean()) if not col_data.isnull().all() else None,
                            "max_length": int(col_data.astype(str).str.len().max()) if not col_data.isnull().all() else None
                        })
                
                analysis_results["statistics"][column] = col_stats
            
            job.update_progress(70)
            db.commit()
            
            # Generate recommendations
            recommendations = []
            
            for column, stats in analysis_results["statistics"].items():
                missing_pct = stats["missing_percentage"]
                
                if missing_pct > 0:
                    if missing_pct < 5:
                        recommendations.append({
                            "column": column,
                            "missing_percentage": missing_pct,
                            "recommendation": "drop_rows",
                            "reason": "Low missing percentage - consider dropping rows",
                            "priority": "low"
                        })
                    elif missing_pct < 20:
                        if column in analysis_results["data_types"]["numeric_columns"]:
                            recommendations.append({
                                "column": column,
                                "missing_percentage": missing_pct,
                                "recommendation": "mean_imputation",
                                "reason": "Moderate missing percentage in numeric column",
                                "priority": "medium"
                            })
                        else:
                            recommendations.append({
                                "column": column,
                                "missing_percentage": missing_pct,
                                "recommendation": "mode_imputation",
                                "reason": "Moderate missing percentage in categorical column",
                                "priority": "medium"
                            })
                    elif missing_pct < 50:
                        recommendations.append({
                            "column": column,
                            "missing_percentage": missing_pct,
                            "recommendation": "advanced_imputation",
                            "reason": "High missing percentage - consider KNN or iterative imputation",
                            "priority": "high"
                        })
                    else:
                        recommendations.append({
                            "column": column,
                            "missing_percentage": missing_pct,
                            "recommendation": "drop_column",
                            "reason": "Very high missing percentage - consider dropping column",
                            "priority": "high"
                        })
            
            analysis_results["recommendations"] = recommendations
            
            job.update_progress(90)
            db.commit()
            
            # Store results
            dataset.set_analysis_results(analysis_results)
            dataset.status = "analyzed"
            dataset.row_count = df.shape[0]
            dataset.column_count = df.shape[1]
            dataset.missing_values_count = analysis_results["missing_data"]["total_missing"]
            dataset.missing_percentage = f"{analysis_results['missing_data']['total_missing'] / (df.shape[0] * df.shape[1]) * 100:.2f}%"
            
            # Complete job
            job.complete_job(analysis_results)
            db.commit()
            
            logger.info(f"Dataset analysis completed for dataset {dataset_id}")
            return analysis_results
            
    except Exception as e:
        logger.error(f"Dataset analysis failed: {str(e)}")
        
        with db_session() as db:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.fail_job(str(e))
                db.commit()
        
        raise


@celery_app.task(bind=True, name="app.tasks.imputation_tasks.process_imputation_task")
def process_imputation_task(self, dataset_id: str, job_id: str, imputation_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process data imputation based on configuration.
    
    Args:
        dataset_id: ID of the dataset to process
        job_id: ID of the job tracking this task
        imputation_config: Imputation configuration
        
    Returns:
        dict: Processing results
    """
    try:
        logger.info(f"Starting imputation processing for dataset {dataset_id}")
        
        with db_session() as db:
            # Get dataset and job
            dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
            job = db.query(Job).filter(Job.id == job_id).first()
            
            if not dataset or not job:
                raise ValueError("Dataset or job not found")
            
            # Update job status
            job.start_job(self.request.id)
            job.set_parameters(imputation_config)
            job.update_progress(10)
            db.commit()
            
            # Load dataset
            try:
                df = pd.read_csv(dataset.file_path)
                original_shape = df.shape
                logger.info(f"Loaded dataset with shape: {original_shape}")
            except Exception as e:
                raise ValueError(f"Failed to load dataset: {str(e)}")
            
            job.update_progress(30)
            db.commit()
            
            # Apply imputation strategies
            imputed_df = df.copy()
            imputation_log = []
            
            for column_config in imputation_config.get("columns", []):
                column = column_config["column"]
                strategy = column_config["strategy"]
                
                if column not in imputed_df.columns:
                    continue
                
                missing_count = imputed_df[column].isnull().sum()
                if missing_count == 0:
                    continue
                
                logger.info(f"Applying {strategy} imputation to column {column}")
                
                try:
                    if strategy == "drop_rows":
                        before_rows = len(imputed_df)
                        imputed_df = imputed_df.dropna(subset=[column])
                        after_rows = len(imputed_df)
                        imputation_log.append({
                            "column": column,
                            "strategy": strategy,
                            "rows_removed": before_rows - after_rows,
                            "success": True
                        })
                    
                    elif strategy == "mean_imputation":
                        if pd.api.types.is_numeric_dtype(imputed_df[column]):
                            mean_value = imputed_df[column].mean()
                            imputed_df[column].fillna(mean_value, inplace=True)
                            imputation_log.append({
                                "column": column,
                                "strategy": strategy,
                                "fill_value": float(mean_value),
                                "imputed_count": missing_count,
                                "success": True
                            })
                    
                    elif strategy == "median_imputation":
                        if pd.api.types.is_numeric_dtype(imputed_df[column]):
                            median_value = imputed_df[column].median()
                            imputed_df[column].fillna(median_value, inplace=True)
                            imputation_log.append({
                                "column": column,
                                "strategy": strategy,
                                "fill_value": float(median_value),
                                "imputed_count": missing_count,
                                "success": True
                            })
                    
                    elif strategy == "mode_imputation":
                        mode_values = imputed_df[column].mode()
                        if not mode_values.empty:
                            mode_value = mode_values.iloc[0]
                            imputed_df[column].fillna(mode_value, inplace=True)
                            imputation_log.append({
                                "column": column,
                                "strategy": strategy,
                                "fill_value": mode_value,
                                "imputed_count": missing_count,
                                "success": True
                            })
                    
                    elif strategy == "forward_fill":
                        imputed_df[column].fillna(method='ffill', inplace=True)
                        imputation_log.append({
                            "column": column,
                            "strategy": strategy,
                            "imputed_count": missing_count,
                            "success": True
                        })
                    
                    elif strategy == "backward_fill":
                        imputed_df[column].fillna(method='bfill', inplace=True)
                        imputation_log.append({
                            "column": column,
                            "strategy": strategy,
                            "imputed_count": missing_count,
                            "success": True
                        })
                    
                    elif strategy == "constant_fill":
                        fill_value = column_config.get("fill_value", 0)
                        imputed_df[column].fillna(fill_value, inplace=True)
                        imputation_log.append({
                            "column": column,
                            "strategy": strategy,
                            "fill_value": fill_value,
                            "imputed_count": missing_count,
                            "success": True
                        })
                    
                    elif strategy == "drop_column":
                        imputed_df.drop(columns=[column], inplace=True)
                        imputation_log.append({
                            "column": column,
                            "strategy": strategy,
                            "success": True
                        })
                    
                except Exception as e:
                    logger.error(f"Failed to apply {strategy} to column {column}: {str(e)}")
                    imputation_log.append({
                        "column": column,
                        "strategy": strategy,
                        "error": str(e),
                        "success": False
                    })
            
            job.update_progress(70)
            db.commit()
            
            # Generate output filename
            base_name = os.path.splitext(dataset.original_filename)[0]
            output_filename = f"{base_name}_imputed.csv"
            output_path = os.path.join(os.path.dirname(dataset.file_path), output_filename)
            
            # Save imputed dataset
            imputed_df.to_csv(output_path, index=False)
            
            job.update_progress(90)
            db.commit()
            
            # Prepare results
            results = {
                "original_shape": original_shape,
                "final_shape": imputed_df.shape,
                "imputation_log": imputation_log,
                "output_file": output_path,
                "missing_data_summary": {
                    "original_missing": int(df.isnull().sum().sum()),
                    "final_missing": int(imputed_df.isnull().sum().sum()),
                    "rows_removed": original_shape[0] - imputed_df.shape[0],
                    "columns_removed": original_shape[1] - imputed_df.shape[1]
                }
            }
            
            # Update dataset
            dataset.set_processing_config(imputation_config)
            dataset.mark_as_processed()
            
            # Complete job
            job.complete_job(results)
            job.set_output_files([output_path])
            db.commit()
            
            logger.info(f"Imputation processing completed for dataset {dataset_id}")
            return results
            
    except Exception as e:
        logger.error(f"Imputation processing failed: {str(e)}")
        
        with db_session() as db:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.fail_job(str(e))
                db.commit()
        
        raise


@celery_app.task(bind=True, name="app.tasks.imputation_tasks.generate_correlation_matrix_task")
def generate_correlation_matrix_task(self, dataset_id: str, job_id: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate correlation matrix for numeric columns.
    
    Args:
        dataset_id: ID of the dataset
        job_id: ID of the job tracking this task
        options: Additional options for correlation calculation
        
    Returns:
        dict: Correlation matrix results
    """
    try:
        logger.info(f"Starting correlation matrix generation for dataset {dataset_id}")
        
        with db_session() as db:
            # Get dataset and job
            dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
            job = db.query(Job).filter(Job.id == job_id).first()
            
            if not dataset or not job:
                raise ValueError("Dataset or job not found")
            
            # Update job status
            job.start_job(self.request.id)
            job.update_progress(10)
            db.commit()
            
            # Load dataset (use processed version if available)
            try:
                if dataset.is_processed and dataset.get_processing_config():
                    # Try to find the processed file
                    base_name = os.path.splitext(dataset.original_filename)[0]
                    processed_filename = f"{base_name}_imputed.csv"
                    processed_path = os.path.join(os.path.dirname(dataset.file_path), processed_filename)
                    
                    if os.path.exists(processed_path):
                        df = pd.read_csv(processed_path)
                        logger.info(f"Using processed dataset with shape: {df.shape}")
                    else:
                        df = pd.read_csv(dataset.file_path)
                        logger.info(f"Using original dataset with shape: {df.shape}")
                else:
                    df = pd.read_csv(dataset.file_path)
                    logger.info(f"Using original dataset with shape: {df.shape}")
                    
            except Exception as e:
                raise ValueError(f"Failed to load dataset: {str(e)}")
            
            job.update_progress(30)
            db.commit()
            
            # Get numeric columns only
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if not numeric_columns:
                raise ValueError("No numeric columns found for correlation analysis")
            
            logger.info(f"Computing correlation for {len(numeric_columns)} numeric columns")
            
            # Compute correlation matrix
            correlation_method = options.get("method", "pearson") if options else "pearson"
            corr_matrix = df[numeric_columns].corr(method=correlation_method)
            
            job.update_progress(70)
            db.commit()
            
            # Generate output files
            base_name = os.path.splitext(dataset.original_filename)[0]
            
            # Save correlation matrix as CSV
            corr_csv_filename = f"{base_name}_correlation.csv"
            corr_csv_path = os.path.join(os.path.dirname(dataset.file_path), corr_csv_filename)
            corr_matrix.to_csv(corr_csv_path)
            
            # Create correlation analysis
            correlation_analysis = {
                "method": correlation_method,
                "numeric_columns": numeric_columns,
                "correlation_matrix": corr_matrix.round(4).to_dict(),
                "strong_correlations": [],
                "weak_correlations": [],
                "summary_stats": {
                    "mean_correlation": float(corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean()),
                    "max_correlation": float(corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].max()),
                    "min_correlation": float(corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].min())
                }
            }
            
            # Find strong and weak correlations
            for i, col1 in enumerate(numeric_columns):
                for j, col2 in enumerate(numeric_columns):
                    if i < j:  # Avoid duplicates and self-correlation
                        corr_value = corr_matrix.iloc[i, j]
                        
                        if abs(corr_value) > 0.7:
                            correlation_analysis["strong_correlations"].append({
                                "column1": col1,
                                "column2": col2,
                                "correlation": float(corr_value)
                            })
                        elif abs(corr_value) < 0.3:
                            correlation_analysis["weak_correlations"].append({
                                "column1": col1,
                                "column2": col2,
                                "correlation": float(corr_value)
                            })
            
            job.update_progress(90)
            db.commit()
            
            # Prepare results
            results = {
                "correlation_analysis": correlation_analysis,
                "output_files": [corr_csv_path],
                "numeric_columns_count": len(numeric_columns),
                "strong_correlations_count": len(correlation_analysis["strong_correlations"]),
                "weak_correlations_count": len(correlation_analysis["weak_correlations"])
            }
            
            # Complete job
            job.complete_job(results)
            job.set_output_files([corr_csv_path])
            db.commit()
            
            logger.info(f"Correlation matrix generation completed for dataset {dataset_id}")
            return results
            
    except Exception as e:
        logger.error(f"Correlation matrix generation failed: {str(e)}")
        
        with db_session() as db:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.fail_job(str(e))
                db.commit()
        
        raise