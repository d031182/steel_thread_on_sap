"""
Log Manager Module
==================
SQLite-based persistent application logging system.

Quick Start:
    from modules.log_manager import SQLiteLogHandler, setup_logging
    
    # Setup logging
    import logging
    logger = logging.getLogger(__name__)
    handler = setup_logging(logger, db_path='logs/app_logs.db', retention_days=2)
    
    # Use Flask Blueprint
    from modules.log_manager.backend.api import create_blueprint
    app.register_blueprint(create_blueprint(handler), url_prefix='/api')

Author: P2P Development Team
Version: 1.0.0
"""

from modules.log_manager.backend.sqlite_logger import SQLiteLogHandler, setup_logging
from modules.log_manager.backend.api import create_blueprint

__version__ = '1.0.0'
__all__ = ['SQLiteLogHandler', 'setup_logging', 'create_blueprint']