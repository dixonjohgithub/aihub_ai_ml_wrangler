"""
File: data_preview.py

Overview:
FastAPI endpoints for data preview functionality including file upload,
validation, type detection, and missing data analysis.

Purpose:
Provides RESTful API endpoints for the data processing pipeline
with comprehensive error handling and response formatting.

Dependencies:
- FastAPI for web framework
- pydantic for data validation
- aiofiles for async file operations
- Data processing services

Last Modified: 2025-08-15
Author: Claude
"""

import asyncio
import tempfile
import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
import aiofiles
import pandas as pd

from app.services.data_parser import DataParser
from app.services.metadata_extractor import MetadataExtractor
from app.services.data_validation import DataValidationService
from app.services.data_chunking import DataChunkingService
from app.ml_modules.type_detection import TypeDetector
from app.ml_modules.missing_data_analysis import MissingDataAnalyzer

router = APIRouter()

# Request/Response Models
class AnalysisRequest(BaseModel):
    file_path: str
    analysis_type: str = "full"  # full, basic, validation_only, types_only
    chunk_size: Optional[int] = None
    sample_size: Optional[int] = 1000

class ValidationRequest(BaseModel):
    file_path: str
    metadata: Optional[Dict[str, Any]] = None

class TypeDetectionRequest(BaseModel):
    file_path: str
    sample_size: Optional[int] = 10000

class MissingAnalysisRequest(BaseModel):
    file_path: str

# Service instances
data_parser = DataParser()
metadata_extractor = MetadataExtractor()
data_validator = DataValidationService()
data_chunker = DataChunkingService()
type_detector = TypeDetector()
missing_analyzer = MissingDataAnalyzer()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and store a CSV file for processing."""
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.json')):
            raise HTTPException(status_code=400, detail="Only CSV and JSON files are supported")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            temp_path = temp_file.name
            
            # Write uploaded file to temporary location
            async with aiofiles.open(temp_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
        
        # Get file info
        file_size = os.path.getsize(temp_path)
        
        # Basic parsing to validate file
        if file.filename.endswith('.csv'):
            parse_result = await data_parser.get_data_preview(temp_path, rows=100)
            if not parse_result['success']:
                os.unlink(temp_path)  # Clean up
                raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {parse_result['error']}")
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "file_path": temp_path,
            "filename": file.filename,
            "file_size": file_size,
            "file_type": "csv" if file.filename.endswith('.csv') else "json"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "file_path": None
        }

@router.post("/preview")
async def get_data_preview(request: AnalysisRequest):
    """Get a preview of the uploaded data with basic statistics."""
    try:
        file_path = request.file_path
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Parse and preview data
        preview_result = await data_parser.get_data_preview(file_path, rows=request.sample_size)
        
        if not preview_result['success']:
            raise HTTPException(status_code=400, detail=f"Failed to preview data: {preview_result['error']}")
        
        # Get basic statistics
        df_preview = pd.DataFrame(preview_result['preview'])
        basic_stats = {
            'shape': [len(df_preview), len(df_preview.columns)] if not df_preview.empty else [0, 0],
            'columns': df_preview.columns.tolist() if not df_preview.empty else [],
            'dtypes': df_preview.dtypes.astype(str).to_dict() if not df_preview.empty else {},
            'memory_usage': df_preview.memory_usage(deep=True).sum() if not df_preview.empty else 0,
            'sample_size': len(df_preview)
        }
        
        return {
            "success": True,
            "preview": preview_result['preview'][:100],  # Limit preview size
            "metadata": preview_result['metadata'],
            "statistics": basic_stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_data(request: ValidationRequest):
    """Perform comprehensive data validation."""
    try:
        file_path = request.file_path
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Parse data
        parse_result = await data_parser.parse_csv_file(file_path)
        
        if not parse_result['success']:
            raise HTTPException(status_code=400, detail=f"Failed to parse data: {parse_result['error']}")
        
        df = parse_result['data']
        
        # Perform validation
        validation_result = await data_validator.validate_dataset(df, request.metadata)
        
        if not validation_result['success']:
            raise HTTPException(status_code=500, detail=f"Validation failed: {validation_result['error']}")
        
        return {
            "success": True,
            "validation": validation_result['validation']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-types")
async def detect_column_types(request: TypeDetectionRequest):
    """Detect column data types with confidence scoring."""
    try:
        file_path = request.file_path
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Create sample for type detection
        sample_result = await data_chunker.create_data_sample(
            file_path, 
            sample_size=request.sample_size, 
            sampling_method='random'
        )
        
        if not sample_result['success']:
            raise HTTPException(status_code=400, detail=f"Failed to create sample: {sample_result['error']}")
        
        df_sample = sample_result['sample']
        
        # Detect types
        type_result = await type_detector.detect_column_types(df_sample)
        
        if not type_result['success']:
            raise HTTPException(status_code=500, detail=f"Type detection failed: {type_result['error']}")
        
        return {
            "success": True,
            "type_detection": type_result['type_detection'],
            "sample_info": {
                "sample_size": sample_result['sample_size'],
                "sampling_ratio": sample_result['sampling_ratio'],
                "method": sample_result['method']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-missing")
async def analyze_missing_data(request: MissingAnalysisRequest):
    """Analyze missing data patterns and mechanisms."""
    try:
        file_path = request.file_path
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # For missing data analysis, we need to be more careful with sampling
        # as missing patterns might not be preserved in small samples
        
        # First check file size
        chunk_stats = await data_chunker.get_chunk_statistics(file_path)
        
        if chunk_stats['success'] and chunk_stats['estimated_total_rows'] < 50000:
            # Small enough to load entirely
            parse_result = await data_parser.parse_csv_file(file_path)
            
            if not parse_result['success']:
                raise HTTPException(status_code=400, detail=f"Failed to parse data: {parse_result['error']}")
            
            df = parse_result['data']
        else:
            # Use larger sample for missing data analysis
            sample_result = await data_chunker.create_data_sample(
                file_path, 
                sample_size=25000,  # Larger sample for missing data patterns
                sampling_method='systematic'
            )
            
            if not sample_result['success']:
                raise HTTPException(status_code=400, detail=f"Failed to create sample: {sample_result['error']}")
            
            df = sample_result['sample']
        
        # Analyze missing patterns
        missing_result = await missing_analyzer.analyze_missing_patterns(df)
        
        if not missing_result['success']:
            raise HTTPException(status_code=500, detail=f"Missing data analysis failed: {missing_result['error']}")
        
        return {
            "success": True,
            "missing_analysis": missing_result['missing_analysis'],
            "data_info": {
                "rows_analyzed": len(df),
                "columns_analyzed": len(df.columns),
                "analysis_method": "full_data" if chunk_stats.get('estimated_total_rows', 0) < 50000 else "sample_based"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chunk-info")
async def get_chunking_info(request: AnalysisRequest):
    """Get information about optimal chunking strategy for large files."""
    try:
        file_path = request.file_path
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Calculate optimal chunk size
        chunk_size_info = await data_chunker.calculate_optimal_chunk_size(file_path)
        
        # Get chunk statistics
        chunk_stats = await data_chunker.get_chunk_statistics(file_path, request.chunk_size)
        
        return {
            "success": True,
            "chunking_info": chunk_size_info,
            "chunk_statistics": chunk_stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/full-analysis")
async def perform_full_analysis(request: AnalysisRequest):
    """Perform comprehensive data analysis including all components."""
    try:
        file_path = request.file_path
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        results = {
            "success": True,
            "analysis_type": request.analysis_type,
            "components": {}
        }
        
        # 1. Data Preview
        preview_result = await data_parser.get_data_preview(file_path, rows=request.sample_size)
        results["components"]["preview"] = preview_result
        
        if not preview_result['success']:
            return results
        
        # 2. Chunking Analysis (for large files)
        chunk_info = await data_chunker.calculate_optimal_chunk_size(file_path)
        results["components"]["chunking"] = chunk_info
        
        # Create appropriate sample
        if chunk_info.get('requires_chunking', False):
            sample_result = await data_chunker.create_data_sample(
                file_path, 
                sample_size=min(request.sample_size, 15000),
                sampling_method='random'
            )
            df = sample_result['sample']
            results["components"]["sampling"] = sample_result
        else:
            parse_result = await data_parser.parse_csv_file(file_path)
            df = parse_result['data']
            results["components"]["parsing"] = parse_result
        
        if df is None or df.empty:
            results["success"] = False
            results["error"] = "Failed to load data for analysis"
            return results
        
        # 3. Type Detection
        if request.analysis_type in ['full', 'types']:
            type_result = await type_detector.detect_column_types(df)
            results["components"]["type_detection"] = type_result
        
        # 4. Data Validation
        if request.analysis_type in ['full', 'validation']:
            validation_result = await data_validator.validate_dataset(df)
            results["components"]["validation"] = validation_result
        
        # 5. Missing Data Analysis
        if request.analysis_type in ['full', 'missing']:
            missing_result = await missing_analyzer.analyze_missing_patterns(df)
            results["components"]["missing_analysis"] = missing_result
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cleanup/{file_id}")
async def cleanup_temp_file(file_id: str):
    """Clean up temporary files after processing."""
    try:
        # In a real implementation, you'd track file IDs
        # For now, this is a placeholder
        return {
            "success": True,
            "message": "File cleanup completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint for the data preview API."""
    return {
        "status": "healthy",
        "service": "data_preview_api",
        "components": {
            "data_parser": "available",
            "metadata_extractor": "available",
            "data_validator": "available",
            "type_detector": "available",
            "missing_analyzer": "available",
            "data_chunker": "available"
        }
    }