"""
Logging Service with Retention Policies
========================================
High-level service for managing application logs with auto-cleanup.

Features:
- Level-based retention policies
- Automatic cleanup of old logs
- Database optimization (VACUUM)
- Thread-safe operations

Author: P2P Development Team
Version: 2.0.0
Date: 2026-02-10
"""

import sqlite3
import threading
import time
from datetime import datetime, timedelta
from .sqlite_handler import SQLiteLogHandler


class LoggingService:
    """
    Logging service with retention policy management
    
    Industry best practices:
    - Different retention by severity (ERROR: 30d, WARNING: 14d, INFO: 7d)
    - Automatic cleanup to manage disk space
    - Database optimization for performance
    """
    
    def __init__(self, db_path='logs/app_logs.db', retention_policy=None):
        """
        Initialize logging service
        
        Args:
            db_path: Path to SQLite database
            retention_policy: Dict mapping log levels to retention days
                             Example: {'ERROR': 30, 'WARNING': 14, 'INFO': 7}
        """
        self.db_path = db_path
        self.retention_policy = retention_policy or {
            'ERROR': 30,
            'WARNING': 14,
            'INFO': 7
        }
        
        # Create log handler
        self.handler = SQLiteLogHandler(db_path=db_path)
        
        # Start cleanup thread
        self.cleanup_interval = 21600  # 6 hours
        self.shutdown_flag = threading.Event()
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def get_handler(self):
        """Get the SQLite log handler for attaching to loggers"""
        return self.handler
    
    def _cleanup_loop(self):
        """Background thread for periodic log cleanup"""
        while not self.shutdown_flag.is_set():
            try:
                self._cleanup_old_logs()
                
                # Wait for next cleanup or shutdown signal
                self.shutdown_flag.wait(timeout=self.cleanup_interval)
                
            except Exception as e:
                print(f"Error in cleanup loop: {e}", file=__import__('sys').stderr)
                # Wait before retrying
                time.sleep(60)
    
    def _cleanup_old_logs(self):
        """Delete logs older than retention policy"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Delete logs by level based on retention policy
            for level, retention_days in self.retention_policy.items():
                cutoff_date = (datetime.now() - timedelta(days=retention_days)).isoformat()
                
                cursor.execute('''
                    DELETE FROM logs 
                    WHERE level = ? AND timestamp < ?
                ''', (level, cutoff_date))
            
            deleted_count = cursor.rowcount
            
            conn.commit()
            
            # Optimize database if significant deletions
            if deleted_count > 1000:
                cursor.execute('VACUUM')
                conn.commit()
            
            if deleted_count > 0:
                print(f"Cleaned up {deleted_count} old log entries")
                
        except Exception as e:
            print(f"Error cleaning up logs: {e}", file=__import__('sys').stderr)
        finally:
            conn.close()
    
    def get_logs(self, level=None, limit=100, offset=0, start_date=None, end_date=None):
        """Query logs from database (delegates to handler)"""
        return self.handler.get_logs(level, limit, offset, start_date, end_date)
    
    def get_log_count(self, level=None):
        """Get log count (delegates to handler)"""
        return self.handler.get_log_count(level)
    
    def clear_logs(self):
        """Clear all logs (delegates to handler)"""
        self.handler.clear_logs()
    
    def close(self):
        """Shutdown service and cleanup resources"""
        # Signal cleanup thread to stop
        self.shutdown_flag.set()
        
        # Wait for cleanup thread
        if self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=2.0)
        
        # Close handler
        self.handler.close()