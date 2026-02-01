"""
Log Manager Backend Package
============================
Backend components for application logging system.

Exports:
    SQLiteLogHandler: Async logging handler with SQLite persistence
    LoggingService: Business logic wrapper implementing ApplicationLogger interface
    setup_logging: Helper function to configure logging
    create_blueprint: Flask Blueprint factory
"""

from modules.log_manager.backend.sqlite_logger import SQLiteLogHandler, setup_logging
from modules.log_manager.backend.logging_service import LoggingService
from modules.log_manager.backend.api import create_blueprint

__all__ = ['SQLiteLogHandler', 'LoggingService', 'setup_logging', 'create_blueprint']
