"""
Application Logger Module - Backend
====================================
Modern structured logging system with SQLite persistence and REST API.

Features:
- Async log writing with batch processing
- Level-based retention policies (ERROR: 30d, WARNING: 14d, INFO: 7d)
- Structured logging support
- Client-side error capture
- REST API for log management

Author: P2P Development Team
Version: 2.0.0
Date: 2026-02-10
"""

from flask import Blueprint
from .service import LoggingService
from .api import create_blueprint

# Export key components
__all__ = ['logger_api', 'LoggingService']

# Initialize logging service (will be configured by app)
_logging_service = None

def get_logging_service():
    """Get the logging service instance"""
    return _logging_service

def initialize_logging_service(db_path='logs/app_logs.db', retention_policy=None):
    """
    Initialize the logging service
    
    Args:
        db_path: Path to SQLite database
        retention_policy: Dict of retention days by level
    """
    global _logging_service
    if retention_policy is None:
        retention_policy = {'ERROR': 30, 'WARNING': 14, 'INFO': 7}
    
    _logging_service = LoggingService(db_path=db_path, retention_policy=retention_policy)
    return _logging_service

# Create Flask blueprint
logger_api = create_blueprint()