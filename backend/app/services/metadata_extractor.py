"""
File: metadata_extractor.py

Overview:
JSON metadata extraction service for analyzing dataset metadata and configuration files

Purpose:
Extracts and validates metadata from JSON files, including dataset descriptions,
column definitions, transformation history, and data lineage information

Dependencies:
- json: JSON parsing and validation
- jsonschema: JSON schema validation
- pandas: Data type validation and conversion
- pathlib: File path handling

Last Modified: 2025-08-15
Author: Claude
"""

import json
import jsonschema
from jsonschema import validate, ValidationError
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MetadataExtractionError(Exception):
    """Custom exception for metadata extraction errors"""
    pass

class JSONMetadataExtractor:
    """
    Service for extracting and validating metadata from JSON files
    """
    
    def __init__(self):
        """Initialize metadata extractor with validation schemas"""
        self.dataset_schema = self._get_dataset_schema()
        self.column_schema = self._get_column_schema()
        self.transformation_schema = self._get_transformation_schema()
    
    def _get_dataset_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for dataset metadata validation
        
        Returns:
            JSON schema for dataset metadata
        """
        return {
            "type": "object",
            "properties": {
                "dataset_name": {"type": "string"},
                "description": {"type": "string"},
                "source": {"type": "string"},
                "created_date": {"type": "string", "format": "date-time"},
                "last_modified": {"type": "string", "format": "date-time"},
                "version": {"type": "string"},
                "size_info": {
                    "type": "object",
                    "properties": {
                        "rows": {"type": "integer", "minimum": 0},
                        "columns": {"type": "integer", "minimum": 0},
                        "file_size_bytes": {"type": "integer", "minimum": 0}
                    }
                },
                "columns": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/column"}
                },
                "transformations": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/transformation"}
                }
            },
            "required": ["dataset_name", "columns"],
            "definitions": {
                "column": self._get_column_schema(),
                "transformation": self._get_transformation_schema()
            }
        }
    
    def _get_column_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for column metadata validation
        
        Returns:
            JSON schema for column metadata
        """
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "display_name": {"type": "string"},
                "description": {"type": "string"},
                "data_type": {
                    "type": "string",
                    "enum": ["integer", "float", "string", "boolean", "datetime", "categorical"]
                },
                "pandas_dtype": {"type": "string"},
                "nullable": {"type": "boolean"},
                "unique": {"type": "boolean"},
                "primary_key": {"type": "boolean"},
                "statistics": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer"},
                        "missing_count": {"type": "integer"},
                        "missing_percentage": {"type": "number"},
                        "unique_count": {"type": "integer"},
                        "unique_percentage": {"type": "number"}
                    }
                },
                "constraints": {
                    "type": "object",
                    "properties": {
                        "min_value": {"type": ["number", "null"]},
                        "max_value": {"type": ["number", "null"]},
                        "min_length": {"type": ["integer", "null"]},
                        "max_length": {"type": ["integer", "null"]},
                        "pattern": {"type": ["string", "null"]},
                        "allowed_values": {"type": ["array", "null"]}
                    }
                },
                "encoding_info": {
                    "type": "object",
                    "properties": {
                        "encoding_type": {"type": "string"},
                        "encoded_values": {"type": "object"},
                        "original_type": {"type": "string"}
                    }
                }
            },
            "required": ["name", "data_type"]
        }
    
    def _get_transformation_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for transformation metadata validation
        
        Returns:
            JSON schema for transformation metadata
        """
        return {
            "type": "object",
            "properties": {
                "transformation_id": {"type": "string"},
                "transformation_type": {
                    "type": "string",
                    "enum": ["imputation", "encoding", "scaling", "feature_engineering", "validation"]
                },
                "column_name": {"type": "string"},
                "method": {"type": "string"},
                "parameters": {"type": "object"},
                "applied_date": {"type": "string", "format": "date-time"},
                "before_stats": {"type": "object"},
                "after_stats": {"type": "object"},
                "quality_metrics": {"type": "object"}
            },
            "required": ["transformation_id", "transformation_type", "column_name", "method"]
        }
    
    async def extract_metadata_from_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Extract metadata from a JSON file
        
        Args:
            file_path: Path to the JSON metadata file
            
        Returns:
            Extracted and validated metadata
            
        Raises:
            MetadataExtractionError: If extraction or validation fails
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise MetadataExtractionError(f"Metadata file not found: {file_path}")
            
            # Read JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_metadata = json.load(f)
            
            # Validate against schema
            self.validate_metadata_schema(raw_metadata)
            
            # Process and enrich metadata
            processed_metadata = self._process_metadata(raw_metadata)
            
            logger.info(f"Successfully extracted metadata from {file_path}")
            return processed_metadata
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in metadata file: {e}")
            raise MetadataExtractionError(f"Invalid JSON format: {e}")
        except Exception as e:
            logger.error(f"Failed to extract metadata: {e}")
            raise MetadataExtractionError(f"Metadata extraction failed: {e}")
    
    def validate_metadata_schema(self, metadata: Dict[str, Any]) -> bool:
        """
        Validate metadata against JSON schema
        
        Args:
            metadata: Metadata dictionary to validate
            
        Returns:
            True if valid
            
        Raises:
            MetadataExtractionError: If validation fails
        """
        try:
            validate(instance=metadata, schema=self.dataset_schema)
            logger.debug("Metadata schema validation passed")
            return True
            
        except ValidationError as e:
            logger.error(f"Metadata schema validation failed: {e.message}")
            raise MetadataExtractionError(f"Invalid metadata schema: {e.message}")
    
    def _process_metadata(self, raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and enrich raw metadata
        
        Args:
            raw_metadata: Raw metadata from JSON file
            
        Returns:
            Processed and enriched metadata
        """
        processed = raw_metadata.copy()
        
        # Add processing timestamp
        processed['extracted_at'] = datetime.now().isoformat()
        
        # Process column metadata
        if 'columns' in processed:
            processed['columns'] = [
                self._process_column_metadata(col) for col in processed['columns']
            ]
        
        # Process transformation metadata
        if 'transformations' in processed:
            processed['transformations'] = [
                self._process_transformation_metadata(trans) for trans in processed['transformations']
            ]
        
        # Calculate summary statistics
        processed['summary'] = self._calculate_summary_stats(processed)
        
        return processed
    
    def _process_column_metadata(self, column_meta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process individual column metadata
        
        Args:
            column_meta: Raw column metadata
            
        Returns:
            Processed column metadata
        """
        processed = column_meta.copy()
        
        # Standardize data type
        if 'data_type' in processed:
            processed['data_type'] = self._standardize_data_type(processed['data_type'])
        
        # Calculate derived statistics
        if 'statistics' in processed:
            stats = processed['statistics']
            if 'count' in stats and 'missing_count' in stats:
                stats['non_missing_count'] = stats['count'] - stats['missing_count']
                if stats['count'] > 0:
                    stats['missing_percentage'] = (stats['missing_count'] / stats['count']) * 100
                    if 'unique_count' in stats:
                        stats['unique_percentage'] = (stats['unique_count'] / stats['count']) * 100
        
        return processed
    
    def _process_transformation_metadata(self, trans_meta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process transformation metadata
        
        Args:
            trans_meta: Raw transformation metadata
            
        Returns:
            Processed transformation metadata
        """
        processed = trans_meta.copy()
        
        # Add transformation quality assessment
        if 'before_stats' in processed and 'after_stats' in processed:
            processed['improvement_metrics'] = self._calculate_improvement_metrics(
                processed['before_stats'], processed['after_stats']
            )
        
        return processed
    
    def _standardize_data_type(self, data_type: str) -> str:
        """
        Standardize data type names
        
        Args:
            data_type: Original data type string
            
        Returns:
            Standardized data type
        """
        type_mapping = {
            'int': 'integer',
            'int64': 'integer',
            'float': 'float',
            'float64': 'float',
            'str': 'string',
            'object': 'string',
            'bool': 'boolean',
            'datetime64': 'datetime',
            'category': 'categorical'
        }
        
        return type_mapping.get(data_type.lower(), data_type)
    
    def _calculate_improvement_metrics(self, before_stats: Dict[str, Any], 
                                     after_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate improvement metrics from before/after statistics
        
        Args:
            before_stats: Statistics before transformation
            after_stats: Statistics after transformation
            
        Returns:
            Improvement metrics
        """
        metrics = {}
        
        # Missing data improvement
        if 'missing_count' in before_stats and 'missing_count' in after_stats:
            before_missing = before_stats['missing_count']
            after_missing = after_stats['missing_count']
            metrics['missing_data_reduction'] = before_missing - after_missing
            if before_missing > 0:
                metrics['missing_data_improvement_percentage'] = (
                    (before_missing - after_missing) / before_missing
                ) * 100
        
        # Data quality improvement
        if 'quality_score' in before_stats and 'quality_score' in after_stats:
            metrics['quality_improvement'] = (
                after_stats['quality_score'] - before_stats['quality_score']
            )
        
        return metrics
    
    def _calculate_summary_stats(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate summary statistics for the entire dataset
        
        Args:
            metadata: Complete metadata dictionary
            
        Returns:
            Summary statistics
        """
        summary = {}
        
        if 'columns' in metadata:
            columns = metadata['columns']
            summary['total_columns'] = len(columns)
            
            # Column type distribution
            type_distribution = {}
            for col in columns:
                data_type = col.get('data_type', 'unknown')
                type_distribution[data_type] = type_distribution.get(data_type, 0) + 1
            summary['column_type_distribution'] = type_distribution
            
            # Missing data summary
            missing_columns = [
                col for col in columns 
                if col.get('statistics', {}).get('missing_percentage', 0) > 0
            ]
            summary['columns_with_missing_data'] = len(missing_columns)
            
            # Unique columns
            unique_columns = [
                col for col in columns 
                if col.get('unique', False)
            ]
            summary['unique_columns'] = len(unique_columns)
        
        if 'transformations' in metadata:
            transformations = metadata['transformations']
            summary['total_transformations'] = len(transformations)
            
            # Transformation type distribution
            trans_distribution = {}
            for trans in transformations:
                trans_type = trans.get('transformation_type', 'unknown')
                trans_distribution[trans_type] = trans_distribution.get(trans_type, 0) + 1
            summary['transformation_type_distribution'] = trans_distribution
        
        return summary
    
    def create_metadata_template(self, df: pd.DataFrame, 
                                dataset_name: str = "untitled_dataset") -> Dict[str, Any]:
        """
        Create a metadata template from a DataFrame
        
        Args:
            df: DataFrame to create metadata for
            dataset_name: Name for the dataset
            
        Returns:
            Metadata template dictionary
        """
        columns_metadata = []
        
        for col in df.columns:
            col_meta = {
                "name": str(col),
                "display_name": str(col).replace('_', ' ').title(),
                "description": f"Column {col}",
                "data_type": self._infer_data_type(df[col]),
                "pandas_dtype": str(df[col].dtype),
                "nullable": df[col].isnull().any(),
                "unique": df[col].nunique() == len(df),
                "primary_key": False,
                "statistics": {
                    "count": len(df),
                    "missing_count": df[col].isnull().sum(),
                    "missing_percentage": (df[col].isnull().sum() / len(df)) * 100,
                    "unique_count": df[col].nunique(),
                    "unique_percentage": (df[col].nunique() / len(df)) * 100
                }
            }
            columns_metadata.append(col_meta)
        
        template = {
            "dataset_name": dataset_name,
            "description": f"Metadata for {dataset_name}",
            "source": "user_upload",
            "created_date": datetime.now().isoformat(),
            "version": "1.0.0",
            "size_info": {
                "rows": len(df),
                "columns": len(df.columns),
                "file_size_bytes": df.memory_usage(deep=True).sum()
            },
            "columns": columns_metadata,
            "transformations": []
        }
        
        return template
    
    def _infer_data_type(self, series: pd.Series) -> str:
        """
        Infer standardized data type from pandas Series
        
        Args:
            series: Pandas Series to analyze
            
        Returns:
            Standardized data type string
        """
        if pd.api.types.is_integer_dtype(series):
            return "integer"
        elif pd.api.types.is_float_dtype(series):
            return "float"
        elif pd.api.types.is_bool_dtype(series):
            return "boolean"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"
        elif pd.api.types.is_categorical_dtype(series):
            return "categorical"
        else:
            return "string"
    
    def export_metadata(self, metadata: Dict[str, Any], 
                       output_path: Union[str, Path]) -> None:
        """
        Export metadata to JSON file
        
        Args:
            metadata: Metadata dictionary to export
            output_path: Path for output JSON file
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Metadata exported to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to export metadata: {e}")
            raise MetadataExtractionError(f"Failed to export metadata: {e}")