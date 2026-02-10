"""
SQLite Log Handler with Async Batch Processing
===============================================
Production-grade logging handler with async writes and batch processing.

Features:
- Asynchronous log writing via queue
- Batch processing for efficiency
- Auto-retry on failures
- Thread-safe operations
- Automatic database initialization

Author: P2P Development Team
Version: 2.0.0
Date: 2026-02-10
"""

import logging
import sqlite3
import threading
import queue
import time
import os
from datetime import datetime
from pathlib import Path


class SQLiteLogHandler(logging.Handler):
    """
    Async SQLite log handler with batch processing
    
    Industry best practices implemented:
    - Async writes to prevent blocking
    - Batch processing for performance
    - Structured log storage
    - Thread-safe queue-based design
    """
    
    def __init__(self, db_path='logs/app_logs.db', batch_size=100, batch_timeout=5.0):
        """
        Initialize SQLite log handler
        
        Args:
            db_path: Path to SQLite database
            batch_size: Number of logs to batch before writing
            batch_timeout: Seconds to wait before forcing batch write
        """
        super().__init__()
        self.db_path = db_path
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        
        # Create database directory if needed
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Async writing setup
        self.log_queue = queue.Queue()
        self.batch = []
        self.last_write_time = time.time()
        self.shutdown_flag = threading.Event()
        
        # Start background writer thread
        self.writer_thread = threading.Thread(target=self._batch_writer, daemon=True)
        self.writer_thread.start()
    
    def _init_database(self):
        """Initialize SQLite database with logs table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                logger_name TEXT,
                message TEXT NOT NULL,
                pathname TEXT,
                lineno INTEGER,
                func_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes separately
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_level ON logs(level)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON logs(created_at)')
        
        conn.commit()
        conn.close()
    
    def emit(self, record):
        """
        Handle a log record (called by logging framework)
        
        Args:
            record: LogRecord instance
        """
        try:
            # Format timestamp
            timestamp = datetime.fromtimestamp(record.created).isoformat()
            
            # Extract log data
            log_data = {
                'timestamp': timestamp,
                'level': record.levelname,
                'logger_name': record.name,
                'message': self.format(record),
                'pathname': record.pathname,
                'lineno': record.lineno,
                'func_name': record.funcName
            }
            
            # Add to queue for async processing
            self.log_queue.put(log_data)
            
        except Exception:
            self.handleError(record)
    
    def _batch_writer(self):
        """Background thread for batch writing logs"""
        while not self.shutdown_flag.is_set():
            try:
                # Try to get log from queue (with timeout)
                try:
                    log_data = self.log_queue.get(timeout=1.0)
                    self.batch.append(log_data)
                except queue.Empty:
                    pass
                
                # Write batch if size reached or timeout exceeded
                should_write = (
                    len(self.batch) >= self.batch_size or
                    (self.batch and time.time() - self.last_write_time >= self.batch_timeout)
                )
                
                if should_write:
                    self._write_batch()
                    
            except Exception as e:
                # Log errors to stderr to avoid infinite loop
                print(f"Error in batch writer: {e}", file=__import__('sys').stderr)
    
    def _write_batch(self):
        """Write accumulated logs to database"""
        if not self.batch:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Batch insert
            cursor.executemany('''
                INSERT INTO logs (timestamp, level, logger_name, message, pathname, lineno, func_name)
                VALUES (:timestamp, :level, :logger_name, :message, :pathname, :lineno, :func_name)
            ''', self.batch)
            
            conn.commit()
            conn.close()
            
            # Clear batch
            self.batch = []
            self.last_write_time = time.time()
            
        except Exception as e:
            print(f"Error writing batch to database: {e}", file=__import__('sys').stderr)
    
    def close(self):
        """Close handler and flush remaining logs"""
        # Signal shutdown
        self.shutdown_flag.set()
        
        # Wait for writer thread
        if self.writer_thread.is_alive():
            self.writer_thread.join(timeout=5.0)
        
        # Flush remaining batch
        self._write_batch()
        
        super().close()
    
    def get_logs(self, level=None, limit=100, offset=0, start_date=None, end_date=None):
        """
        Query logs from database
        
        Args:
            level: Filter by log level (INFO, WARNING, ERROR)
            limit: Maximum logs to return
            offset: Pagination offset
            start_date: Filter logs after this date (ISO format)
            end_date: Filter logs before this date (ISO format)
            
        Returns:
            List of log dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build query
        query = "SELECT * FROM logs WHERE 1=1"
        params = []
        
        if level:
            query += " AND level = ?"
            params.append(level)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dicts
        logs = [dict(row) for row in rows]
        return logs
    
    def get_log_count(self, level=None):
        """
        Get total log count
        
        Args:
            level: Filter by log level (optional)
            
        Returns:
            Integer count
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if level:
            cursor.execute("SELECT COUNT(*) FROM logs WHERE level = ?", (level,))
        else:
            cursor.execute("SELECT COUNT(*) FROM logs")
        
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def clear_logs(self):
        """Delete all logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM logs")
        conn.commit()
        conn.close()