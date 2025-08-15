"""
File: services/database_service.py

Overview:
Database service providing high-level database operations and utilities.

Purpose:
Provides database operations like health checks, table management,
and common database utilities for the application.

Dependencies:
- sqlalchemy: ORM functionality
- app.database: Database connections
- app.models: Database models

Last Modified: 2025-08-15
Author: Claude
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

from ..database import (
    sync_engine,
    async_engine,
    SessionLocal,
    AsyncSessionLocal,
    create_tables,
    create_tables_async,
    drop_tables,
    drop_tables_async,
    check_database_connection,
    check_database_connection_async,
    get_database_info
)
from ..models import User, Dataset, Job

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database operations and management."""
    
    def __init__(self):
        """Initialize database service."""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive database health check.
        
        Returns:
            dict: Health check results
        """
        health_data = {
            "status": "unknown",
            "sync_connection": False,
            "async_connection": False,
            "tables_exist": False,
            "pool_info": {},
            "error": None
        }
        
        try:
            # Check synchronous connection
            health_data["sync_connection"] = check_database_connection()
            
            # Check asynchronous connection
            health_data["async_connection"] = await check_database_connection_async()
            
            # Check if tables exist
            health_data["tables_exist"] = await self.check_tables_exist()
            
            # Get connection pool information
            health_data["pool_info"] = get_database_info()
            
            # Determine overall status
            if health_data["sync_connection"] and health_data["async_connection"]:
                health_data["status"] = "healthy"
            else:
                health_data["status"] = "unhealthy"
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            health_data["status"] = "error"
            health_data["error"] = str(e)
        
        return health_data
    
    async def check_tables_exist(self) -> bool:
        """
        Check if all required tables exist in the database.
        
        Returns:
            bool: True if all tables exist, False otherwise
        """
        try:
            async with async_engine.connect() as conn:
                # Get inspector
                inspector = inspect(conn.sync_connection)
                existing_tables = inspector.get_table_names()
                
                # Check required tables
                required_tables = {"users", "datasets", "jobs"}
                missing_tables = required_tables - set(existing_tables)
                
                if missing_tables:
                    logger.warning(f"Missing tables: {missing_tables}")
                    return False
                
                return True
                
        except Exception as e:
            logger.error(f"Error checking tables: {e}")
            return False
    
    async def initialize_database(self) -> Dict[str, Any]:
        """
        Initialize the database by creating all tables.
        
        Returns:
            dict: Initialization results
        """
        result = {
            "success": False,
            "tables_created": False,
            "error": None
        }
        
        try:
            logger.info("Initializing database...")
            
            # Create tables asynchronously
            await create_tables_async()
            
            # Verify tables were created
            tables_exist = await self.check_tables_exist()
            
            result["tables_created"] = tables_exist
            result["success"] = tables_exist
            
            if tables_exist:
                logger.info("Database initialized successfully")
            else:
                logger.error("Database initialization failed - tables not created")
                
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            result["error"] = str(e)
        
        return result
    
    async def reset_database(self) -> Dict[str, Any]:
        """
        Reset the database by dropping and recreating all tables.
        
        Returns:
            dict: Reset results
        """
        result = {
            "success": False,
            "tables_dropped": False,
            "tables_created": False,
            "error": None
        }
        
        try:
            logger.warning("Resetting database...")
            
            # Drop all tables
            await drop_tables_async()
            result["tables_dropped"] = True
            
            # Recreate all tables
            await create_tables_async()
            
            # Verify tables were created
            tables_exist = await self.check_tables_exist()
            result["tables_created"] = tables_exist
            result["success"] = tables_exist
            
            if tables_exist:
                logger.warning("Database reset completed successfully")
            else:
                logger.error("Database reset failed - tables not created")
                
        except Exception as e:
            logger.error(f"Database reset failed: {e}")
            result["error"] = str(e)
        
        return result
    
    async def get_table_info(self) -> Dict[str, Any]:
        """
        Get information about database tables.
        
        Returns:
            dict: Table information
        """
        table_info = {
            "tables": {},
            "total_tables": 0,
            "error": None
        }
        
        try:
            async with async_engine.connect() as conn:
                inspector = inspect(conn.sync_connection)
                
                for table_name in inspector.get_table_names():
                    columns = inspector.get_columns(table_name)
                    indexes = inspector.get_indexes(table_name)
                    foreign_keys = inspector.get_foreign_keys(table_name)
                    
                    table_info["tables"][table_name] = {
                        "columns": [
                            {
                                "name": col["name"],
                                "type": str(col["type"]),
                                "nullable": col["nullable"],
                                "primary_key": col.get("primary_key", False)
                            }
                            for col in columns
                        ],
                        "indexes": [idx["name"] for idx in indexes],
                        "foreign_keys": [fk["name"] for fk in foreign_keys],
                        "column_count": len(columns)
                    }
                
                table_info["total_tables"] = len(table_info["tables"])
                
        except Exception as e:
            logger.error(f"Error getting table info: {e}")
            table_info["error"] = str(e)
        
        return table_info
    
    async def execute_query(self, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute a raw SQL query.
        
        Args:
            query: SQL query to execute
            params: Optional query parameters
            
        Returns:
            dict: Query results
        """
        result = {
            "success": False,
            "rows": [],
            "row_count": 0,
            "error": None
        }
        
        try:
            async with AsyncSessionLocal() as session:
                # Execute query
                if params:
                    db_result = await session.execute(text(query), params)
                else:
                    db_result = await session.execute(text(query))
                
                # Fetch results if it's a SELECT query
                if query.strip().upper().startswith("SELECT"):
                    rows = db_result.fetchall()
                    result["rows"] = [dict(row._mapping) for row in rows]
                    result["row_count"] = len(result["rows"])
                else:
                    # For non-SELECT queries, commit the transaction
                    await session.commit()
                    result["row_count"] = db_result.rowcount
                
                result["success"] = True
                
        except SQLAlchemyError as e:
            logger.error(f"SQL query error: {e}")
            result["error"] = str(e)
        except Exception as e:
            logger.error(f"Unexpected error executing query: {e}")
            result["error"] = str(e)
        
        return result
    
    async def get_database_size(self) -> Dict[str, Any]:
        """
        Get database size information.
        
        Returns:
            dict: Database size information
        """
        size_info = {
            "database_size": None,
            "table_sizes": {},
            "total_rows": 0,
            "error": None
        }
        
        try:
            async with AsyncSessionLocal() as session:
                # Get database size
                db_size_result = await session.execute(
                    text("SELECT pg_size_pretty(pg_database_size(current_database())) as size")
                )
                size_row = db_size_result.fetchone()
                if size_row:
                    size_info["database_size"] = size_row[0]
                
                # Get table sizes and row counts
                tables = ["users", "datasets", "jobs"]
                total_rows = 0
                
                for table in tables:
                    try:
                        # Get table size
                        size_result = await session.execute(
                            text(f"SELECT pg_size_pretty(pg_total_relation_size('{table}')) as size")
                        )
                        size_row = size_result.fetchone()
                        table_size = size_row[0] if size_row else "Unknown"
                        
                        # Get row count
                        count_result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count_row = count_result.fetchone()
                        row_count = count_row[0] if count_row else 0
                        
                        size_info["table_sizes"][table] = {
                            "size": table_size,
                            "rows": row_count
                        }
                        
                        total_rows += row_count
                        
                    except Exception as e:
                        logger.warning(f"Could not get size info for table {table}: {e}")
                        size_info["table_sizes"][table] = {
                            "size": "Unknown",
                            "rows": 0
                        }
                
                size_info["total_rows"] = total_rows
                
        except Exception as e:
            logger.error(f"Error getting database size: {e}")
            size_info["error"] = str(e)
        
        return size_info
    
    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get database connection information.
        
        Returns:
            dict: Connection information
        """
        return get_database_info()


# Global database service instance
database_service = DatabaseService()