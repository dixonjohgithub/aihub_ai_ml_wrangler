"""
File: file_storage.py

Overview:
File storage service for secure file handling and management

Purpose:
Provides secure file upload, storage, validation, and retrieval operations

Dependencies:
- aiofiles (async file operations)
- pathlib (file path handling)
- magic (MIME type detection)
- pandas (data analysis for CSV files)

Last Modified: 2025-08-15
Author: Claude
"""

import os
import shutil
import uuid
import aiofiles
import magic
import pandas as pd
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import logging

from ..models.upload import (
    UploadFile, FileValidation, FilePreview, FileType, UploadStatus
)

logger = logging.getLogger(__name__)

class FileStorageService:
    def __init__(self, base_upload_dir: str = "uploads"):
        self.base_upload_dir = Path(base_upload_dir)
        self.temp_dir = self.base_upload_dir / "temp"
        self.permanent_dir = self.base_upload_dir / "files"
        self.quarantine_dir = self.base_upload_dir / "quarantine"
        
        # Configuration
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.allowed_extensions = {'.csv', '.json'}
        self.allowed_mime_types = {
            'text/csv', 'application/csv', 'text/plain',
            'application/json', 'text/json'
        }
        
        # Create directories
        self._ensure_directories()

    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        for directory in [self.temp_dir, self.permanent_dir, self.quarantine_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Storage directories ensured: {self.base_upload_dir}")

    async def save_uploaded_file(
        self, 
        file_content: bytes, 
        original_filename: str,
        file_id: Optional[str] = None
    ) -> UploadFile:
        """Save uploaded file to temporary storage"""
        if not file_id:
            file_id = str(uuid.uuid4())
        
        # Generate safe filename
        file_extension = Path(original_filename).suffix.lower()
        stored_filename = f"{file_id}{file_extension}"
        temp_path = self.temp_dir / stored_filename
        
        try:
            # Save file to temporary location
            async with aiofiles.open(temp_path, 'wb') as f:
                await f.write(file_content)
            
            # Get file info
            file_size = len(file_content)
            mime_type = await self._detect_mime_type(temp_path)
            
            # Create upload record
            upload_file = UploadFile(
                id=file_id,
                original_name=original_filename,
                stored_name=stored_filename,
                file_path=str(temp_path),
                size=file_size,
                mime_type=mime_type,
                status=UploadStatus.PENDING,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            logger.info(f"File saved to temp storage: {file_id}")
            return upload_file
            
        except Exception as e:
            # Clean up on error
            if temp_path.exists():
                temp_path.unlink()
            logger.error(f"Error saving file {file_id}: {e}")
            raise

    async def validate_file(self, upload_file: UploadFile) -> FileValidation:
        """Validate uploaded file"""
        errors = []
        warnings = []
        
        file_path = Path(upload_file.file_path)
        
        # Check if file exists
        if not file_path.exists():
            errors.append("File not found")
            return FileValidation(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                file_type=FileType.UNKNOWN,
                size_bytes=0
            )
        
        # File size validation
        if upload_file.size > self.max_file_size:
            errors.append(f"File size {upload_file.size} exceeds maximum allowed size of {self.max_file_size}")
        
        # File extension validation
        file_extension = file_path.suffix.lower()
        if file_extension not in self.allowed_extensions:
            errors.append(f"File extension '{file_extension}' is not allowed")
        
        # MIME type validation
        if upload_file.mime_type and upload_file.mime_type not in self.allowed_mime_types:
            warnings.append(f"MIME type '{upload_file.mime_type}' may not be supported")
        
        # Determine file type
        file_type = self._determine_file_type(upload_file.original_name, upload_file.mime_type)
        
        # Content validation
        content_errors, content_warnings = await self._validate_file_content(file_path, file_type)
        errors.extend(content_errors)
        warnings.extend(content_warnings)
        
        # Data Wrangler pattern validation
        is_dw_format, dw_warnings = self._validate_data_wrangler_pattern(upload_file.original_name)
        warnings.extend(dw_warnings)
        
        return FileValidation(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            file_type=file_type,
            mime_type=upload_file.mime_type,
            size_bytes=upload_file.size,
            is_data_wrangler_format=is_dw_format
        )

    async def generate_preview(self, upload_file: UploadFile) -> FilePreview:
        """Generate file preview with data analysis"""
        file_path = Path(upload_file.file_path)
        
        preview = FilePreview(
            name=upload_file.original_name,
            size=upload_file.size,
            type=upload_file.mime_type or 'unknown'
        )
        
        try:
            file_type = self._determine_file_type(upload_file.original_name, upload_file.mime_type)
            
            if file_type == FileType.CSV:
                await self._generate_csv_preview(file_path, preview)
            elif file_type == FileType.JSON:
                await self._generate_json_preview(file_path, preview)
                
        except Exception as e:
            logger.error(f"Error generating preview for {upload_file.id}: {e}")
            # Return basic preview even if detailed analysis fails
        
        return preview

    async def move_to_permanent_storage(self, upload_file: UploadFile) -> str:
        """Move file from temporary to permanent storage"""
        temp_path = Path(upload_file.file_path)
        permanent_path = self.permanent_dir / upload_file.stored_name
        
        try:
            shutil.move(str(temp_path), str(permanent_path))
            logger.info(f"File moved to permanent storage: {upload_file.id}")
            return str(permanent_path)
        except Exception as e:
            logger.error(f"Error moving file to permanent storage: {e}")
            raise

    async def quarantine_file(self, upload_file: UploadFile, reason: str) -> str:
        """Move file to quarantine"""
        current_path = Path(upload_file.file_path)
        quarantine_path = self.quarantine_dir / f"{upload_file.stored_name}.quarantined"
        
        try:
            shutil.move(str(current_path), str(quarantine_path))
            
            # Create quarantine log
            log_path = quarantine_path.with_suffix('.log')
            async with aiofiles.open(log_path, 'w') as f:
                await f.write(json.dumps({
                    'file_id': upload_file.id,
                    'original_name': upload_file.original_name,
                    'reason': reason,
                    'quarantined_at': datetime.utcnow().isoformat(),
                    'file_size': upload_file.size,
                    'mime_type': upload_file.mime_type
                }, indent=2))
            
            logger.warning(f"File quarantined: {upload_file.id} - {reason}")
            return str(quarantine_path)
        except Exception as e:
            logger.error(f"Error quarantining file: {e}")
            raise

    async def delete_file(self, file_path: str) -> bool:
        """Delete file from storage"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False

    async def get_file_content(self, file_path: str) -> bytes:
        """Read file content"""
        async with aiofiles.open(file_path, 'rb') as f:
            return await f.read()

    def calculate_file_hash(self, content: bytes) -> str:
        """Calculate SHA-256 hash of file content"""
        return hashlib.sha256(content).hexdigest()

    # Private helper methods
    
    async def _detect_mime_type(self, file_path: Path) -> str:
        """Detect MIME type using python-magic"""
        try:
            mime_type = magic.from_file(str(file_path), mime=True)
            return mime_type
        except Exception as e:
            logger.warning(f"Could not detect MIME type for {file_path}: {e}")
            return 'application/octet-stream'

    def _determine_file_type(self, filename: str, mime_type: Optional[str]) -> FileType:
        """Determine file type from filename and MIME type"""
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.csv') or (mime_type and 'csv' in mime_type):
            return FileType.CSV
        elif filename_lower.endswith('.json') or (mime_type and 'json' in mime_type):
            return FileType.JSON
        else:
            return FileType.UNKNOWN

    async def _validate_file_content(self, file_path: Path, file_type: FileType) -> Tuple[List[str], List[str]]:
        """Validate file content based on type"""
        errors = []
        warnings = []
        
        try:
            if file_type == FileType.CSV:
                csv_errors, csv_warnings = await self._validate_csv_content(file_path)
                errors.extend(csv_errors)
                warnings.extend(csv_warnings)
            elif file_type == FileType.JSON:
                json_errors, json_warnings = await self._validate_json_content(file_path)
                errors.extend(json_errors)
                warnings.extend(json_warnings)
        except Exception as e:
            errors.append(f"Error reading file content: {str(e)}")
        
        return errors, warnings

    async def _validate_csv_content(self, file_path: Path) -> Tuple[List[str], List[str]]:
        """Validate CSV file content"""
        errors = []
        warnings = []
        
        try:
            # Try to read with pandas
            df = pd.read_csv(file_path, nrows=5)  # Read only first 5 rows for validation
            
            if df.empty:
                warnings.append("CSV file appears to be empty")
            elif len(df.columns) == 1:
                warnings.append("CSV file has only one column - check delimiter")
                
        except pd.errors.EmptyDataError:
            errors.append("CSV file is empty")
        except pd.errors.ParserError as e:
            errors.append(f"CSV parsing error: {str(e)}")
        except Exception as e:
            errors.append(f"Error reading CSV file: {str(e)}")
        
        return errors, warnings

    async def _validate_json_content(self, file_path: Path) -> Tuple[List[str], List[str]]:
        """Validate JSON file content"""
        errors = []
        warnings = []
        
        try:
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
            
            if not content.strip():
                errors.append("JSON file is empty")
                return errors, warnings
            
            data = json.loads(content)
            
            # Basic structure validation for Data Wrangler metadata
            if file_path.name.lower().find('metadata') != -1:
                if not isinstance(data, dict):
                    warnings.append("Metadata file should contain a JSON object")
                else:
                    expected_fields = ['statistics', 'transformations', 'columns', 'dataTypes']
                    missing_fields = [field for field in expected_fields if field not in data]
                    if missing_fields:
                        warnings.append(f"Metadata file missing expected fields: {', '.join(missing_fields)}")
                        
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            errors.append(f"Error reading JSON file: {str(e)}")
        
        return errors, warnings

    def _validate_data_wrangler_pattern(self, filename: str) -> Tuple[bool, List[str]]:
        """Validate Data Wrangler file naming patterns"""
        warnings = []
        filename_lower = filename.lower()
        
        is_transformation = 'transformation_file' in filename_lower and filename_lower.endswith('.csv')
        is_mapped_data = 'mapped_data' in filename_lower and filename_lower.endswith('.csv')
        is_metadata = 'metadata' in filename_lower and filename_lower.endswith('.json')
        
        is_dw_format = is_transformation or is_mapped_data or is_metadata
        
        if not is_dw_format:
            warnings.append(
                "File name does not match Data Wrangler export patterns. "
                "Expected: transformation_file.csv, mapped_data.csv, or metadata.json"
            )
        
        return is_dw_format, warnings

    async def _generate_csv_preview(self, file_path: Path, preview: FilePreview):
        """Generate preview for CSV files"""
        try:
            df = pd.read_csv(file_path, nrows=1000)  # Read first 1000 rows
            
            preview.rows = len(df)
            preview.columns = df.columns.tolist()
            
            # Generate sample data (first 5 rows)
            sample_df = df.head(5)
            preview.sample_data = sample_df.to_dict('records')
            
        except Exception as e:
            logger.error(f"Error generating CSV preview: {e}")

    async def _generate_json_preview(self, file_path: Path, preview: FilePreview):
        """Generate preview for JSON files"""
        try:
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
            
            data = json.loads(content)
            
            if isinstance(data, list):
                preview.rows = len(data)
                if data and isinstance(data[0], dict):
                    preview.columns = list(data[0].keys())
                preview.sample_data = data[:5]  # First 5 items
                preview.metadata = {'type': 'array', 'total_items': len(data)}
            elif isinstance(data, dict):
                preview.columns = list(data.keys())
                preview.sample_data = [data]
                preview.metadata = {'type': 'object', 'keys_count': len(data)}
                
                # Check for Data Wrangler metadata structure
                if file_path.name.lower().find('metadata') != -1:
                    preview.metadata.update({
                        'is_data_wrangler_metadata': True,
                        'has_statistics': 'statistics' in data,
                        'has_transformations': 'transformations' in data,
                        'has_data_types': 'dataTypes' in data
                    })
            
        except Exception as e:
            logger.error(f"Error generating JSON preview: {e}")

# Global service instance
file_storage_service = FileStorageService()

def ensure_upload_directories():
    """Ensure upload directories exist - called during app startup"""
    file_storage_service._ensure_directories()