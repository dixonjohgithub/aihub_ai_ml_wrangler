"""
File: virus_scan.py

Overview:
Virus scanning service for uploaded files with multiple scanner support

Purpose:
Provides security scanning capabilities to detect malicious files

Dependencies:
- subprocess (for ClamAV integration)
- hashlib (for file hashing)
- pathlib (for file operations)

Last Modified: 2025-08-15
Author: Claude
"""

import subprocess
import hashlib
import time
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..models.upload import ScanResult, ScanStatus

logger = logging.getLogger(__name__)

class VirusScanService:
    def __init__(self):
        self.clamav_available = self._check_clamav_availability()
        self.scan_timeout = 300  # 5 minutes
        
        # Known malicious file signatures (simplified for demo)
        self.malicious_signatures = {
            'eicar_test': b'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*',
            'suspicious_script': b'<script>alert("xss")</script>',
        }
        
        # File extension risk levels
        self.risk_extensions = {
            '.exe': 'high',
            '.bat': 'high',
            '.cmd': 'high',
            '.scr': 'high',
            '.vbs': 'medium',
            '.js': 'medium',
            '.jar': 'medium',
            '.zip': 'low',
            '.rar': 'low'
        }

    def _check_clamav_availability(self) -> bool:
        """Check if ClamAV is available on the system"""
        try:
            result = subprocess.run(
                ['clamscan', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            available = result.returncode == 0
            if available:
                logger.info("ClamAV scanner available")
            else:
                logger.warning("ClamAV scanner not available, using fallback scanning")
            return available
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            logger.warning("ClamAV scanner not available, using fallback scanning")
            return False

    async def scan_file(self, file_path: str) -> ScanResult:
        """Scan file for viruses and malware"""
        start_time = datetime.utcnow()
        path = Path(file_path)
        
        if not path.exists():
            return ScanResult(
                is_clean=False,
                scan_engine="error",
                threats=["File not found"],
                scan_time=start_time
            )
        
        try:
            # Try ClamAV first if available
            if self.clamav_available:
                result = await self._scan_with_clamav(file_path)
            else:
                result = await self._scan_with_fallback(file_path)
            
            # Calculate scan duration
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            result.scan_duration_ms = duration_ms
            
            logger.info(f"File scan completed: {file_path} - Clean: {result.is_clean}")
            return result
            
        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {e}")
            return ScanResult(
                is_clean=False,
                scan_engine="error",
                threats=[f"Scan error: {str(e)}"],
                scan_time=start_time
            )

    async def _scan_with_clamav(self, file_path: str) -> ScanResult:
        """Scan file using ClamAV"""
        try:
            # Run ClamAV scan
            result = subprocess.run(
                ['clamscan', '--no-summary', '--infected', file_path],
                capture_output=True,
                text=True,
                timeout=self.scan_timeout
            )
            
            threats = []
            is_clean = True
            
            if result.returncode == 1:  # Virus found
                is_clean = False
                # Parse ClamAV output for threat names
                for line in result.stdout.split('\n'):
                    if 'FOUND' in line:
                        threat = line.split(':')[-1].strip().replace(' FOUND', '')
                        threats.append(threat)
            elif result.returncode != 0:  # Error occurred
                raise Exception(f"ClamAV scan failed with code {result.returncode}: {result.stderr}")
            
            return ScanResult(
                is_clean=is_clean,
                scan_engine="ClamAV",
                threats=threats if threats else None,
                scan_time=datetime.utcnow()
            )
            
        except subprocess.TimeoutExpired:
            raise Exception("ClamAV scan timed out")
        except Exception as e:
            logger.error(f"ClamAV scan error: {e}")
            raise

    async def _scan_with_fallback(self, file_path: str) -> ScanResult:
        """Fallback scanning when ClamAV is not available"""
        threats = []
        
        # Read file content for signature checking
        try:
            with open(file_path, 'rb') as f:
                content = f.read(10240)  # Read first 10KB for signature check
                
            # Check for known malicious signatures
            for signature_name, signature in self.malicious_signatures.items():
                if signature in content:
                    threats.append(f"Detected: {signature_name}")
            
            # Check file extension risk
            file_ext = Path(file_path).suffix.lower()
            if file_ext in self.risk_extensions:
                risk_level = self.risk_extensions[file_ext]
                if risk_level == 'high':
                    threats.append(f"High-risk file type: {file_ext}")
                elif risk_level == 'medium':
                    # Only warn, don't block
                    logger.warning(f"Medium-risk file type detected: {file_ext}")
            
            # Check for suspicious patterns in text files
            if file_ext in ['.txt', '.csv', '.json']:
                suspicious_patterns = [
                    b'<script',
                    b'javascript:',
                    b'eval(',
                    b'document.write',
                    b'<?php'
                ]
                
                for pattern in suspicious_patterns:
                    if pattern in content.lower():
                        threats.append(f"Suspicious pattern detected: {pattern.decode('utf-8', errors='ignore')}")
            
            return ScanResult(
                is_clean=len(threats) == 0,
                scan_engine="Fallback Scanner",
                threats=threats if threats else None,
                scan_time=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Fallback scan error: {e}")
            raise

    async def scan_multiple_files(self, file_paths: List[str]) -> Dict[str, ScanResult]:
        """Scan multiple files"""
        results = {}
        
        for file_path in file_paths:
            try:
                result = await self.scan_file(file_path)
                results[file_path] = result
            except Exception as e:
                logger.error(f"Error scanning {file_path}: {e}")
                results[file_path] = ScanResult(
                    is_clean=False,
                    scan_engine="error",
                    threats=[f"Scan failed: {str(e)}"],
                    scan_time=datetime.utcnow()
                )
        
        return results

    def get_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            raise

    def is_scanner_available(self) -> bool:
        """Check if virus scanner is available"""
        return self.clamav_available

    def get_scanner_info(self) -> Dict[str, Any]:
        """Get information about available scanners"""
        info = {
            'clamav_available': self.clamav_available,
            'fallback_available': True,
            'scan_timeout': self.scan_timeout
        }
        
        if self.clamav_available:
            try:
                result = subprocess.run(
                    ['clamscan', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    info['clamav_version'] = result.stdout.strip()
            except Exception:
                pass
        
        return info

    async def update_virus_definitions(self) -> bool:
        """Update virus definitions (ClamAV only)"""
        if not self.clamav_available:
            logger.warning("Cannot update virus definitions: ClamAV not available")
            return False
        
        try:
            logger.info("Updating virus definitions...")
            result = subprocess.run(
                ['freshclam'],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes for updates
            )
            
            success = result.returncode == 0
            if success:
                logger.info("Virus definitions updated successfully")
            else:
                logger.error(f"Failed to update virus definitions: {result.stderr}")
            
            return success
            
        except subprocess.TimeoutExpired:
            logger.error("Virus definition update timed out")
            return False
        except Exception as e:
            logger.error(f"Error updating virus definitions: {e}")
            return False

# Global service instance
virus_scan_service = VirusScanService()