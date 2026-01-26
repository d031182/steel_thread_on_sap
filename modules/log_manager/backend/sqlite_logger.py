"""
SQLite Log Handler Module
========================
Persistent logging handler that stores logs in SQLite database with
automatic cleanup, batching, and async writing.

Features:
- Async log writing via background thread
- Batch processing for efficiency
- Automatic retention policy enforcement
- Database optimization (VACUUM)
- Thread-safe operations

Author: P2P Development Team
Version: 1.0.0
Date: 2026-01-24
"""

import logging
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from queue import Queue
import os


class SQLiteLogHandler(logging.Handler):
    """
    Custom log handler that stores logs in SQLite database
    
    This handler provides persistent, queryable log storage with:
    - Asynchronous writing via background thread
    - Batch processing for efficiency
    - Automatic cleanup of old logs
    - Thread-safe operations
    - Database optimization
    
    Args:
        db_path: Path to SQLite database file
        retention_days: Number of days to retain logs (default: 2)
        batch_size: Number of logs to batch before writing (default: 100)
        batch_timeout: Seconds to wait before forcing batch write (default: 5.0)
        cleanup_interval: Seconds between cleanup runs (default: 21600 = 6 hours)
    """
    
    def __init__(self, db_path='logs/app_logs.db', retention_days=2, 
                 batch_size=100, batch_timeout=5.0, cleanup_interval=21600):
        super().__init__()
        self.db_path = db_path
        self.retention_days = retention_days
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.cleanup_interval = cleanup_interval
        
        self.queue = Queue()
        self.lock = threading.Lock()
        self._stop_event = threading.Event()
        
        # Initialize database
        self.init_database()
        
        # Start background writer thread
        self.writer_thread = threading.Thread(target=self._writer_loop, daemon=True)
        self.writer_thread.start()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def init_database(self):
        """Initialize SQLite database with schema"""
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else '.', exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS application_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                level VARCHAR(10) NOT NULL,
                logger VARCHAR(100) NOT NULL,
                message TEXT NOT NULL,
                duration_ms REAL DEFAULT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Check if duration_ms column exists (for migration from old schema)
        cursor.execute("PRAGMA table_info(application_logs)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'duration_ms' not in columns:
            # Add duration_ms column to existing table
            try:
                cursor.execute('ALTER TABLE application_logs ADD COLUMN duration_ms REAL DEFAULT NULL')
                print("Added duration_ms column to application_logs table")
            except sqlite3.OperationalError as e:
                # Column might already exist in a race condition
                if 'duplicate column name' not in str(e).lower():
                    raise
        
        # Create indices for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON application_logs(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_level ON application_logs(level)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON application_logs(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_duration ON application_logs(duration_ms)')
        
        conn.commit()
        conn.close()
    
    def emit(self, record):
        """
        Store log record in queue for async writing
        
        Args:
            record: LogRecord instance from logging module
        """
        try:
            # Extract duration if present in the record
            duration_ms = getattr(record, 'duration_ms', None)
            
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': self.format(record),
                'duration_ms': duration_ms
            }
            self.queue.put(log_entry)
        except Exception:
            self.handleError(record)
    
    def _writer_loop(self):
        """Background thread that writes logs to database in batches"""
        batch = []
        last_write = time.time()
        
        while not self._stop_event.is_set():
            try:
                # Collect logs from queue
                timeout = self.batch_timeout - (time.time() - last_write)
                if timeout > 0:
                    try:
                        log_entry = self.queue.get(timeout=timeout)
                        batch.append(log_entry)
                    except:
                        pass
                
                # Write batch if we have logs and either batch is full or timeout
                if batch and (len(batch) >= self.batch_size or time.time() - last_write >= self.batch_timeout):
                    self._write_batch(batch)
                    batch = []
                    last_write = time.time()
                
            except Exception as e:
                print(f"Error in log writer thread: {e}")
                time.sleep(1)
    
    def _write_batch(self, batch):
        """
        Write a batch of logs to database
        
        Args:
            batch: List of log entry dictionaries
        """
        if not batch:
            return
        
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                cursor.executemany('''
                    INSERT INTO application_logs (timestamp, level, logger, message, duration_ms)
                    VALUES (?, ?, ?, ?, ?)
                ''', [(log['timestamp'], log['level'], log['logger'], log['message'], log.get('duration_ms')) for log in batch])
                
                conn.commit()
            except Exception as e:
                print(f"Error writing logs to database: {e}")
            finally:
                conn.close()
    
    def _cleanup_loop(self):
        """Background thread that cleans up old logs periodically"""
        while not self._stop_event.is_set():
            try:
                time.sleep(self.cleanup_interval)
                self.cleanup_old_logs()
            except Exception as e:
                print(f"Error in cleanup thread: {e}")
    
    def cleanup_old_logs(self):
        """Delete logs older than retention period and optimize database"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute('DELETE FROM application_logs WHERE created_at < ?', 
                             (cutoff_date.isoformat(),))
                deleted = cursor.rowcount
                conn.commit()
                
                # Vacuum if database is large (>50MB)
                cursor.execute('PRAGMA page_count')
                page_count = cursor.fetchone()[0]
                cursor.execute('PRAGMA page_size')
                page_size = cursor.fetchone()[0]
                db_size_mb = (page_count * page_size) / (1024 * 1024)
                
                if db_size_mb > 50:
                    cursor.execute('VACUUM')
                    conn.commit()
                    print(f"Database vacuumed (was {db_size_mb:.1f}MB)")
                
                if deleted > 0:
                    print(f"Cleaned up {deleted} old logs (retention: {self.retention_days} days)")
                
            except Exception as e:
                print(f"Error cleaning up logs: {e}")
            finally:
                conn.close()
    
    def get_logs(self, level=None, limit=100, offset=0, start_date=None, end_date=None):
        """
        Retrieve logs from database with filtering
        
        Args:
            level: Filter by log level (INFO, WARNING, ERROR)
            limit: Maximum number of logs to return
            offset: Number of logs to skip (for pagination)
            start_date: Filter logs after this date (ISO format)
            end_date: Filter logs before this date (ISO format)
            
        Returns:
            List of log dictionaries
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = 'SELECT * FROM application_logs WHERE 1=1'
            params = []
            
            if level:
                query += ' AND level = ?'
                params.append(level)
            
            if start_date:
                query += ' AND created_at >= ?'
                params.append(start_date)
            
            if end_date:
                query += ' AND created_at <= ?'
                params.append(end_date)
            
            query += ' ORDER BY id DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            logs = [{
                'id': row['id'],
                'timestamp': row['timestamp'],
                'level': row['level'],
                'logger': row['logger'],
                'message': row['message'],
                'duration_ms': row['duration_ms'] if 'duration_ms' in row.keys() else None
            } for row in rows]
            
            conn.close()
            return logs
    
    def get_log_count(self, level=None):
        """
        Get total count of logs
        
        Args:
            level: Filter by log level (optional)
            
        Returns:
            Integer count of logs
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if level:
                cursor.execute('SELECT COUNT(*) FROM application_logs WHERE level = ?', (level,))
            else:
                cursor.execute('SELECT COUNT(*) FROM application_logs')
            
            count = cursor.fetchone()[0]
            conn.close()
            return count
    
    def clear_logs(self):
        """Clear all logs from database"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM application_logs')
            cursor.execute('VACUUM')  # Reclaim space
            conn.commit()
            conn.close()
    
    def close(self):
        """Stop background threads and close handler"""
        self._stop_event.set()
        if self.writer_thread.is_alive():
            self.writer_thread.join(timeout=5)
        if self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5)
        super().close()


def setup_logging(logger, db_path='logs/app_logs.db', retention_days=2, level=logging.INFO):
    """
    Convenience function to set up SQLite logging on a logger
    
    Args:
        logger: Logger instance to add handler to
        db_path: Path to SQLite database
        retention_days: Number of days to retain logs
        level: Logging level (default: INFO)
        
    Returns:
        SQLiteLogHandler instance
    """
    handler = SQLiteLogHandler(db_path=db_path, retention_days=retention_days)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(handler)
    return handler