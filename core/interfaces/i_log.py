"""
ApplicationLogger Interface

Abstract base class for all logging implementations.
Ensures consistent logging API across different storage backends.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class ApplicationLogger(ABC):
    """
    Abstract interface for application loggers.
    
    All logging implementations (SQLite, database, file, etc.)
    must implement this interface to ensure consistent behavior.
    """
    
    @abstractmethod
    def get_logs(
        self, 
        level: Optional[str] = None, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[Dict]:
        """
        Retrieve application logs with optional filtering.
        
        Args:
            level: Filter by log level ('INFO', 'WARNING', 'ERROR'), None for all
            limit: Maximum number of logs to return
            offset: Number of logs to skip (for pagination)
            
        Returns:
            List of log entry dictionaries with keys:
            - id: int
            - timestamp: str (ISO format)
            - level: str ('INFO', 'WARNING', 'ERROR', 'DEBUG')
            - message: str
            - module: str (optional)
            - function: str (optional)
        """
        pass
    
    @abstractmethod
    def get_log_count(self, level: Optional[str] = None) -> int:
        """
        Get total number of log entries.
        
        Args:
            level: Filter by log level, None for all
            
        Returns:
            Total count of log entries
        """
        pass
    
    @abstractmethod
    def clear_logs(self, level: Optional[str] = None) -> int:
        """
        Clear log entries.
        
        Args:
            level: Clear only logs of specific level, None to clear all
            
        Returns:
            Number of log entries deleted
        """
        pass
    
    @abstractmethod
    def log(self, level: str, message: str, **kwargs) -> None:
        """
        Write a log entry.
        
        Args:
            level: Log level ('INFO', 'WARNING', 'ERROR', 'DEBUG')
            message: Log message
            **kwargs: Additional context (module, function, etc.)
        """
        pass