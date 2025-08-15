"""
File: upload.py

Overview:
FastAPI router for file upload endpoints

Purpose:
Provides RESTful API endpoints for file upload, validation, and management

Dependencies:
- FastAPI (web framework)
- file_storage service (file operations)
- virus_scan service (security scanning)

Last Modified: 2025-08-15
Author: Claude
"""

from fastapi import APIRouter, UploadFile as FastAPIUploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional, List
import logging
import uuid
from datetime import datetime

from ..models.upload import (
    ApiResponse, UploadResponse, StatusResponse, ScanResult,
    UploadRequest, FileValidation, FilePreview, UploadStatus
)
from ..services.file_storage import file_storage_service
from ..services.virus_scan import virus_scan_service

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for upload tracking (in production, use a database)
upload_registry = {}

@router.post("/upload", response_model=ApiResponse[UploadResponse])
async def upload_file(
    background_tasks: BackgroundTasks,
    file: FastAPIUploadFile,
    file_id: Optional[str] = Form(None),
    validate_content: bool = Form(True),
    generate_preview: bool = Form(True),
    virus_scan: bool = Form(True)
):
    """Upload a file with validation and optional preview generation"""
    
    if not file_id:
        file_id = str(uuid.uuid4())
    
    try:
        # Read file content
        content = await file.read()
        
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Save to temporary storage
        upload_file = await file_storage_service.save_uploaded_file(
            content, file.filename or "unknown", file_id
        )
        
        # Update status
        upload_file.status = UploadStatus.UPLOADING
        upload_registry[file_id] = upload_file
        
        # Validate file
        if validate_content:
            validation = await file_storage_service.validate_file(upload_file)
            upload_file.validation = validation
            
            if not validation.is_valid:
                upload_file.status = UploadStatus.ERROR
                upload_file.error_message = "; ".join(validation.errors)
                upload_registry[file_id] = upload_file
                
                return ApiResponse(
                    success=False,
                    error=f"File validation failed: {upload_file.error_message}"
                )
        
        # Generate preview
        preview = None
        if generate_preview:
            try:
                preview = await file_storage_service.generate_preview(upload_file)
                upload_file.preview = preview
            except Exception as e:
                logger.warning(f"Could not generate preview for {file_id}: {e}")
        
        # Move to permanent storage
        permanent_path = await file_storage_service.move_to_permanent_storage(upload_file)
        upload_file.file_path = permanent_path
        upload_file.status = UploadStatus.COMPLETED
        upload_file.updated_at = datetime.utcnow()
        
        # Schedule virus scan in background
        if virus_scan:
            background_tasks.add_task(scan_file_background, file_id)
        
        upload_registry[file_id] = upload_file
        
        # Prepare response
        response_data = UploadResponse(
            file_id=file_id,
            file_name=upload_file.original_name,
            file_size=upload_file.size,
            uploaded_at=upload_file.created_at,
            preview=preview,
            validation=upload_file.validation
        )
        
        logger.info(f"File uploaded successfully: {file_id}")
        
        return ApiResponse(
            success=True,
            data=response_data.model_dump(),
            message="File uploaded successfully"
        )
        
    except Exception as e:
        logger.error(f"Error uploading file {file_id}: {e}")
        
        # Update status on error
        if file_id in upload_registry:
            upload_registry[file_id].status = UploadStatus.ERROR
            upload_registry[file_id].error_message = str(e)
        
        return ApiResponse(
            success=False,
            error=f"Upload failed: {str(e)}"
        )

@router.get("/upload/{file_id}/status", response_model=ApiResponse[StatusResponse])
async def get_upload_status(file_id: str):
    """Get upload status for a specific file"""
    
    if file_id not in upload_registry:
        raise HTTPException(status_code=404, detail="File not found")
    
    upload_file = upload_registry[file_id]
    
    status_response = StatusResponse(
        file_id=file_id,
        status=upload_file.status,
        error=upload_file.error_message
    )
    
    return ApiResponse(
        success=True,
        data=status_response.model_dump()
    )

@router.post("/upload/{file_id}/scan", response_model=ApiResponse[ScanResult])
async def scan_file(file_id: str):
    """Manually trigger virus scan for uploaded file"""
    
    if file_id not in upload_registry:
        raise HTTPException(status_code=404, detail="File not found")
    
    upload_file = upload_registry[file_id]
    
    if upload_file.status != UploadStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="File not ready for scanning")
    
    try:
        scan_result = await virus_scan_service.scan_file(upload_file.file_path)
        upload_file.scan_result = scan_result
        upload_file.updated_at = datetime.utcnow()
        
        # Quarantine if infected
        if not scan_result.is_clean:
            quarantine_path = await file_storage_service.quarantine_file(
                upload_file, 
                f"Virus scan failed: {'; '.join(scan_result.threats or [])}"
            )
            upload_file.file_path = quarantine_path
            upload_file.status = UploadStatus.ERROR
            upload_file.error_message = "File quarantined due to security scan failure"
        
        upload_registry[file_id] = upload_file
        
        return ApiResponse(
            success=True,
            data=scan_result.model_dump(),
            message="Scan completed"
        )
        
    except Exception as e:
        logger.error(f"Error scanning file {file_id}: {e}")
        return ApiResponse(
            success=False,
            error=f"Scan failed: {str(e)}"
        )

@router.get("/upload/{file_id}/preview", response_model=ApiResponse[FilePreview])
async def get_file_preview(file_id: str):
    """Get file preview and data analysis"""
    
    if file_id not in upload_registry:
        raise HTTPException(status_code=404, detail="File not found")
    
    upload_file = upload_registry[file_id]
    
    if upload_file.status != UploadStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="File not ready for preview")
    
    try:
        if upload_file.preview:
            preview = upload_file.preview
        else:
            preview = await file_storage_service.generate_preview(upload_file)
            upload_file.preview = preview
            upload_registry[file_id] = upload_file
        
        return ApiResponse(
            success=True,
            data=preview.model_dump(),
            message="Preview generated"
        )
        
    except Exception as e:
        logger.error(f"Error generating preview for {file_id}: {e}")
        return ApiResponse(
            success=False,
            error=f"Preview generation failed: {str(e)}"
        )

@router.delete("/upload/{file_id}", response_model=ApiResponse)
async def delete_file(file_id: str):
    """Delete uploaded file"""
    
    if file_id not in upload_registry:
        raise HTTPException(status_code=404, detail="File not found")
    
    upload_file = upload_registry[file_id]
    
    try:
        # Delete file from storage
        deleted = await file_storage_service.delete_file(upload_file.file_path)
        
        if deleted:
            # Remove from registry
            del upload_registry[file_id]
            
            return ApiResponse(
                success=True,
                message="File deleted successfully"
            )
        else:
            return ApiResponse(
                success=False,
                error="File not found on disk"
            )
            
    except Exception as e:
        logger.error(f"Error deleting file {file_id}: {e}")
        return ApiResponse(
            success=False,
            error=f"Delete failed: {str(e)}"
        )

@router.post("/upload/validate", response_model=ApiResponse[FileValidation])
async def validate_file_content(file: FastAPIUploadFile):
    """Validate file content without uploading"""
    
    try:
        content = await file.read()
        
        # Create temporary upload file for validation
        temp_file = await file_storage_service.save_uploaded_file(
            content, file.filename or "temp", str(uuid.uuid4())
        )
        
        try:
            validation = await file_storage_service.validate_file(temp_file)
            
            return ApiResponse(
                success=True,
                data=validation.model_dump(),
                message="Validation completed"
            )
            
        finally:
            # Clean up temporary file
            await file_storage_service.delete_file(temp_file.file_path)
            
    except Exception as e:
        logger.error(f"Error validating file: {e}")
        return ApiResponse(
            success=False,
            error=f"Validation failed: {str(e)}"
        )

@router.get("/upload/stats")
async def get_upload_stats():
    """Get upload statistics"""
    
    total_files = len(upload_registry)
    total_size = sum(f.size for f in upload_registry.values())
    
    by_status = {}
    for status in UploadStatus:
        by_status[status.value] = len([f for f in upload_registry.values() if f.status == status])
    
    return ApiResponse(
        success=True,
        data={
            "total_files": total_files,
            "total_size": total_size,
            "by_status": by_status,
            "scanner_info": virus_scan_service.get_scanner_info()
        }
    )

@router.get("/upload")
async def list_uploads():
    """List all uploaded files"""
    
    files = []
    for file_id, upload_file in upload_registry.items():
        files.append({
            "id": file_id,
            "name": upload_file.original_name,
            "size": upload_file.size,
            "status": upload_file.status.value,
            "created_at": upload_file.created_at.isoformat(),
            "has_preview": upload_file.preview is not None,
            "scan_status": "clean" if upload_file.scan_result and upload_file.scan_result.is_clean else "unknown"
        })
    
    return ApiResponse(
        success=True,
        data=files
    )

# Background task functions

async def scan_file_background(file_id: str):
    """Background task to scan uploaded file"""
    if file_id not in upload_registry:
        return
    
    upload_file = upload_registry[file_id]
    
    try:
        scan_result = await virus_scan_service.scan_file(upload_file.file_path)
        upload_file.scan_result = scan_result
        upload_file.updated_at = datetime.utcnow()
        
        # Quarantine if infected
        if not scan_result.is_clean:
            quarantine_path = await file_storage_service.quarantine_file(
                upload_file,
                f"Background scan failed: {'; '.join(scan_result.threats or [])}"
            )
            upload_file.file_path = quarantine_path
            upload_file.status = UploadStatus.ERROR
            upload_file.error_message = "File quarantined due to security scan failure"
        
        upload_registry[file_id] = upload_file
        logger.info(f"Background scan completed for {file_id}: {'clean' if scan_result.is_clean else 'infected'}")
        
    except Exception as e:
        logger.error(f"Background scan failed for {file_id}: {e}")
        upload_file.error_message = f"Scan error: {str(e)}"
        upload_registry[file_id] = upload_file