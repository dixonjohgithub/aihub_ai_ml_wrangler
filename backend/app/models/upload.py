"""
File: upload.py

Overview:
Pydantic models for file upload and validation

Purpose:
Provides data validation and serialization for upload operations

Dependencies:
- Pydantic (data validation)
- typing (type hints)

Last Modified: 2025-08-15
Author: Claude
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class UploadStatus(str, Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

class FileType(str, Enum):
    CSV = "csv"
    JSON = "json"
    UNKNOWN = "unknown"

class ScanStatus(str, Enum):
    PENDING = "pending"
    SCANNING = "scanning"
    CLEAN = "clean"
    INFECTED = "infected"
    ERROR = "error"

class FileValidation(BaseModel):
    """File validation result"""
    model_config = ConfigDict(from_attributes=True)
    
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    file_type: FileType
    mime_type: Optional[str] = None
    size_bytes: int
    is_data_wrangler_format: bool = False

class FilePreview(BaseModel):
    """File content preview"""
    model_config = ConfigDict(from_attributes=True)
    
    name: str
    size: int
    type: str
    rows: Optional[int] = None
    columns: Optional[List[str]] = None
    sample_data: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None

class ScanResult(BaseModel):
    """Virus scan result"""
    model_config = ConfigDict(from_attributes=True)
    
    is_clean: bool
    scan_engine: str
    threats: Optional[List[str]] = None
    scan_time: datetime
    scan_duration_ms: Optional[int] = None

class UploadProgress(BaseModel):
    """Upload progress information"""
    model_config = ConfigDict(from_attributes=True)
    
    loaded: int
    total: int
    percentage: float
    speed_bps: Optional[float] = None
    eta_seconds: Optional[int] = None

class UploadFile(BaseModel):
    """Upload file information"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    original_name: str
    stored_name: str
    file_path: str
    size: int
    mime_type: Optional[str] = None
    status: UploadStatus
    upload_progress: Optional[UploadProgress] = None
    validation: Optional[FileValidation] = None
    preview: Optional[FilePreview] = None
    scan_result: Optional[ScanResult] = None
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None

class UploadRequest(BaseModel):
    """Upload request payload"""
    model_config = ConfigDict(from_attributes=True)
    
    file_id: Optional[str] = None
    validate_content: bool = True
    generate_preview: bool = True
    virus_scan: bool = True

class UploadResponse(BaseModel):
    """Upload response"""
    model_config = ConfigDict(from_attributes=True)
    
    file_id: str
    file_name: str
    file_size: int
    uploaded_at: datetime
    preview: Optional[FilePreview] = None
    validation: Optional[FileValidation] = None

class StatusResponse(BaseModel):
    """Status check response"""
    model_config = ConfigDict(from_attributes=True)
    
    file_id: str
    status: UploadStatus
    progress: Optional[UploadProgress] = None
    error: Optional[str] = None
    scan_status: Optional[ScanStatus] = None

class ApiResponse(BaseModel):
    """Generic API response wrapper"""
    model_config = ConfigDict(from_attributes=True)
    
    success: bool
    data: Optional[Union[Dict[str, Any], List[Any]]] = None
    error: Optional[str] = None
    message: Optional[str] = None

class BatchUploadRequest(BaseModel):
    """Batch upload request"""
    model_config = ConfigDict(from_attributes=True)
    
    files: List[str] = Field(description="List of file IDs to process")
    validate_content: bool = True
    generate_preview: bool = True
    virus_scan: bool = True

class BatchUploadResponse(BaseModel):
    """Batch upload response"""
    model_config = ConfigDict(from_attributes=True)
    
    results: Dict[str, UploadResponse]
    errors: Dict[str, str]
    total_files: int
    successful_uploads: int
    failed_uploads: int

class FileStats(BaseModel):
    """File statistics"""
    model_config = ConfigDict(from_attributes=True)
    
    total_files: int
    total_size: int
    by_status: Dict[UploadStatus, int]
    by_type: Dict[FileType, int]
    upload_rate_24h: Optional[float] = None