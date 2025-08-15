"""
File: config.py

Overview:
Configuration management for the AI Hub AI/ML Wrangler backend application.

Purpose:
Centralized configuration using Pydantic settings with environment variable support
for database connections, Redis, Celery, and application settings.

Dependencies:
- pydantic_settings: Configuration management
- typing: Type hints

Last Modified: 2025-08-15
Author: Claude
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    name: str = Field(default="aihub_ml_wrangler", env="DB_NAME")
    user: str = Field(default="postgres", env="DB_USER")
    password: str = Field(default="postgres", env="DB_PASSWORD")
    
    # Connection pool settings
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    pool_pre_ping: bool = Field(default=True, env="DB_POOL_PRE_PING")
    pool_recycle: int = Field(default=3600, env="DB_POOL_RECYCLE")
    
    @property
    def database_url(self) -> str:
        """Generate database URL for SQLAlchemy."""
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    @property
    def async_database_url(self) -> str:
        """Generate async database URL for SQLAlchemy."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    db: int = Field(default=0, env="REDIS_DB")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Connection settings
    max_connections: int = Field(default=50, env="REDIS_MAX_CONNECTIONS")
    retry_on_timeout: bool = Field(default=True, env="REDIS_RETRY_ON_TIMEOUT")
    
    @property
    def redis_url(self) -> str:
        """Generate Redis URL for connections."""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class CelerySettings(BaseSettings):
    """Celery configuration settings."""
    
    broker_url: Optional[str] = Field(default=None, env="CELERY_BROKER_URL")
    result_backend: Optional[str] = Field(default=None, env="CELERY_RESULT_BACKEND")
    
    # Task settings
    task_serializer: str = Field(default="json", env="CELERY_TASK_SERIALIZER")
    result_serializer: str = Field(default="json", env="CELERY_RESULT_SERIALIZER")
    accept_content: list[str] = Field(default=["json"], env="CELERY_ACCEPT_CONTENT")
    timezone: str = Field(default="UTC", env="CELERY_TIMEZONE")
    enable_utc: bool = Field(default=True, env="CELERY_ENABLE_UTC")
    
    # Worker settings
    worker_prefetch_multiplier: int = Field(default=1, env="CELERY_WORKER_PREFETCH_MULTIPLIER")
    task_acks_late: bool = Field(default=True, env="CELERY_TASK_ACKS_LATE")
    task_reject_on_worker_lost: bool = Field(default=True, env="CELERY_TASK_REJECT_ON_WORKER_LOST")


class ApplicationSettings(BaseSettings):
    """Application configuration settings."""
    
    title: str = Field(default="AI Hub AI/ML Wrangler", env="APP_TITLE")
    description: str = Field(
        default="Statistical data imputation and analysis tool with AI-powered recommendations",
        env="APP_DESCRIPTION"
    )
    version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    
    # API settings
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    docs_url: str = Field(default="/docs", env="DOCS_URL")
    redoc_url: str = Field(default="/redoc", env="REDOC_URL")
    
    # Security settings
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # File handling
    max_file_size: int = Field(default=100 * 1024 * 1024, env="MAX_FILE_SIZE")  # 100MB
    upload_path: str = Field(default="/tmp/uploads", env="UPLOAD_PATH")
    
    # External APIs
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")


class Settings(BaseSettings):
    """Main application settings."""
    
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    celery: CelerySettings = Field(default_factory=CelerySettings)
    app: ApplicationSettings = Field(default_factory=ApplicationSettings)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Auto-configure Celery broker and result backend if not set
        if not self.celery.broker_url:
            self.celery.broker_url = self.redis.redis_url
        if not self.celery.result_backend:
            self.celery.result_backend = self.redis.redis_url


# Global settings instance
settings = Settings()