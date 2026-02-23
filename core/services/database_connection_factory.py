"""
Database Connection Factory

Factory pattern for creating database connections with proper resource management.
Resolves DI violations by centralizing connection creation logic.

@author P2P Development Team
@version 1.0.0 (DI Compliance)
@date 2026-02-23
"""

import sqlite3
import logging
from typing import Protocol, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class IDatabaseConnectionFactory(Protocol):
    """Interface for database connection factories"""
    
    def create_connection(self) -> sqlite3.Connection:
        """
        Create a new database connection
        
        Returns:
            sqlite3.Connection: Active database connection
            
        Raises:
            DatabaseConnectionError: If connection fails
        """
        ...
    
    @contextmanager
    def connection_scope(self):
        """
        Context manager for automatic connection cleanup
        
        Yields:
            sqlite3.Connection: Active database connection
            
        Example:
            with factory.connection_scope() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")
        """
        ...


class DatabaseConnectionError(Exception):
    """Raised when database connection fails"""
    pass


class SqliteConnectionFactory:
    """
    SQLite connection factory implementation
    
    Benefits:
    - Centralized connection creation
    - DI compliant (injected db_path)
    - Resource management (context managers)
    - Consistent error handling
    """
    
    def __init__(self, db_path: str):
        """
        Initialize factory with database path
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        logger.debug(f"SqliteConnectionFactory initialized: {db_path}")
    
    def create_connection(self) -> sqlite3.Connection:
        """
        Create new SQLite connection
        
        Returns:
            sqlite3.Connection: Active connection
            
        Raises:
            DatabaseConnectionError: If connection fails
        """
        try:
            conn = sqlite3.connect(self.db_path)
            # Enable foreign keys for referential integrity
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
            
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database {self.db_path}: {e}")
            raise DatabaseConnectionError(f"Connection failed: {e}") from e
    
    @contextmanager
    def connection_scope(self):
        """
        Context manager for automatic connection cleanup
        
        Yields:
            sqlite3.Connection: Active connection
            
        Example:
            with factory.connection_scope() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")
                # Connection automatically closed on exit
        """
        conn = None
        try:
            conn = self.create_connection()
            yield conn
        finally:
            if conn:
                conn.close()