"""
Logger Interface (ILogger)
=========================
Abstract interface for application logging following DI principles.

All modules should depend on this interface, not concrete implementations.

Usage Example:
    # In module (e.g., AI Assistant)
    from core.interfaces.logger import ILogger
    
    class AgentService:
        def __init__(self, logger: ILogger):
            self._logger = logger
        
        def process(self):
            self._logger.info("Processing request")
            try:
                # ... business logic
                self._logger.debug("Step completed")
            except Exception as e:
                self._logger.error(f"Failed: {e}")

Design Principles:
    - Modules depend on ILogger interface (not concrete LogManager)
    - Concrete implementation injected at runtime
    - Easy to mock for testing
    - Follows Open/Closed Principle (SOLID)

Author: P2P Development Team
Version: 1.0.0
Date: 2026-02-17
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum


class LogLevel(Enum):
    """Log levels (standard Python logging levels)"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ILogger(ABC):
    """
    Logger interface for dependency injection
    
    Implementations:
    - FlightRecorderLogger: Detailed logging with all context
    - DefaultLogger: Minimal business-level logging
    - NoOpLogger: Silent logger for testing
    
    Pattern: Strategy Pattern (different logging strategies)
    """
    
    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """
        Log debug message (development/troubleshooting)
        
        Args:
            message: Log message
            **kwargs: Additional context (e.g., user_id, request_id)
        
        Example:
            logger.debug("Database query", query="SELECT *", duration_ms=45)
        """
        pass
    
    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """
        Log informational message (business events)
        
        Args:
            message: Log message
            **kwargs: Additional context
        
        Example:
            logger.info("Order created", order_id="ORD-123", amount=1500.00)
        """
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """
        Log warning message (recoverable issues)
        
        Args:
            message: Log message
            **kwargs: Additional context
        
        Example:
            logger.warning("Slow API response", endpoint="/api/data", duration_ms=3500)
        """
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """
        Log error message (failures)
        
        Args:
            message: Log message
            **kwargs: Additional context (should include exception if available)
        
        Example:
            logger.error("Database connection failed", exception=str(e), host="localhost")
        """
        pass
    
    @abstractmethod
    def critical(self, message: str, **kwargs) -> None:
        """
        Log critical message (system failures)
        
        Args:
            message: Log message
            **kwargs: Additional context
        
        Example:
            logger.critical("Service crashed", service="api", exit_code=1)
        """
        pass
    
    @abstractmethod
    def log(self, level: LogLevel, message: str, **kwargs) -> None:
        """
        Log at specific level (generic method)
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            **kwargs: Additional context
        
        Example:
            logger.log(LogLevel.INFO, "Process completed", status="success")
        """
        pass
    
    @abstractmethod
    def get_mode(self) -> str:
        """
        Get current logging mode
        
        Returns:
            'default' or 'flight_recorder'
        
        Example:
            if logger.get_mode() == 'flight_recorder':
                logger.debug("Detailed trace")  # Only logged in Flight Recorder
        """
        pass
    
    @abstractmethod
    def set_mode(self, mode: str) -> None:
        """
        Set logging mode
        
        Args:
            mode: 'default' or 'flight_recorder'
        
        Example:
            logger.set_mode('flight_recorder')  # Enable detailed logging
        """
        pass
    
    @abstractmethod
    def is_enabled_for(self, level: LogLevel) -> bool:
        """
        Check if level is enabled in current mode
        
        Args:
            level: Log level to check
        
        Returns:
            True if level will be logged, False otherwise
        
        Example:
            if logger.is_enabled_for(LogLevel.DEBUG):
                expensive_data = compute_debug_info()
                logger.debug("Debug info", data=expensive_data)
        """
        pass


class NoOpLogger(ILogger):
    """
    No-operation logger for testing
    
    Implements ILogger but does nothing.
    Useful for unit tests where logging is not needed.
    
    Usage:
        # In test
        logger = NoOpLogger()
        service = AgentService(logger)  # Service works without real logger
    """
    
    def debug(self, message: str, **kwargs) -> None:
        pass
    
    def info(self, message: str, **kwargs) -> None:
        pass
    
    def warning(self, message: str, **kwargs) -> None:
        pass
    
    def error(self, message: str, **kwargs) -> None:
        pass
    
    def critical(self, message: str, **kwargs) -> None:
        pass
    
    def log(self, level: LogLevel, message: str, **kwargs) -> None:
        pass
    
    def get_mode(self) -> str:
        return 'default'
    
    def set_mode(self, mode: str) -> None:
        pass
    
    def is_enabled_for(self, level: LogLevel) -> bool:
        return False