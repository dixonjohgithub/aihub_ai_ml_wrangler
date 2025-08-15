"""
File: metadata_extractor.py

Overview:
Metadata extraction service for JSON files with schema validation
and comprehensive data lineage tracking.

Purpose:
Extracts and validates metadata from JSON files, providing structured
information about datasets for the processing pipeline.

Dependencies:
- json for JSON parsing
- jsonschema for validation
- datetime for timestamp handling
- typing for type hints

Last Modified: 2025-08-15
Author: Claude
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path
import jsonschema
from jsonschema import validate, ValidationError

class MetadataExtractor:
    """Extract and validate metadata from JSON files."""
    
    def __init__(self):
        self.metadata_schema = {
            "type": "object",
            "properties": {
                "dataset": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "version": {"type": "string"},
                        "created_at": {"type": "string"},
                        "source": {"type": "string"}
                    }
                },
                "columns": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "description": {"type": "string"},
                            "nullable": {"type": "boolean"},
                            "unique": {"type": "boolean"}
                        }
                    }
                },
                "processing": {
                    "type": "object",
                    "properties": {
                        "transformations": {"type": "array"},
                        "quality_checks": {"type": "array"},
                        "imputation_methods": {"type": "array"}
                    }
                }
            }
        }
    
    async def extract_from_file(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Validate against schema
            validation_result = await self.validate_metadata(metadata)
            
            # Extract standard metadata fields
            extracted = await self.extract_standard_fields(metadata)
            
            # Generate processing metadata
            processing_meta = await self.generate_processing_metadata(metadata)
            
            return {
                'success': True,
                'metadata': extracted,
                'processing': processing_meta,
                'validation': validation_result,
                'raw': metadata
            }
            
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f"Invalid JSON format: {str(e)}",
                'metadata': None,
                'processing': None,
                'validation': None,
                'raw': None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'metadata': None,
                'processing': None,
                'validation': None,
                'raw': None
            }
    
    async def validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metadata against schema."""
        try:
            validate(instance=metadata, schema=self.metadata_schema)
            return {
                'valid': True,
                'errors': [],
                'warnings': []
            }
        except ValidationError as e:
            return {
                'valid': False,
                'errors': [str(e)],
                'warnings': []
            }
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Validation failed: {str(e)}"],
                'warnings': []
            }
    
    async def extract_standard_fields(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract standard metadata fields with defaults."""
        dataset_info = metadata.get('dataset', {})
        columns_info = metadata.get('columns', [])
        
        # Extract dataset information
        extracted = {
            'name': dataset_info.get('name', 'Unknown Dataset'),
            'description': dataset_info.get('description', ''),
            'version': dataset_info.get('version', '1.0.0'),
            'created_at': dataset_info.get('created_at', datetime.now().isoformat()),
            'source': dataset_info.get('source', 'Unknown'),
            'columns': [],
            'column_count': len(columns_info),
            'tags': metadata.get('tags', []),
            'license': metadata.get('license', ''),
            'author': metadata.get('author', '')
        }
        
        # Process column information
        for col in columns_info:
            extracted_col = {
                'name': col.get('name', ''),
                'data_type': col.get('type', 'unknown'),
                'description': col.get('description', ''),
                'nullable': col.get('nullable', True),
                'unique': col.get('unique', False),
                'constraints': col.get('constraints', []),
                'default_value': col.get('default', None),
                'format': col.get('format', ''),
                'examples': col.get('examples', [])
            }
            extracted['columns'].append(extracted_col)
        
        return extracted
    
    async def generate_processing_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate processing-specific metadata."""
        processing = metadata.get('processing', {})
        
        return {
            'transformations_applied': processing.get('transformations', []),
            'quality_checks': processing.get('quality_checks', []),
            'imputation_methods': processing.get('imputation_methods', []),
            'last_processed': datetime.now().isoformat(),
            'processing_status': 'pending',
            'data_lineage': await self.extract_lineage(metadata),
            'quality_score': await self.calculate_quality_score(metadata),
            'completeness': await self.calculate_completeness(metadata)
        }
    
    async def extract_lineage(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract data lineage information."""
        lineage = metadata.get('lineage', [])
        extracted_lineage = []
        
        for item in lineage:
            if isinstance(item, dict):
                extracted_lineage.append({
                    'source': item.get('source', ''),
                    'transformation': item.get('transformation', ''),
                    'timestamp': item.get('timestamp', datetime.now().isoformat()),
                    'tool': item.get('tool', ''),
                    'version': item.get('version', '')
                })
        
        return extracted_lineage
    
    async def calculate_quality_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate a quality score based on metadata completeness."""
        score = 0.0
        total_checks = 10
        
        # Check dataset information completeness
        dataset = metadata.get('dataset', {})
        if dataset.get('name'): score += 1
        if dataset.get('description'): score += 1
        if dataset.get('version'): score += 1
        if dataset.get('source'): score += 1
        
        # Check column information
        columns = metadata.get('columns', [])
        if columns:
            score += 2
            # Check column details
            complete_columns = sum(1 for col in columns 
                                 if col.get('name') and col.get('type'))
            if complete_columns == len(columns):
                score += 1
        
        # Check processing information
        processing = metadata.get('processing', {})
        if processing.get('transformations'): score += 1
        if processing.get('quality_checks'): score += 1
        
        # Check additional metadata
        if metadata.get('tags'): score += 0.5
        if metadata.get('license'): score += 0.5
        
        return round((score / total_checks) * 100, 2)
    
    async def calculate_completeness(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metadata completeness statistics."""
        columns = metadata.get('columns', [])
        
        if not columns:
            return {
                'overall': 0.0,
                'columns_with_descriptions': 0,
                'columns_with_types': 0,
                'total_columns': 0
            }
        
        columns_with_descriptions = sum(1 for col in columns if col.get('description'))
        columns_with_types = sum(1 for col in columns if col.get('type'))
        total_columns = len(columns)
        
        overall_completeness = (
            (columns_with_descriptions + columns_with_types) / (total_columns * 2)
        ) * 100 if total_columns > 0 else 0
        
        return {
            'overall': round(overall_completeness, 2),
            'columns_with_descriptions': columns_with_descriptions,
            'columns_with_types': columns_with_types,
            'total_columns': total_columns,
            'description_completeness': round((columns_with_descriptions / total_columns) * 100, 2) if total_columns > 0 else 0,
            'type_completeness': round((columns_with_types / total_columns) * 100, 2) if total_columns > 0 else 0
        }
    
    async def create_metadata_template(self, dataset_name: str, columns: List[str]) -> Dict[str, Any]:
        """Create a metadata template for a dataset."""
        template = {
            "dataset": {
                "name": dataset_name,
                "description": f"Metadata for {dataset_name}",
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "source": "Generated template"
            },
            "columns": [
                {
                    "name": col,
                    "type": "unknown",
                    "description": f"Description for {col}",
                    "nullable": True,
                    "unique": False
                }
                for col in columns
            ],
            "processing": {
                "transformations": [],
                "quality_checks": [],
                "imputation_methods": []
            },
            "tags": [],
            "license": "",
            "author": ""
        }
        
        return template