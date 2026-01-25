"""
Application Logging Backend
==========================
Backend components for application logging.

Exports:
    - SQLiteLogHandler: Low-level SQLite logging handler
    - LoggingService: ApplicationLogger interface implementation
    - setup_logging: Convenience function for quick setup
    - create_blueprint: Flask API blueprint
"""

from modules.application_logging.backend.sqlite_logger import SQLiteLogHandler, setup_logging
from modules.application_logging.backend.logging_service import LoggingService
from modules.application_logging.backend.api import create_blueprint

__all__ = ['SQLiteLogHandler', 'LoggingService', 'setup_logging', 'create_blueprint']