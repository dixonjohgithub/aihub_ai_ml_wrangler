"""
File: security_service.py

Overview:
Comprehensive security service for input validation, sanitization, and protection.

Purpose:
Provides security measures against common vulnerabilities without authentication.

Dependencies:
- bleach: HTML sanitization
- sqlalchemy: SQL injection prevention
- validators: Input validation

Last Modified: 2025-08-15
Author: Claude
"""

import re
import hashlib
import secrets
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import logging
import json
from functools import wraps
import time
from collections import defaultdict
import mimetypes

import bleach
import validators
from sqlalchemy import text
from sqlalchemy.sql import visitors
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class SecurityConfig:
    """Security configuration"""
    max_file_size_mb: int = 100
    allowed_file_extensions: List[str] = None
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60
    max_input_length: int = 10000
    enable_sql_injection_protection: bool = True
    enable_xss_protection: bool = True
    enable_path_traversal_protection: bool = True
    
    def __post_init__(self):
        if self.allowed_file_extensions is None:
            self.allowed_file_extensions = [
                '.csv', '.json', '.xlsx', '.xls', '.parquet', '.txt', '.tsv'
            ]


class InputValidator:
    """
    Validates and sanitizes user inputs
    """
    
    def __init__(self, config: SecurityConfig = None):
        """Initialize input validator"""
        self.config = config or SecurityConfig()
        self.validation_rules = self._setup_validation_rules()
    
    def _setup_validation_rules(self) -> Dict[str, Any]:
        """Setup validation rules for different input types"""
        return {
            'email': lambda x: validators.email(x),
            'url': lambda x: validators.url(x),
            'alphanumeric': lambda x: x.isalnum(),
            'numeric': lambda x: x.replace('.', '').replace('-', '').isdigit(),
            'sql_safe': lambda x: self._is_sql_safe(x),
            'path_safe': lambda x: self._is_path_safe(x),
            'json_safe': lambda x: self._is_json_safe(x)
        }
    
    def validate_input(
        self,
        input_value: Any,
        input_type: str = 'general',
        max_length: Optional[int] = None
    ) -> tuple[bool, str]:
        """
        Validate input based on type
        
        Args:
            input_value: Value to validate
            input_type: Type of input to validate
            max_length: Maximum allowed length
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if input_value is None:
            return True, ""
        
        # Convert to string for validation
        str_value = str(input_value)
        
        # Check length
        max_len = max_length or self.config.max_input_length
        if len(str_value) > max_len:
            return False, f"Input exceeds maximum length of {max_len}"
        
        # Check for null bytes (security risk)
        if '\x00' in str_value:
            return False, "Input contains null bytes"
        
        # Apply type-specific validation
        if input_type in self.validation_rules:
            try:
                if not self.validation_rules[input_type](str_value):
                    return False, f"Invalid {input_type} format"
            except Exception as e:
                return False, f"Validation error: {str(e)}"
        
        # Check for common injection patterns
        if self._contains_injection_pattern(str_value):
            return False, "Input contains potentially malicious patterns"
        
        return True, ""
    
    def _is_sql_safe(self, value: str) -> bool:
        """Check if value is safe from SQL injection"""
        if not self.config.enable_sql_injection_protection:
            return True
        
        # Common SQL injection patterns
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION|FROM|WHERE)\b)",
            r"(--|#|\/\*|\*\/)",  # SQL comments
            r"(\bOR\b.*=.*)",  # OR conditions
            r"(;.*\b(SELECT|INSERT|UPDATE|DELETE|DROP)\b)",  # Multiple statements
            r"(\'.*\b(OR|AND)\b.*\')",  # String-based injection
            r"(\d+\s*=\s*\d+)",  # Always true conditions
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected: {value[:50]}...")
                return False
        
        return True
    
    def _is_path_safe(self, value: str) -> bool:
        """Check if path is safe from traversal attacks"""
        if not self.config.enable_path_traversal_protection:
            return True
        
        # Path traversal patterns
        unsafe_patterns = [
            '..',  # Parent directory
            '~',   # Home directory
            '/etc/',  # System directories
            '/proc/',
            '/sys/',
            'C:\\Windows',  # Windows system
            'C:\\Program',
            '\\\\',  # UNC paths
        ]
        
        for pattern in unsafe_patterns:
            if pattern in value:
                logger.warning(f"Potential path traversal detected: {value[:50]}...")
                return False
        
        # Check for absolute paths (unless explicitly allowed)
        if value.startswith('/') or (len(value) > 1 and value[1] == ':'):
            logger.warning(f"Absolute path detected: {value[:50]}...")
            return False
        
        return True
    
    def _is_json_safe(self, value: str) -> bool:
        """Check if JSON is safe to parse"""
        try:
            # Try to parse JSON
            json.loads(value)
            
            # Check for excessive nesting (DoS prevention)
            depth = self._get_json_depth(value)
            if depth > 10:
                logger.warning(f"JSON nesting depth exceeds limit: {depth}")
                return False
            
            return True
        except json.JSONDecodeError:
            return False
    
    def _get_json_depth(self, json_str: str) -> int:
        """Calculate JSON nesting depth"""
        max_depth = 0
        current_depth = 0
        
        for char in json_str:
            if char in '[{':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char in ']}':
                current_depth -= 1
        
        return max_depth
    
    def _contains_injection_pattern(self, value: str) -> bool:
        """Check for general injection patterns"""
        # JavaScript injection patterns
        js_patterns = [
            r"<script",
            r"javascript:",
            r"on\w+\s*=",  # Event handlers
            r"eval\s*\(",
            r"setTimeout\s*\(",
            r"setInterval\s*\(",
        ]
        
        for pattern in js_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        
        return False
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent security issues
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove path components
        filename = Path(filename).name
        
        # Remove special characters
        filename = re.sub(r'[^\w\s\-\.]', '', filename)
        
        # Limit length
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        if len(name) > 100:
            name = name[:100]
        
        # Ensure extension is allowed
        if ext and f'.{ext.lower()}' not in self.config.allowed_file_extensions:
            raise ValueError(f"File extension .{ext} not allowed")
        
        return f"{name}.{ext}" if ext else name
    
    def validate_dataframe_columns(self, df: pd.DataFrame) -> tuple[bool, List[str]]:
        """
        Validate DataFrame column names for security
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, invalid_columns)
        """
        invalid_columns = []
        
        for col in df.columns:
            # Check for SQL injection in column names
            if not self._is_sql_safe(str(col)):
                invalid_columns.append(col)
            
            # Check for special characters that could cause issues
            if re.search(r'[<>\"\'`]', str(col)):
                invalid_columns.append(col)
        
        return len(invalid_columns) == 0, invalid_columns


class XSSProtection:
    """
    Provides XSS (Cross-Site Scripting) protection
    """
    
    def __init__(self):
        """Initialize XSS protection"""
        self.allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img'
        ]
        self.allowed_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'width', 'height']
        }
    
    def sanitize_html(self, html: str) -> str:
        """
        Sanitize HTML to prevent XSS attacks
        
        Args:
            html: HTML content to sanitize
            
        Returns:
            Sanitized HTML
        """
        return bleach.clean(
            html,
            tags=self.allowed_tags,
            attributes=self.allowed_attributes,
            strip=True
        )
    
    def escape_javascript(self, text: str) -> str:
        """
        Escape text for safe inclusion in JavaScript
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        escape_chars = {
            '\\': '\\\\',
            '"': '\\"',
            "'": "\\'",
            '\n': '\\n',
            '\r': '\\r',
            '\t': '\\t',
            '<': '\\u003C',
            '>': '\\u003E',
            '/': '\\/',
            '\u2028': '\\u2028',
            '\u2029': '\\u2029'
        }
        
        for char, escape in escape_chars.items():
            text = text.replace(char, escape)
        
        return text
    
    def sanitize_json_output(self, data: Any) -> str:
        """
        Sanitize JSON output to prevent XSS
        
        Args:
            data: Data to convert to JSON
            
        Returns:
            Sanitized JSON string
        """
        # Convert to JSON with proper escaping
        json_str = json.dumps(data, ensure_ascii=True)
        
        # Additional escaping for HTML context
        json_str = json_str.replace('<', '\\u003C')
        json_str = json_str.replace('>', '\\u003E')
        json_str = json_str.replace('&', '\\u0026')
        
        return json_str


class SQLInjectionProtection:
    """
    Provides SQL injection protection
    """
    
    @staticmethod
    def parameterize_query(query: str, params: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """
        Parameterize SQL query to prevent injection
        
        Args:
            query: SQL query with placeholders
            params: Parameters to bind
            
        Returns:
            Tuple of (parameterized_query, sanitized_params)
        """
        # Ensure all parameters are properly typed
        sanitized_params = {}
        for key, value in params.items():
            if isinstance(value, str):
                # Check for SQL injection patterns
                validator = InputValidator()
                is_valid, _ = validator.validate_input(value, 'sql_safe')
                if not is_valid:
                    raise ValueError(f"Potentially unsafe parameter: {key}")
            
            sanitized_params[key] = value
        
        # Use SQLAlchemy's text() for parameterization
        safe_query = text(query)
        
        return safe_query, sanitized_params
    
    @staticmethod
    def validate_table_name(table_name: str) -> bool:
        """
        Validate table name to prevent injection
        
        Args:
            table_name: Table name to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Allow only alphanumeric and underscore
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
            return False
        
        # Check against reserved words
        reserved_words = [
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
            'ALTER', 'TABLE', 'DATABASE', 'INDEX', 'VIEW'
        ]
        
        if table_name.upper() in reserved_words:
            return False
        
        return True
    
    @staticmethod
    def escape_like_pattern(pattern: str) -> str:
        """
        Escape special characters in LIKE patterns
        
        Args:
            pattern: LIKE pattern to escape
            
        Returns:
            Escaped pattern
        """
        # Escape special LIKE characters
        pattern = pattern.replace('\\', '\\\\')
        pattern = pattern.replace('%', '\\%')
        pattern = pattern.replace('_', '\\_')
        pattern = pattern.replace('[', '\\[')
        
        return pattern


class RateLimiter:
    """
    Implements rate limiting for API endpoints
    """
    
    def __init__(self, config: SecurityConfig = None):
        """Initialize rate limiter"""
        self.config = config or SecurityConfig()
        self.requests = defaultdict(list)
        self.blocked_ips = {}
    
    def check_rate_limit(self, identifier: str) -> tuple[bool, Optional[int]]:
        """
        Check if request is within rate limit
        
        Args:
            identifier: Unique identifier (IP address, user ID, etc.)
            
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        now = time.time()
        
        # Check if IP is blocked
        if identifier in self.blocked_ips:
            block_until = self.blocked_ips[identifier]
            if now < block_until:
                return False, int(block_until - now)
            else:
                del self.blocked_ips[identifier]
        
        # Clean old requests
        cutoff = now - self.config.rate_limit_window_seconds
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > cutoff
        ]
        
        # Check rate limit
        if len(self.requests[identifier]) >= self.config.rate_limit_requests:
            # Block for window duration
            self.blocked_ips[identifier] = now + self.config.rate_limit_window_seconds
            return False, self.config.rate_limit_window_seconds
        
        # Add current request
        self.requests[identifier].append(now)
        return True, None
    
    def rate_limit_decorator(self, get_identifier):
        """
        Decorator for rate limiting functions
        
        Args:
            get_identifier: Function to get identifier from request
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                identifier = get_identifier(*args, **kwargs)
                is_allowed, retry_after = self.check_rate_limit(identifier)
                
                if not is_allowed:
                    raise Exception(f"Rate limit exceeded. Retry after {retry_after} seconds")
                
                return func(*args, **kwargs)
            return wrapper
        return decorator


class FileUploadSecurity:
    """
    Secure file upload handling
    """
    
    def __init__(self, config: SecurityConfig = None):
        """Initialize file upload security"""
        self.config = config or SecurityConfig()
        self.validator = InputValidator(config)
    
    def validate_file(
        self,
        file_path: str,
        file_content: Optional[bytes] = None
    ) -> tuple[bool, str]:
        """
        Validate uploaded file
        
        Args:
            file_path: Path to file
            file_content: Optional file content bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate filename
        try:
            safe_filename = self.validator.sanitize_filename(Path(file_path).name)
        except ValueError as e:
            return False, str(e)
        
        # Check file extension
        ext = Path(safe_filename).suffix.lower()
        if ext not in self.config.allowed_file_extensions:
            return False, f"File type {ext} not allowed"
        
        # Check file size if content provided
        if file_content:
            size_mb = len(file_content) / (1024 * 1024)
            if size_mb > self.config.max_file_size_mb:
                return False, f"File size {size_mb:.2f}MB exceeds limit of {self.config.max_file_size_mb}MB"
            
            # Check file signature (magic bytes)
            if not self._validate_file_signature(file_content, ext):
                return False, "File content does not match extension"
        
        # Check for malicious patterns in filename
        if '../' in file_path or '..\\' in file_path:
            return False, "Path traversal detected in filename"
        
        return True, ""
    
    def _validate_file_signature(self, content: bytes, extension: str) -> bool:
        """
        Validate file signature matches extension
        
        Args:
            content: File content bytes
            extension: File extension
            
        Returns:
            True if signature matches
        """
        # File signatures (magic bytes)
        signatures = {
            '.csv': [b'', b'"', b'#'],  # CSV can start with various characters
            '.json': [b'{', b'['],
            '.xlsx': [b'PK\x03\x04'],  # ZIP format
            '.xls': [b'\xd0\xcf\x11\xe0'],  # OLE format
            '.parquet': [b'PAR1'],
            '.txt': [b''],  # Text files have no specific signature
            '.tsv': [b'']
        }
        
        if extension not in signatures:
            return True  # Unknown type, allow for now
        
        valid_signatures = signatures[extension]
        if not valid_signatures or b'' in valid_signatures:
            return True  # No signature check needed
        
        # Check if content starts with any valid signature
        for sig in valid_signatures:
            if content.startswith(sig):
                return True
        
        return False
    
    def scan_csv_content(self, df: pd.DataFrame) -> tuple[bool, List[str]]:
        """
        Scan CSV content for security issues
        
        Args:
            df: DataFrame from CSV
            
        Returns:
            Tuple of (is_safe, issues)
        """
        issues = []
        
        # Check column names
        is_valid, invalid_cols = self.validator.validate_dataframe_columns(df)
        if not is_valid:
            issues.append(f"Invalid column names: {invalid_cols}")
        
        # Check for formula injection in cells
        for col in df.columns:
            if df[col].dtype == object:  # String columns
                for value in df[col].dropna().head(100):  # Check first 100 values
                    if self._is_formula_injection(str(value)):
                        issues.append(f"Potential formula injection in column {col}")
                        break
        
        return len(issues) == 0, issues
    
    def _is_formula_injection(self, value: str) -> bool:
        """Check for CSV formula injection"""
        # Excel/CSV formula indicators
        formula_starts = ['=', '+', '-', '@', '\t=', '\n=', '\r=']
        
        for start in formula_starts:
            if value.strip().startswith(start):
                return True
        
        return False


class SecurityService:
    """
    Main security service integrating all security components
    """
    
    def __init__(self, config: SecurityConfig = None):
        """Initialize security service"""
        self.config = config or SecurityConfig()
        self.validator = InputValidator(self.config)
        self.xss_protection = XSSProtection()
        self.sql_protection = SQLInjectionProtection()
        self.rate_limiter = RateLimiter(self.config)
        self.file_security = FileUploadSecurity(self.config)
    
    def validate_request(
        self,
        request_data: Dict[str, Any],
        validation_rules: Dict[str, str]
    ) -> tuple[bool, Dict[str, str]]:
        """
        Validate request data against rules
        
        Args:
            request_data: Request data to validate
            validation_rules: Validation rules for each field
            
        Returns:
            Tuple of (is_valid, errors)
        """
        errors = {}
        
        for field, rule in validation_rules.items():
            if field in request_data:
                is_valid, error = self.validator.validate_input(
                    request_data[field],
                    rule
                )
                if not is_valid:
                    errors[field] = error
        
        return len(errors) == 0, errors
    
    def sanitize_output(self, data: Any, output_type: str = 'json') -> Any:
        """
        Sanitize output data
        
        Args:
            data: Data to sanitize
            output_type: Type of output (json, html, text)
            
        Returns:
            Sanitized data
        """
        if output_type == 'json':
            return self.xss_protection.sanitize_json_output(data)
        elif output_type == 'html':
            if isinstance(data, str):
                return self.xss_protection.sanitize_html(data)
            else:
                return str(data)
        else:
            return data
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate secure random token"""
        return secrets.token_urlsafe(length)
    
    def hash_sensitive_data(self, data: str, salt: Optional[str] = None) -> str:
        """
        Hash sensitive data
        
        Args:
            data: Data to hash
            salt: Optional salt
            
        Returns:
            Hashed data
        """
        if salt:
            data = f"{data}{salt}"
        
        return hashlib.sha256(data.encode()).hexdigest()
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get recommended security headers"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Content-Security-Policy': "default-src 'self'",
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }