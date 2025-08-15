"""
File: health.py

Overview:
Health check endpoint for API monitoring and status verification

Purpose:
Provide health status information for load balancers and monitoring systems

Dependencies:
- FastAPI: Router and response models
- datetime: Timestamp generation

Last Modified: 2025-08-15
Author: Claude
"""

from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint
    
    Returns:
        Dict containing service status and timestamp
    """
    return {
        "status": "healthy",
        "service": "AI Hub AI/ML Wrangler API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "development"
    }


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with system information
    
    Returns:
        Dict containing detailed service status
    """
    return {
        "status": "healthy",
        "service": "AI Hub AI/ML Wrangler API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "development",
        "components": {
            "api": "healthy",
            "database": "not_configured",
            "redis": "not_configured",
            "file_system": "healthy"
        },
        "uptime": "just_started"
    }