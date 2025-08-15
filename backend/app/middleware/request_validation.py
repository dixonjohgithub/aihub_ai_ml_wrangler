"""
File: request_validation.py

Overview:
Request validation middleware for API endpoints.

Purpose:
Validates all incoming requests using the SecurityService to ensure data integrity and security.

Dependencies:
- fastapi: Web framework
- app.services.security_service: Security validation

Last Modified: 2025-08-15
Author: Claude
"""

from typing import Dict, Any, Optional, List, Callable
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import json
import logging
from functools import wraps

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.security_service import SecurityService, SecurityConfig

logger = logging.getLogger(__name__)


# Pydantic models for request validation

class FileUploadRequest(BaseModel):
    """Validation model for file upload requests"""
    filename: str = Field(..., min_length=1, max_length=255)
    file_type: str = Field(..., regex=r"^\.(csv|json|xlsx|xls|parquet|txt|tsv)$")
    file_size: int = Field(..., gt=0, le=104857600)  # Max 100MB
    
    @validator('filename')
    def validate_filename(cls, v):
        """Validate filename for security issues"""
        if '../' in v or '..\\' in v:
            raise ValueError('Path traversal detected in filename')
        if any(char in v for char in ['<', '>', ':', '"', '|', '?', '*']):
            raise ValueError('Invalid characters in filename')
        return v


class ImputationRequest(BaseModel):
    """Validation model for imputation requests"""
    strategy: str = Field(..., regex=r"^(mean|median|mode|knn|mice|missforest|forward_fill|backward_fill|interpolate|constant)$")
    columns: List[str] = Field(..., min_items=1, max_items=100)
    parameters: Optional[Dict[str, Any]] = Field(default={})
    
    @validator('columns')
    def validate_columns(cls, v):
        """Validate column names"""
        for col in v:
            if not col.replace('_', '').replace('-', '').replace('.', '').isalnum():
                raise ValueError(f'Invalid column name: {col}')
            if len(col) > 100:
                raise ValueError(f'Column name too long: {col}')
        return v


class CorrelationRequest(BaseModel):
    """Validation model for correlation analysis requests"""
    method: str = Field(..., regex=r"^(pearson|spearman|kendall|cramers_v|point_biserial)$")
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    columns: Optional[List[str]] = Field(default=None, max_items=200)
    target_column: Optional[str] = Field(default=None, max_length=100)


class ReportGenerationRequest(BaseModel):
    """Validation model for report generation requests"""
    title: str = Field(..., min_length=1, max_length=200)
    sections: List[str] = Field(..., min_items=1, max_items=20)
    format: str = Field(default="markdown", regex=r"^(markdown|html|pdf)$")
    include_visualizations: bool = Field(default=True)
    include_metadata: bool = Field(default=True)
    
    @validator('title')
    def validate_title(cls, v):
        """Validate report title"""
        # Remove potentially dangerous characters
        if any(char in v for char in ['<', '>', '"', "'", '`']):
            raise ValueError('Invalid characters in title')
        return v


class DataQueryRequest(BaseModel):
    """Validation model for data query requests"""
    query_type: str = Field(..., regex=r"^(select|filter|aggregate|transform)$")
    filters: Optional[Dict[str, Any]] = Field(default={})
    limit: int = Field(default=1000, ge=1, le=10000)
    offset: int = Field(default=0, ge=0)
    
    @validator('filters')
    def validate_filters(cls, v):
        """Validate filter parameters"""
        if v:
            # Check for SQL injection patterns in filter values
            for key, value in v.items():
                if isinstance(value, str):
                    if any(pattern in value.upper() for pattern in ['DROP', 'DELETE', 'INSERT', 'UPDATE']):
                        raise ValueError(f'Potentially dangerous filter value: {value}')
        return v


class RequestValidationMiddleware:
    """
    Middleware for validating incoming requests
    """
    
    def __init__(self, security_config: Optional[SecurityConfig] = None):
        """Initialize validation middleware"""
        self.security_service = SecurityService(security_config)
        self.validation_rules = self._setup_validation_rules()
    
    def _setup_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Setup validation rules for different endpoints"""
        return {
            '/api/upload': {
                'model': FileUploadRequest,
                'rate_limit': 10,  # 10 uploads per minute
                'require_auth': False
            },
            '/api/imputation': {
                'model': ImputationRequest,
                'rate_limit': 30,
                'require_auth': False
            },
            '/api/correlation': {
                'model': CorrelationRequest,
                'rate_limit': 30,
                'require_auth': False
            },
            '/api/report': {
                'model': ReportGenerationRequest,
                'rate_limit': 10,
                'require_auth': False
            },
            '/api/data/query': {
                'model': DataQueryRequest,
                'rate_limit': 60,
                'require_auth': False
            }
        }
    
    async def validate_request(
        self,
        request: Request,
        call_next: Callable
    ) -> JSONResponse:
        """
        Validate incoming request
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or endpoint
            
        Returns:
            Response or error
        """
        try:
            # Get client IP for rate limiting
            client_ip = request.client.host if request.client else "unknown"
            
            # Check rate limit
            is_allowed, retry_after = self.security_service.rate_limiter.check_rate_limit(client_ip)
            if not is_allowed:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "retry_after": retry_after
                    },
                    headers={"Retry-After": str(retry_after)}
                )
            
            # Get endpoint path
            path = request.url.path
            
            # Find matching validation rule
            validation_rule = None
            for pattern, rule in self.validation_rules.items():
                if path.startswith(pattern):
                    validation_rule = rule
                    break
            
            # If validation rule exists, validate request body
            if validation_rule and request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    # Read request body
                    body = await request.body()
                    if body:
                        # Parse JSON
                        try:
                            data = json.loads(body)
                        except json.JSONDecodeError:
                            return JSONResponse(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                content={"error": "Invalid JSON in request body"}
                            )
                        
                        # Validate with Pydantic model
                        model_class = validation_rule['model']
                        try:
                            validated_data = model_class(**data)
                            
                            # Store validated data for endpoint to use
                            request.state.validated_data = validated_data
                            
                        except Exception as e:
                            return JSONResponse(
                                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content={
                                    "error": "Validation failed",
                                    "details": str(e)
                                }
                            )
                        
                        # Additional security checks
                        security_checks = self._perform_security_checks(data)
                        if not security_checks['valid']:
                            return JSONResponse(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                content={
                                    "error": "Security validation failed",
                                    "details": security_checks['errors']
                                }
                            )
            
            # Validate headers
            header_validation = self._validate_headers(request.headers)
            if not header_validation['valid']:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "error": "Invalid headers",
                        "details": header_validation['errors']
                    }
                )
            
            # Call next middleware or endpoint
            response = await call_next(request)
            
            # Add security headers to response
            security_headers = self.security_service.get_security_headers()
            for header, value in security_headers.items():
                response.headers[header] = value
            
            return response
            
        except Exception as e:
            logger.error(f"Request validation error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Internal server error during validation"}
            )
    
    def _perform_security_checks(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform additional security checks on request data
        
        Args:
            data: Request data
            
        Returns:
            Validation result
        """
        errors = []
        
        # Check all string values for potential security issues
        for key, value in data.items():
            if isinstance(value, str):
                # Check for XSS attempts
                if any(pattern in value.lower() for pattern in ['<script', 'javascript:', 'onerror=']):
                    errors.append(f"Potential XSS in field: {key}")
                
                # Check for SQL injection
                is_valid, error = self.security_service.validator.validate_input(value, 'sql_safe')
                if not is_valid:
                    errors.append(f"SQL injection risk in field {key}: {error}")
                
                # Check length
                if len(value) > 10000:
                    errors.append(f"Field {key} exceeds maximum length")
            
            elif isinstance(value, dict):
                # Recursive check for nested objects
                nested_check = self._perform_security_checks(value)
                if not nested_check['valid']:
                    errors.extend(nested_check['errors'])
            
            elif isinstance(value, list):
                # Check list items
                for item in value[:100]:  # Limit to first 100 items
                    if isinstance(item, str):
                        is_valid, error = self.security_service.validator.validate_input(item, 'general')
                        if not is_valid:
                            errors.append(f"Invalid item in {key}: {error}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _validate_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate request headers
        
        Args:
            headers: Request headers
            
        Returns:
            Validation result
        """
        errors = []
        
        # Check Content-Type for POST/PUT requests
        content_type = headers.get('content-type', '')
        if content_type and 'multipart/form-data' not in content_type:
            # For non-file uploads, should be JSON
            if 'application/json' not in content_type and 'text/csv' not in content_type:
                errors.append(f"Invalid Content-Type: {content_type}")
        
        # Check for suspicious headers
        suspicious_headers = ['x-forwarded-host', 'x-original-url', 'x-rewrite-url']
        for header in suspicious_headers:
            if header in headers:
                logger.warning(f"Suspicious header detected: {header}")
        
        # Validate User-Agent
        user_agent = headers.get('user-agent', '')
        if user_agent:
            # Check for common scanner/bot patterns
            bot_patterns = ['sqlmap', 'nikto', 'burp', 'nmap', 'metasploit']
            if any(pattern in user_agent.lower() for pattern in bot_patterns):
                errors.append(f"Suspicious User-Agent: {user_agent}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }


def create_validation_decorator(validation_model: BaseModel):
    """
    Create a decorator for endpoint validation
    
    Args:
        validation_model: Pydantic model for validation
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Get request data
            try:
                if request.method in ['POST', 'PUT', 'PATCH']:
                    data = await request.json()
                    # Validate with model
                    validated_data = validation_model(**data)
                    # Add to kwargs
                    kwargs['validated_data'] = validated_data
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Validation error: {str(e)}"
                )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


# Validation functions for specific data types

def validate_dataframe_request(df_data: Dict[str, Any]) -> bool:
    """
    Validate DataFrame data from request
    
    Args:
        df_data: DataFrame data as dictionary
        
    Returns:
        True if valid
    """
    # Check structure
    if not isinstance(df_data, dict):
        return False
    
    # Check for required keys
    if 'columns' not in df_data or 'data' not in df_data:
        return False
    
    # Validate columns
    columns = df_data['columns']
    if not isinstance(columns, list) or len(columns) > 1000:
        return False
    
    # Validate column names
    for col in columns:
        if not isinstance(col, str) or len(col) > 100:
            return False
        # Check for SQL injection in column names
        if any(char in col for char in [';', '--', '/*', '*/', 'DROP', 'DELETE']):
            return False
    
    return True


def validate_file_content(content: bytes, file_type: str) -> bool:
    """
    Validate file content matches expected type
    
    Args:
        content: File content bytes
        file_type: Expected file type
        
    Returns:
        True if valid
    """
    # Check file signatures
    signatures = {
        'csv': [b',', b'"', b'\n'],
        'json': [b'{', b'['],
        'parquet': [b'PAR1']
    }
    
    if file_type in signatures:
        # Check if content contains expected patterns
        for sig in signatures[file_type]:
            if sig in content[:1000]:  # Check first 1KB
                return True
        return False
    
    return True  # Allow unknown types


# Export validation models for use in endpoints
__all__ = [
    'RequestValidationMiddleware',
    'FileUploadRequest',
    'ImputationRequest',
    'CorrelationRequest',
    'ReportGenerationRequest',
    'DataQueryRequest',
    'create_validation_decorator',
    'validate_dataframe_request',
    'validate_file_content'
]