"""
File: config.py

Overview:
Application configuration settings using Pydantic BaseSettings

Purpose:
Centralize environment variable management and application configuration

Dependencies:
- pydantic: Settings management
- python-dotenv: Environment file loading

Last Modified: 2025-08-15
Author: Claude
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AI Hub AI/ML Wrangler"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/ai_ml_wrangler"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # File uploads
    UPLOAD_FOLDER: str = "/tmp/ml_analysis_uploads"
    MAX_UPLOAD_SIZE: int = 104857600  # 100MB
    
    # OpenAI (for future implementation)
    OPENAI_API_KEY: str = ""
    
    # Research Pipeline
    RESEARCH_PIPELINE_PATH: str = "/research_pipeline"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()