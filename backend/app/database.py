"""
File: database.py

Overview:
Database connection setup and session management for PostgreSQL with SQLAlchemy.

Purpose:
Provides database engine configuration, session management, and connection pooling
for the AI Hub AI/ML Wrangler application.

Dependencies:
- sqlalchemy: ORM and database toolkit
- asyncpg: Async PostgreSQL driver
- psycopg2: Sync PostgreSQL driver

Last Modified: 2025-08-15
Author: Claude
"""

from typing import AsyncGenerator, Generator
import logging
from contextlib import asynccontextmanager, contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import QueuePool

from .config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create the declarative base for models
Base = declarative_base()

# Synchronous database engine with connection pooling
sync_engine = create_engine(
    settings.database.database_url,
    poolclass=QueuePool,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_pre_ping=settings.database.pool_pre_ping,
    pool_recycle=settings.database.pool_recycle,
    echo=settings.app.debug,
    future=True
)

# Asynchronous database engine with connection pooling
async_engine = create_async_engine(
    settings.database.async_database_url,
    poolclass=QueuePool,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_pre_ping=settings.database.pool_pre_ping,
    pool_recycle=settings.database.pool_recycle,
    echo=settings.app.debug,
    future=True
)

# Session makers
SessionLocal = sessionmaker(
    bind=sync_engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


# Event listeners for connection management
@event.listens_for(sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set connection-level settings for PostgreSQL."""
    if settings.app.debug:
        logger.info("Database connection established")


@event.listens_for(sync_engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log connection checkout in debug mode."""
    if settings.app.debug:
        logger.debug("Connection checked out from pool")


@event.listens_for(sync_engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log connection checkin in debug mode."""
    if settings.app.debug:
        logger.debug("Connection checked back into pool")


# Dependency for FastAPI
def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async dependency function to get database session.
    
    Yields:
        AsyncSession: SQLAlchemy async database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Async database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Yields:
        Session: SQLAlchemy database session
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error(f"Database session error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


@asynccontextmanager
async def async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions.
    
    Yields:
        AsyncSession: SQLAlchemy async database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Async database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


def create_tables():
    """Create all database tables."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=sync_engine)
    logger.info("Database tables created successfully")


async def create_tables_async():
    """Create all database tables asynchronously."""
    logger.info("Creating database tables asynchronously...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")


def drop_tables():
    """Drop all database tables."""
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=sync_engine)
    logger.warning("All database tables dropped")


async def drop_tables_async():
    """Drop all database tables asynchronously."""
    logger.warning("Dropping all database tables asynchronously...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.warning("All database tables dropped")


def check_database_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with sync_engine.connect() as connection:
            connection.execute("SELECT 1")
        logger.info("Database connection check successful")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


async def check_database_connection_async() -> bool:
    """
    Check if async database connection is working.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        async with async_engine.connect() as connection:
            await connection.execute("SELECT 1")
        logger.info("Async database connection check successful")
        return True
    except Exception as e:
        logger.error(f"Async database connection check failed: {e}")
        return False


def get_database_info() -> dict:
    """
    Get database connection information.
    
    Returns:
        dict: Database connection information
    """
    return {
        "database_url": settings.database.database_url.replace(settings.database.password, "***"),
        "pool_size": settings.database.pool_size,
        "max_overflow": settings.database.max_overflow,
        "pool_pre_ping": settings.database.pool_pre_ping,
        "pool_recycle": settings.database.pool_recycle,
        "engine_pool_size": sync_engine.pool.size(),
        "engine_pool_checked_in": sync_engine.pool.checkedin(),
        "engine_pool_checked_out": sync_engine.pool.checkedout(),
        "engine_pool_invalid": sync_engine.pool.invalid(),
    }