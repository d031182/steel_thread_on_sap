"""
Logging Service
===============
ApplicationLogger interface implementation using SQLite backend.

This service provides a clean interface for application logging,
abstracting away the SQLite implementation details.
"""

import sys
import os
from typing import List, Dict, Optional

# Add project root to path for interface imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(backend_dir)))
sys.path.insert(0, project_root)

from core.interfaces.logger import ApplicationLogger
from .sqlite_logger import SQLiteLogHandler


class LoggingService(ApplicationLogger):
    """
    ApplicationLogger implementation using SQLite backend
    
    Provides standard interface for application logging with
    SQLite persistence, querying, and management.
    """
    
    def __init__(self, db_path: str = 'logs/app_logs.db', retention_days: int = 2):
        """
        Initialize logging service
        
        Args:
            db_path: Path to SQLite database file
            retention_days: Number of days to retain logs
        """
        self.handler = SQLiteLogHandler(db_path=db_path, retention_days=retention_days)
    
    def get_logs(self, level: Optional[str] = None, limit: int = 100, 
                 offset: int = 0, start_date: Optional[str] = None, 
                 end_date: Optional[str] = None) -> List[Dict]:
        """
        Retrieve logs with filtering
        
        Args:
            level: Filter by log level (INFO, WARNING, ERROR)
            limit: Maximum number of logs to return
            offset: Number of logs to skip (pagination)
            start_date: Filter logs after this date (ISO format)
            end_date: Filter logs before this date (ISO format)
        
        Returns:
            List of log entries as dictionaries
        """
        return self.handler.get_logs(
            level=level,
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date
        )
    
    def get_log_count(self, level: Optional[str] = None) -> int:
        """
        Get total count of logs
        
        Args:
            level: Filter by log level (optional)
        
        Returns:
            Number of log entries
        """
        return self.handler.get_log_count(level=level)
    
    def clear_logs(self) -> None:
        """Clear all logs from storage"""
        self.handler.clear_logs()
    
    def log(self, level: str, message: str, **kwargs) -> None:
        """
        Write a log entry
        
        Args:
            level: Log level (INFO, WARNING, ERROR, etc.)
            message: Log message
            **kwargs: Additional context (currently unused, reserved for future use)
        
        Note:
            This method is provided for interface compliance.
            In practice, logs are written via Python's logging module
            which automatically uses the SQLiteLogHandler.
        """
        import logging
        logger = logging.getLogger('app')
        
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        log_level = level_map.get(level.upper(), logging.INFO)
        logger.log(log_level, message)
    
    def get_handler(self) -> SQLiteLogHandler:
        """
        Get the underlying SQLiteLogHandler
        
        Returns:
            SQLiteLogHandler instance
        
        Note:
            This method allows direct access to the handler for
            advanced use cases like adding it to loggers.
        """
        return self.handler
    
    def close(self) -> None:
        """Close the logging service and stop background threads"""
        self.handler.close()