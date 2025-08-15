"""
File: exceptions.py

Overview:
Custom exception classes and error handlers for the FastAPI application

Purpose:
Provide structured error handling and consistent error responses

Dependencies:
- FastAPI: Exception handling framework
- pydantic: Data validation

Last Modified: 2025-08-15
Author: Claude
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


class MLWranglerException(Exception):
    """Base exception for ML Wrangler application"""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class FileUploadException(MLWranglerException):
    """Exception raised during file upload operations"""
    pass


class DataProcessingException(MLWranglerException):
    """Exception raised during data processing operations"""
    pass


class ImputationException(MLWranglerException):
    """Exception raised during imputation operations"""
    pass


class CorrelationException(MLWranglerException):
    """Exception raised during correlation analysis"""
    pass


async def ml_wrangler_exception_handler(request: Request, exc: MLWranglerException) -> JSONResponse:
    """
    Handle custom ML Wrangler exceptions
    
    Args:
        request: FastAPI request object
        exc: ML Wrangler exception instance
        
    Returns:
        JSON error response
    """
    logger.error(f"ML Wrangler error: {exc.message}", extra={"details": exc.details})
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "ML Wrangler Error",
            "message": exc.message,
            "details": exc.details,
            "type": exc.__class__.__name__
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle general exceptions
    
    Args:
        request: FastAPI request object
        exc: Exception instance
        
    Returns:
        JSON error response
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "type": "InternalServerError"
        }
    )