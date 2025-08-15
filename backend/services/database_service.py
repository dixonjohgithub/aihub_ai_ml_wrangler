"""
File: database_service.py

Overview:
Database service for common database operations

Purpose:
Provides high-level database operations and utilities

Dependencies:
- sqlalchemy: Database ORM
- backend.config.database: Database configuration

Last Modified: 2025-08-15
Author: Claude
"""

import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from backend.config.database import AsyncSessionLocal, engine

logger = logging.getLogger(__name__)

class DatabaseService:
    """Database service with common operations"""
    
    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            async with AsyncSessionLocal() as session:
                await session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def get_session(self) -> AsyncSession:
        """Get a database session"""
        return AsyncSessionLocal()
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Execute a raw SQL query"""
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(query, params or {})
                await session.commit()
                return result
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return None