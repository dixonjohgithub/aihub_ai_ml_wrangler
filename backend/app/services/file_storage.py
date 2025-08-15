"""
File: file_storage.py

Overview:
Service for handling file storage, validation, and metadata extraction

Purpose:
Centralized file handling with security checks, validation, and storage management

Dependencies:
- aiofiles for async file operations
- pandas for data file analysis
- magic for MIME type detection
- pathlib for file path operations

Last Modified: 2025-08-15
Author: Claude
"""

import os
import json
import uuid
import magic
import pandas as pd
import aiofiles
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

from ..models.upload import FileValidationResult, FilePreviewResponse

class FileStorageService:
    def __init__(self, upload_dir: str = "uploads", max_file_size: int = 100 * 1024 * 1024):
        self.upload_dir = Path(upload_dir)
        self.max_file_size = max_file_size
        self.allowed_mime_types = ["text/csv", "application/json"]
        self.allowed_extensions = [".csv", ".json"]
        
        # Create upload directory if it doesn't exist
        self.upload_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for organization
        (self.upload_dir / "temp").mkdir(exist_ok=True)
        (self.upload_dir / "processed").mkdir(exist_ok=True)
        (self.upload_dir / "quarantine").mkdir(exist_ok=True)

    async def validate_file(self, file_path: Path, original_filename: str) -> FileValidationResult:
        """Validate uploaded file for security and format compliance"""
        errors = []
        warnings = []
        
        try:
            # Check if file exists
            if not file_path.exists():
                errors.append("File does not exist")
                return FileValidationResult(is_valid=False, errors=errors, warnings=warnings)
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                errors.append(f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum limit of {self.max_file_size / 1024 / 1024}MB")
            
            # Check file extension
            file_extension = file_path.suffix.lower()
            if file_extension not in self.allowed_extensions:
                errors.append(f"File extension '{file_extension}' is not allowed. Supported: {', '.join(self.allowed_extensions)}")
            
            # Check MIME type
            mime_type = magic.from_file(str(file_path), mime=True)
            if mime_type not in self.allowed_mime_types:
                errors.append(f"File type '{mime_type}' is not allowed. Supported: {', '.join(self.allowed_mime_types)}")
            
            # Check for empty files
            if file_size == 0:
                errors.append("File is empty")
            
            # Warning for large files
            if file_size > 50 * 1024 * 1024:  # 50MB
                warnings.append("Large file detected. Processing may take longer than usual.")
            
            # Validate Data Wrangler file naming patterns
            if not self._is_data_wrangler_file(original_filename):
                warnings.append("File name doesn't match expected Data Wrangler patterns. Please ensure this is a valid export file.")
            
            return FileValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return FileValidationResult(is_valid=False, errors=errors, warnings=warnings)

    def _is_data_wrangler_file(self, filename: str) -> bool:
        """Check if filename matches Data Wrangler export patterns"""
        valid_patterns = [
            "transformation_file.csv",
            "mapped_data.csv", 
            "metadata.json"
        ]
        
        filename_lower = filename.lower()
        return any(pattern in filename_lower for pattern in valid_patterns)

    async def store_file(self, file_content: bytes, original_filename: str) -> Tuple[str, Path]:
        """Store uploaded file with unique identifier"""
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Preserve original extension
        file_extension = Path(original_filename).suffix
        stored_filename = f"{file_id}{file_extension}"
        
        # Store in temp directory initially
        file_path = self.upload_dir / "temp" / stored_filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        return file_id, file_path

    async def generate_preview(self, file_path: Path, file_type: str) -> Optional[FilePreviewResponse]:
        """Generate preview data for uploaded files"""
        try:
            if file_type == "text/csv":
                return await self._generate_csv_preview(file_path)
            elif file_type == "application/json":
                return await self._generate_json_preview(file_path)
            else:
                return None
        except Exception as e:
            print(f"Error generating preview: {str(e)}")
            return None

    async def _generate_csv_preview(self, file_path: Path) -> FilePreviewResponse:
        """Generate preview for CSV files"""
        # Read first few rows to determine structure
        df = pd.read_csv(file_path, nrows=1000)
        
        # Get basic statistics
        total_rows = len(df)
        columns = df.columns.tolist()
        
        # Generate sample data (first 5 rows)
        sample_data = df.head(5).to_dict('records')
        
        # Clean sample data for JSON serialization
        for row in sample_data:
            for key, value in row.items():
                if pd.isna(value):
                    row[key] = None
                elif isinstance(value, (pd.Timestamp, datetime)):
                    row[key] = value.isoformat()
        
        # Detect CSV metadata
        metadata = {
            "encoding": "utf-8",  # Assume UTF-8 for now
            "delimiter": ",",
            "has_header": True,
            "null_values": df.isnull().sum().to_dict()
        }
        
        return FilePreviewResponse(
            columns=columns,
            rows=total_rows,
            sample_data=sample_data,
            file_type="csv",
            metadata=metadata
        )

    async def _generate_json_preview(self, file_path: Path) -> FilePreviewResponse:
        """Generate preview for JSON files"""
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
        
        data = json.loads(content)
        
        if isinstance(data, dict):
            columns = list(data.keys())
            rows = 1
            sample_data = [data]
        elif isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], dict):
                columns = list(data[0].keys())
                rows = len(data)
                sample_data = data[:5]
            else:
                columns = ["value"]
                rows = len(data)
                sample_data = [{"value": item} for item in data[:5]]
        else:
            columns = []
            rows = 0
            sample_data = []
        
        metadata = {
            "data_type": type(data).__name__,
            "structure": "object" if isinstance(data, dict) else "array"
        }
        
        return FilePreviewResponse(
            columns=columns,
            rows=rows,
            sample_data=sample_data,
            file_type="json",
            metadata=metadata
        )

    async def move_to_processed(self, file_path: Path) -> Path:
        """Move file from temp to processed directory"""
        processed_path = self.upload_dir / "processed" / file_path.name
        file_path.rename(processed_path)
        return processed_path

    async def quarantine_file(self, file_path: Path, reason: str) -> Path:
        """Move file to quarantine directory"""
        quarantine_path = self.upload_dir / "quarantine" / file_path.name
        file_path.rename(quarantine_path)
        
        # Create quarantine log
        log_path = quarantine_path.with_suffix('.log')
        async with aiofiles.open(log_path, 'w') as f:
            await f.write(f"Quarantined at: {datetime.now().isoformat()}\n")
            await f.write(f"Reason: {reason}\n")
        
        return quarantine_path

    async def delete_file(self, file_path: Path) -> bool:
        """Delete file from storage"""
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False

    def get_file_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        temp_files = list((self.upload_dir / "temp").glob("*"))
        processed_files = list((self.upload_dir / "processed").glob("*"))
        quarantine_files = list((self.upload_dir / "quarantine").glob("*"))
        
        return {
            "temp_files": len(temp_files),
            "processed_files": len(processed_files),
            "quarantine_files": len(quarantine_files),
            "total_size": sum(f.stat().st_size for f in temp_files + processed_files if f.is_file())
        }