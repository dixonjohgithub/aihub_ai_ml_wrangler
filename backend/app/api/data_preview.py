"""
File: data_preview.py

Overview:
FastAPI endpoints for data preview functionality including file upload,
data parsing, validation, and statistical analysis

Purpose:
Provides REST API endpoints for frontend to interact with data processing
pipeline including chunked data preview and metadata extraction

Dependencies:
- FastAPI: Web framework for API endpoints
- pydantic: Data validation and serialization
- aiofiles: Async file operations
- pandas: Data manipulation

Last Modified: 2025-08-15
Author: Claude
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
import aiofiles
import pandas as pd
import json
import uuid
import os
from pathlib import Path
import logging

# Import our custom services
from app.services.data_parser import CSVParser, DataValidator, DataParseError
from app.services.metadata_extractor import JSONMetadataExtractor, MetadataExtractionError
from app.services.data_validation import DataValidationService
from app.ml_modules.type_detection import ColumnTypeDetector
from app.ml_modules.missing_data_analysis import MissingDataAnalyzer

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/data", tags=["data-preview"])

# Pydantic models for request/response
class DataUploadResponse(BaseModel):
    """Response model for data upload"""
    file_id: str
    filename: str
    file_size: int
    upload_status: str
    message: str

class DataPreviewRequest(BaseModel):
    """Request model for data preview"""
    file_id: str
    start_row: Optional[int] = 0
    limit: Optional[int] = 100
    columns: Optional[List[str]] = None

class DataPreviewResponse(BaseModel):
    """Response model for data preview"""
    file_id: str
    preview_data: List[Dict[str, Any]]
    total_rows: int
    total_columns: int
    columns: List[str]
    data_types: Dict[str, str]
    preview_range: Dict[str, int]

class ValidationRequest(BaseModel):
    """Request model for data validation"""
    file_id: str
    validation_config: Optional[Dict[str, Any]] = {}

class TypeDetectionRequest(BaseModel):
    """Request model for type detection"""
    file_id: str
    sample_size: Optional[int] = 1000

class MissingDataAnalysisRequest(BaseModel):
    """Request model for missing data analysis"""
    file_id: str

# Global storage for uploaded files (in production, use proper storage)
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# In-memory storage for processed data (in production, use Redis/database)
data_cache = {}

# Initialize services
csv_parser = CSVParser()
metadata_extractor = JSONMetadataExtractor()
validation_service = DataValidationService()
type_detector = ColumnTypeDetector()
missing_analyzer = MissingDataAnalyzer()

@router.post("/upload", response_model=DataUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a data file for processing
    
    Args:
        file: Uploaded file (CSV or JSON)
        
    Returns:
        Upload response with file ID
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.csv', '.json')):
            raise HTTPException(
                status_code=400,
                detail="Only CSV and JSON files are supported"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Save uploaded file
        file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        file_size = len(content)
        
        # Store file info in cache
        data_cache[file_id] = {
            "filename": file.filename,
            "file_path": str(file_path),
            "file_size": file_size,
            "file_type": "csv" if file.filename.lower().endswith('.csv') else "json",
            "upload_timestamp": pd.Timestamp.now().isoformat()
        }
        
        logger.info(f"File uploaded successfully: {file.filename} ({file_size} bytes)")
        
        return DataUploadResponse(
            file_id=file_id,
            filename=file.filename,
            file_size=file_size,
            upload_status="success",
            message="File uploaded successfully"
        )
        
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/preview", response_model=DataPreviewResponse)
async def get_data_preview(request: DataPreviewRequest):
    """
    Get a preview of uploaded data
    
    Args:
        request: Data preview request
        
    Returns:
        Data preview response
    """
    try:
        # Validate file ID
        if request.file_id not in data_cache:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_info = data_cache[request.file_id]
        file_path = file_info["file_path"]
        
        # Parse data based on file type
        if file_info["file_type"] == "csv":
            # Get sample info first
            sample_info = await csv_parser.parse_csv_sample(file_path)
            
            # Parse full data
            df = await csv_parser.parse_csv_full(file_path)
            
            # Apply column filter if specified
            if request.columns:
                available_columns = [col for col in request.columns if col in df.columns]
                if available_columns:
                    df = df[available_columns]
            
            # Apply row slicing
            start_row = request.start_row or 0
            limit = request.limit or 100
            end_row = start_row + limit
            
            preview_df = df.iloc[start_row:end_row]
            
            return DataPreviewResponse(
                file_id=request.file_id,
                preview_data=preview_df.to_dict('records'),
                total_rows=len(df),
                total_columns=len(df.columns),
                columns=df.columns.tolist(),
                data_types={col: str(dtype) for col, dtype in df.dtypes.items()},
                preview_range={
                    "start_row": start_row,
                    "end_row": min(end_row, len(df)),
                    "limit": limit
                }
            )
        
        elif file_info["file_type"] == "json":
            # Extract metadata from JSON
            metadata = await metadata_extractor.extract_metadata_from_file(file_path)
            
            # Convert metadata to preview format
            return DataPreviewResponse(
                file_id=request.file_id,
                preview_data=[metadata],  # JSON metadata as single record
                total_rows=1,
                total_columns=len(metadata.keys()),
                columns=list(metadata.keys()),
                data_types={key: type(value).__name__ for key, value in metadata.items()},
                preview_range={"start_row": 0, "end_row": 1, "limit": 1}
            )
        
    except DataParseError as e:
        logger.error(f"Data parsing failed: {e}")
        raise HTTPException(status_code=400, detail=f"Data parsing failed: {str(e)}")
    except Exception as e:
        logger.error(f"Data preview failed: {e}")
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")

@router.post("/validate")
async def validate_data(request: ValidationRequest):
    """
    Validate uploaded data for quality issues
    
    Args:
        request: Validation request
        
    Returns:
        Validation report
    """
    try:
        # Validate file ID
        if request.file_id not in data_cache:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_info = data_cache[request.file_id]
        file_path = file_info["file_path"]
        
        if file_info["file_type"] != "csv":
            raise HTTPException(status_code=400, detail="Validation only supported for CSV files")
        
        # Parse data
        df = await csv_parser.parse_csv_full(file_path)
        
        # Perform validation
        validation_report = validation_service.validate_dataset(df)
        
        # Store validation results in cache
        data_cache[request.file_id]["validation_report"] = validation_report
        
        logger.info(f"Data validation completed for file {request.file_id}")
        
        return JSONResponse(content=validation_report)
        
    except Exception as e:
        logger.error(f"Data validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@router.post("/detect-types")
async def detect_column_types(request: TypeDetectionRequest):
    """
    Detect column data types using advanced algorithm
    
    Args:
        request: Type detection request
        
    Returns:
        Type detection results
    """
    try:
        # Validate file ID
        if request.file_id not in data_cache:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_info = data_cache[request.file_id]
        file_path = file_info["file_path"]
        
        if file_info["file_type"] != "csv":
            raise HTTPException(status_code=400, detail="Type detection only supported for CSV files")
        
        # Parse data
        df = await csv_parser.parse_csv_full(file_path)
        
        # Initialize type detector with custom sample size
        detector = ColumnTypeDetector(sample_size=request.sample_size or 1000)
        
        # Detect types
        detection_results = detector.detect_column_types(df)
        
        # Generate report
        type_report = detector.generate_type_report(detection_results)
        
        # Convert results to serializable format
        serializable_results = {}
        for column, result in detection_results.items():
            serializable_results[column] = {
                "detected_type": result.detected_type.value,
                "confidence": result.confidence,
                "pandas_dtype": result.pandas_dtype,
                "suggested_dtype": result.suggested_dtype,
                "metadata": result.metadata,
                "issues": result.issues
            }
        
        response = {
            "file_id": request.file_id,
            "detection_results": serializable_results,
            "type_report": type_report
        }
        
        # Store results in cache
        data_cache[request.file_id]["type_detection"] = response
        
        logger.info(f"Type detection completed for file {request.file_id}")
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Type detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Type detection failed: {str(e)}")

@router.post("/analyze-missing")
async def analyze_missing_data(request: MissingDataAnalysisRequest):
    """
    Analyze missing data patterns and mechanisms
    
    Args:
        request: Missing data analysis request
        
    Returns:
        Missing data analysis report
    """
    try:
        # Validate file ID
        if request.file_id not in data_cache:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_info = data_cache[request.file_id]
        file_path = file_info["file_path"]
        
        if file_info["file_type"] != "csv":
            raise HTTPException(status_code=400, detail="Missing data analysis only supported for CSV files")
        
        # Parse data
        df = await csv_parser.parse_csv_full(file_path)
        
        # Analyze missing patterns
        missing_analysis = missing_analyzer.analyze_missing_patterns(df)
        
        # Convert insights to serializable format
        serializable_insights = []
        for insight in missing_analysis["insights"]:
            serializable_insights.append({
                "pattern_type": insight.pattern_type.value,
                "mechanism": insight.mechanism.value,
                "description": insight.description,
                "affected_columns": insight.affected_columns,
                "severity": insight.severity,
                "confidence": insight.confidence,
                "suggested_actions": insight.suggested_actions
            })
        
        missing_analysis["insights"] = serializable_insights
        
        # Convert mechanism enum to string
        overall_mechanism = missing_analysis["mechanism_analysis"]["overall_mechanism"]
        overall_mechanism["likely_mechanism"] = overall_mechanism["likely_mechanism"].value
        
        response = {
            "file_id": request.file_id,
            "missing_analysis": missing_analysis
        }
        
        # Store results in cache
        data_cache[request.file_id]["missing_analysis"] = response
        
        logger.info(f"Missing data analysis completed for file {request.file_id}")
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Missing data analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Missing data analysis failed: {str(e)}")

@router.get("/file-info/{file_id}")
async def get_file_info(file_id: str):
    """
    Get information about uploaded file
    
    Args:
        file_id: File identifier
        
    Returns:
        File information
    """
    try:
        if file_id not in data_cache:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_info = data_cache[file_id].copy()
        
        # Remove file path from response for security
        file_info.pop("file_path", None)
        
        return JSONResponse(content=file_info)
        
    except Exception as e:
        logger.error(f"Failed to get file info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get file info: {str(e)}")

@router.get("/columns/{file_id}")
async def get_column_info(file_id: str):
    """
    Get detailed column information for a file
    
    Args:
        file_id: File identifier
        
    Returns:
        Column information
    """
    try:
        if file_id not in data_cache:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_info = data_cache[file_id]
        file_path = file_info["file_path"]
        
        if file_info["file_type"] != "csv":
            raise HTTPException(status_code=400, detail="Column info only available for CSV files")
        
        # Get sample info
        sample_info = await csv_parser.parse_csv_sample(file_path)
        
        return JSONResponse(content={
            "file_id": file_id,
            "columns": sample_info["columns"],
            "dtypes": sample_info["dtypes"],
            "sample_shape": sample_info["sample_shape"]
        })
        
    except Exception as e:
        logger.error(f"Failed to get column info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get column info: {str(e)}")

@router.delete("/file/{file_id}")
async def delete_file(file_id: str):
    """
    Delete uploaded file and associated data
    
    Args:
        file_id: File identifier
        
    Returns:
        Deletion confirmation
    """
    try:
        if file_id not in data_cache:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_info = data_cache[file_id]
        file_path = Path(file_info["file_path"])
        
        # Delete physical file
        if file_path.exists():
            file_path.unlink()
        
        # Remove from cache
        del data_cache[file_id]
        
        logger.info(f"File deleted successfully: {file_id}")
        
        return JSONResponse(content={
            "file_id": file_id,
            "status": "deleted",
            "message": "File and associated data deleted successfully"
        })
        
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint for data preview service
    
    Returns:
        Health status
    """
    return JSONResponse(content={
        "status": "healthy",
        "service": "data-preview",
        "cached_files": len(data_cache),
        "upload_directory": str(UPLOAD_DIR),
        "upload_directory_exists": UPLOAD_DIR.exists()
    })