"""
File: logging.py

Overview:
Logging configuration for the FastAPI application

Purpose:
Centralize logging setup with appropriate levels and formatters

Dependencies:
- logging: Python logging module
- sys: System-specific parameters

Last Modified: 2025-08-15
Author: Claude
"""

import logging
import sys
from typing import Any, Dict


def setup_logging(level: str = "INFO") -> None:
    """
    Setup application logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Configure specific loggers
    loggers_config = {
        "uvicorn": {"level": "INFO"},
        "uvicorn.access": {"level": "INFO"},
        "fastapi": {"level": "INFO"},
        "app": {"level": "DEBUG" if level.upper() == "DEBUG" else "INFO"}
    }
    
    for logger_name, config in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, config["level"]))


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)