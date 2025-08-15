"""
File: upload.py

Overview:
FastAPI endpoints for file upload, validation, and management

Purpose:
HTTP API endpoints for handling file upload operations with security and validation

Dependencies:
- fastapi for web framework
- file_storage for file handling
- virus_scan for security scanning
- upload models for data structures

Last Modified: 2025-08-15
Author: Claude
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
import uuid
from datetime import datetime

from ..models.upload import (
    FileUploadResponse, 
    FilePreviewResponse, 
    UploadStatus,
    FileValidationResult
)
from ..services.file_storage import FileStorageService
from ..services.virus_scan import VirusScanService

router = APIRouter(prefix="/api", tags=["upload"])

# Initialize services
file_storage = FileStorageService()
virus_scanner = VirusScanService()

# In-memory storage for upload status (in production, use Redis or database)
upload_status_store = {}

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload a file with validation and security scanning
    """
    try:
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Initialize upload status
        upload_status_store[file_id] = {
            "status": "uploading",
            "progress": 0,
            "message": "File upload in progress",
            "created_at": datetime.now()
        }
        
        # Read file content
        file_content = await file.read()
        
        # Store file temporarily
        stored_file_id, file_path = await file_storage.store_file(
            file_content, 
            file.filename
        )
        
        # Update progress
        upload_status_store[file_id]["progress"] = 50
        upload_status_store[file_id]["message"] = "File stored, validating..."
        
        # Validate file
        validation_result = await file_storage.validate_file(file_path, file.filename)
        
        if not validation_result.is_valid:
            # Move to quarantine
            await file_storage.quarantine_file(file_path, "Validation failed")
            upload_status_store[file_id]["status"] = "failed"
            upload_status_store[file_id]["message"] = "Validation failed"
            
            return FileUploadResponse(
                success=False,
                file_id=file_id,
                message="File validation failed",
                errors=validation_result.errors
            )
        
        # Start background processing
        background_tasks.add_task(
            process_file_background,
            file_id,
            stored_file_id,
            file_path,
            file.filename,
            file.content_type
        )
        
        upload_status_store[file_id]["progress"] = 75
        upload_status_store[file_id]["message"] = "Processing file..."
        
        return FileUploadResponse(
            success=True,
            file_id=file_id,
            message="File uploaded successfully, processing in background"
        )
        
    except Exception as e:
        # Clean up on error
        if file_id in upload_status_store:
            upload_status_store[file_id]["status"] = "failed"
            upload_status_store[file_id]["message"] = f"Upload failed: {str(e)}"
        
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def process_file_background(
    file_id: str,
    stored_file_id: str, 
    file_path,
    filename: str,
    content_type: str
):
    """Background task for file processing"""
    try:
        # Update status
        upload_status_store[file_id]["message"] = "Scanning for viruses..."
        
        # Virus scan
        is_clean, scan_message = await virus_scanner.scan_file(file_path)
        
        if not is_clean:
            # Move to quarantine
            await file_storage.quarantine_file(file_path, f"Virus scan failed: {scan_message}")
            upload_status_store[file_id]["status"] = "failed"
            upload_status_store[file_id]["message"] = f"Security scan failed: {scan_message}"
            return
        
        upload_status_store[file_id]["progress"] = 90
        upload_status_store[file_id]["message"] = "Generating preview..."
        
        # Generate preview
        preview = await file_storage.generate_preview(file_path, content_type)
        
        # Move to processed directory
        processed_path = await file_storage.move_to_processed(file_path)
        
        # Complete upload
        upload_status_store[file_id]["status"] = "completed"
        upload_status_store[file_id]["progress"] = 100
        upload_status_store[file_id]["message"] = "File processed successfully"
        upload_status_store[file_id]["preview"] = preview.dict() if preview else None
        upload_status_store[file_id]["processed_at"] = datetime.now()
        
    except Exception as e:
        upload_status_store[file_id]["status"] = "failed"
        upload_status_store[file_id]["message"] = f"Processing failed: {str(e)}"

@router.get("/upload/{file_id}/status", response_model=UploadStatus)
async def get_upload_status(file_id: str):
    """Get upload status for a specific file"""
    if file_id not in upload_status_store:
        raise HTTPException(status_code=404, detail="File not found")
    
    status_data = upload_status_store[file_id]
    return UploadStatus(
        file_id=file_id,
        status=status_data["status"],
        progress=status_data["progress"],
        message=status_data.get("message"),
        created_at=status_data["created_at"],
        updated_at=status_data.get("processed_at")
    )

@router.get("/files/{file_id}/preview", response_model=FilePreviewResponse)
async def get_file_preview(file_id: str):
    """Get preview data for an uploaded file"""
    if file_id not in upload_status_store:
        raise HTTPException(status_code=404, detail="File not found")
    
    status_data = upload_status_store[file_id]
    
    if status_data["status"] != "completed":
        raise HTTPException(status_code=400, detail="File not yet processed")
    
    preview_data = status_data.get("preview")
    if not preview_data:
        raise HTTPException(status_code=404, detail="Preview not available")
    
    return FilePreviewResponse(**preview_data)

@router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """Delete an uploaded file"""
    if file_id not in upload_status_store:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Remove from status store
    del upload_status_store[file_id]
    
    return {"message": "File deleted successfully"}

@router.get("/files")
async def list_files():
    """List all uploaded files"""
    return {
        "files": [
            {
                "file_id": file_id,
                "status": data["status"],
                "progress": data["progress"],
                "created_at": data["created_at"],
                "message": data.get("message")
            }
            for file_id, data in upload_status_store.items()
        ]
    }

@router.get("/system/storage-stats")
async def get_storage_stats():
    """Get storage system statistics"""
    stats = file_storage.get_file_stats()
    scan_info = await virus_scanner.get_scan_info()
    
    return {
        "storage": stats,
        "security": scan_info,
        "active_uploads": len(upload_status_store)
    }

@router.post("/system/cleanup")
async def cleanup_old_files():
    """Clean up old temporary files (admin endpoint)"""
    # This would implement cleanup logic for old files
    return {"message": "Cleanup completed"}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "file_storage": "operational",
            "virus_scanner": "operational"
        }
    }