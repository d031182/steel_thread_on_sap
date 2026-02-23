"""
Database Unit of Work Pattern

Manages database transactions with proper commit/rollback handling.
Resolves manual transaction management DI violations.

@author P2P Development Team
@version 1.0.0 (DI Compliance)
@date 2026-02-23
"""

import sqlite3
import logging
from typing import Protocol, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class IUnitOfWork(Protocol):
    """Interface for Unit of Work pattern"""
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions
        
        Automatically commits on success, rolls back on exception.
        
        Yields:
            sqlite3.Connection: Active connection within transaction
            
        Example:
            with unit_of_work.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO table VALUES (?)", (value,))
                # Automatically commits on exit
                # Automatically rolls back on exception
        """
        ...


class TransactionError(Exception):
    """Raised when transaction fails"""
    pass


class SqliteUnitOfWork:
    """
    SQLite Unit of Work implementation
    
    Benefits:
    - Automatic transaction management
    - DI compliant (injected connection factory)
    - Consistent error handling
    - Resource cleanup guaranteed
    
    Pattern: Unit of Work (Fowler's PoEAA)
    """
    
    def __init__(self, connection_factory):
        """
        Initialize with connection factory
        
        Args:
            connection_factory: Factory for creating database connections
                               (IDatabaseConnectionFactory compatible)
        """
        self.connection_factory = connection_factory
        logger.debug("SqliteUnitOfWork initialized")
    
    @contextmanager
    def transaction(self):
        """
        Execute operations within a transaction
        
        Yields:
            sqlite3.Connection: Active connection
            
        Behavior:
        - Creates new connection
        - Begins transaction (implicit in SQLite)
        - Commits on successful completion
        - Rolls back on any exception
        - Always closes connection
        
        Example:
            uow = SqliteUnitOfWork(factory)
            
            try:
                with uow.transaction() as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO users VALUES (?, ?)", (1, 'Alice'))
                    cursor.execute("INSERT INTO profiles VALUES (?, ?)", (1, 'Bio'))
                    # Both committed together
            except TransactionError as e:
                # Both rolled back together
                logger.error(f"Transaction failed: {e}")
        """
        conn = None
        try:
            # Create connection
            conn = self.connection_factory.create_connection()
            
            # Yield connection for operations
            # (SQLite automatically starts transaction on first write)
            yield conn
            
            # Commit transaction on success
            conn.commit()
            logger.debug("Transaction committed successfully")
            
        except Exception as e:
            # Rollback on any error
            if conn:
                conn.rollback()
                logger.warning(f"Transaction rolled back due to error: {e}")
            
            # Re-raise as TransactionError
            raise TransactionError(f"Transaction failed: {e}") from e
            
        finally:
            # Always close connection
            if conn:
                conn.close()
                logger.debug("Connection closed")
    
    @contextmanager
    def readonly_query(self):
        """
        Execute read-only operations (no transaction needed)
        
        Yields:
            sqlite3.Connection: Active connection
            
        Benefits:
        - No transaction overhead for reads
        - Automatic connection cleanup
        - Consistent error handling
        
        Example:
            with uow.readonly_query() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users")
                rows = cursor.fetchall()
        """
        conn = None
        try:
            conn = self.connection_factory.create_connection()
            yield conn
            
        finally:
            if conn:
                conn.close()