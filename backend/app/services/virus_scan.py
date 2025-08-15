"""
File: virus_scan.py

Overview:
Service for scanning uploaded files for malware and security threats

Purpose:
Provides virus scanning capabilities to ensure uploaded files are safe

Dependencies:
- subprocess for running ClamAV
- pathlib for file path operations
- asyncio for async operations

Last Modified: 2025-08-15
Author: Claude
"""

import asyncio
import subprocess
from pathlib import Path
from typing import Tuple, Optional
from datetime import datetime

class VirusScanService:
    def __init__(self, clamd_path: Optional[str] = None):
        self.clamd_path = clamd_path or "clamscan"
        self.scan_timeout = 300  # 5 minutes timeout
        
    async def scan_file(self, file_path: Path) -> Tuple[bool, str]:
        """
        Scan a file for viruses using ClamAV
        
        Returns:
            Tuple[bool, str]: (is_clean, scan_result_message)
        """
        try:
            # Check if file exists
            if not file_path.exists():
                return False, "File does not exist"
            
            # Try to run ClamAV scan
            result = await self._run_clamscan(file_path)
            
            if result is None:
                # If ClamAV is not available, use basic security checks
                return await self._basic_security_scan(file_path)
            
            return result
            
        except Exception as e:
            return False, f"Scan error: {str(e)}"

    async def _run_clamscan(self, file_path: Path) -> Optional[Tuple[bool, str]]:
        """Run ClamAV scan if available"""
        try:
            # Check if ClamAV is available
            check_cmd = ["which", self.clamd_path]
            check_process = await asyncio.create_subprocess_exec(
                *check_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await check_process.communicate()
            
            if check_process.returncode != 0:
                return None  # ClamAV not available
            
            # Run the scan
            scan_cmd = [self.clamd_path, "--no-summary", str(file_path)]
            process = await asyncio.create_subprocess_exec(
                *scan_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=self.scan_timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return False, "Scan timeout - file may be too large or corrupted"
            
            # Parse ClamAV results
            output = stdout.decode('utf-8').strip()
            error = stderr.decode('utf-8').strip()
            
            if process.returncode == 0:
                return True, "File is clean"
            elif process.returncode == 1:
                # Virus found
                return False, f"Threat detected: {output}"
            else:
                # Scan error
                return False, f"Scan failed: {error}"
                
        except Exception:
            return None  # Fall back to basic scan

    async def _basic_security_scan(self, file_path: Path) -> Tuple[bool, str]:
        """
        Basic security checks when ClamAV is not available
        This is not a replacement for proper antivirus scanning
        """
        try:
            # Check file size (very large files might be suspicious)
            file_size = file_path.stat().st_size
            if file_size > 500 * 1024 * 1024:  # 500MB
                return False, "File exceeds safety size limit"
            
            # Check for suspicious file patterns
            if await self._check_suspicious_content(file_path):
                return False, "File contains suspicious patterns"
            
            # Check file extension matches content
            if not await self._validate_file_format(file_path):
                return False, "File format validation failed"
            
            return True, "Basic security checks passed (no antivirus scan performed)"
            
        except Exception as e:
            return False, f"Security check failed: {str(e)}"

    async def _check_suspicious_content(self, file_path: Path) -> bool:
        """Check for suspicious content patterns"""
        try:
            # Read first 1KB to check for suspicious patterns
            with open(file_path, 'rb') as f:
                header = f.read(1024)
            
            # Check for executable headers
            suspicious_patterns = [
                b'\x4D\x5A',  # PE header (Windows executable)
                b'\x7F\x45\x4C\x46',  # ELF header (Linux executable)
                b'\xFE\xED\xFA',  # Mach-O header (macOS executable)
                b'\xCE\xFA\xED\xFE',  # Mach-O header (reversed)
                b'<!DOCTYPE html',  # HTML content (might be phishing)
                b'<script',  # JavaScript content
                b'javascript:',  # JavaScript protocol
            ]
            
            for pattern in suspicious_patterns:
                if pattern in header:
                    return True
            
            return False
            
        except Exception:
            return True  # Assume suspicious if we can't read the file

    async def _validate_file_format(self, file_path: Path) -> bool:
        """Validate that file content matches expected format"""
        try:
            file_extension = file_path.suffix.lower()
            
            if file_extension == '.csv':
                return await self._validate_csv_format(file_path)
            elif file_extension == '.json':
                return await self._validate_json_format(file_path)
            
            return True
            
        except Exception:
            return False

    async def _validate_csv_format(self, file_path: Path) -> bool:
        """Basic CSV format validation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Read first few lines
                lines = [f.readline() for _ in range(5)]
            
            # Check if lines contain CSV-like content
            for line in lines:
                if line.strip():
                    # Should contain commas and printable characters
                    if ',' not in line:
                        return False
                    # Check for excessive control characters
                    control_chars = sum(1 for c in line if ord(c) < 32 and c not in '\n\r\t')
                    if control_chars > len(line) * 0.1:  # More than 10% control chars
                        return False
            
            return True
            
        except Exception:
            return False

    async def _validate_json_format(self, file_path: Path) -> bool:
        """Basic JSON format validation"""
        try:
            import json
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(10000)  # Read first 10KB
            
            # Try to parse as JSON
            json.loads(content)
            return True
            
        except json.JSONDecodeError:
            return False
        except Exception:
            return False

    async def get_scan_info(self) -> dict:
        """Get information about the scanning service"""
        try:
            # Check if ClamAV is available
            check_cmd = ["which", self.clamd_path]
            process = await asyncio.create_subprocess_exec(
                *check_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            clamav_available = process.returncode == 0
            
            if clamav_available:
                # Get ClamAV version
                version_cmd = [self.clamd_path, "--version"]
                version_process = await asyncio.create_subprocess_exec(
                    *version_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await version_process.communicate()
                version_info = stdout.decode('utf-8').strip()
            else:
                version_info = "Not available"
            
            return {
                "clamav_available": clamav_available,
                "version": version_info,
                "scan_method": "ClamAV" if clamav_available else "Basic security checks",
                "timeout": self.scan_timeout
            }
            
        except Exception as e:
            return {
                "clamav_available": False,
                "version": "Error checking",
                "scan_method": "Basic security checks",
                "error": str(e)
            }