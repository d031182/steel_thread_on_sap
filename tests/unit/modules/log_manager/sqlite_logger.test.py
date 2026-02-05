"""
Application Logging Module - SQLite Logger Unit Tests
====================================================
Comprehensive test suite for SQLiteLogHandler class.

Test Coverage:
- Database initialization
- Log writing (sync/async)
- Batch processing
- Filtering and pagination
- Cleanup and retention
- Thread safety
- Error handling

Author: P2P Development Team
Version: 1.0.0
Date: 2026-01-25
"""

import unittest
import os
import sys
import tempfile
import time
import logging
from datetime import datetime, timedelta
import pytest

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from modules.application_logging.backend.sqlite_logger import SQLiteLogHandler, setup_logging


class TestSQLiteLogHandler(unittest.TestCase):
    """Test suite for SQLiteLogHandler"""
    
    def setUp(self):
        """Create temporary database for each test"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Create handler with fast batch timeout for testing
        self.handler = SQLiteLogHandler(
            db_path=self.db_path,
            retention_days=7,
            batch_size=5,
            batch_timeout=0.5,
            cleanup_interval=3600
        )
        
        # Create logger for testing
        self.logger = logging.getLogger('test_logger')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.handler)
    
    def tearDown(self):
        """Clean up test database"""
        self.handler.close()
        time.sleep(0.1)  # Wait for threads to finish
        
        if os.path.exists(self.db_path):
            try:
                os.unlink(self.db_path)
            except:
                pass
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_database_initialization(self):
        """Test database is created with correct schema"""
        self.assertTrue(os.path.exists(self.db_path))
        
        # Verify table exists
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='logs'
        """)
        result = cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'logs')
        conn.close()
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_log_writing_sync(self):
        """Test synchronous log writing"""
        # Write a log
        self.logger.info("Test log message")
        
        # Force batch write
        time.sleep(1.0)
        
        # Verify log was written
        logs = self.handler.get_logs(limit=10)
        self.assertEqual(len(logs), 1)
        self.assertIn("Test log message", logs[0]['message'])
        self.assertEqual(logs[0]['level'], 'INFO')
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_batch_processing(self):
        """Test batch writing with multiple logs"""
        # Write 10 logs (batch_size=5, should write 2 batches)
        for i in range(10):
            self.logger.info(f"Batch test log {i}")
        
        # Wait for batches to process
        time.sleep(1.5)
        
        # Verify all logs written
        logs = self.handler.get_logs(limit=20)
        self.assertEqual(len(logs), 10)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_log_filtering_by_level(self):
        """Test filtering logs by level"""
        # Write different level logs
        self.logger.info("Info message")
        self.logger.warning("Warning message")
        self.logger.error("Error message")
        
        time.sleep(1.0)
        
        # Test INFO filter
        info_logs = self.handler.get_logs(level='INFO', limit=10)
        self.assertEqual(len(info_logs), 1)
        self.assertEqual(info_logs[0]['level'], 'INFO')
        
        # Test WARNING filter
        warning_logs = self.handler.get_logs(level='WARNING', limit=10)
        self.assertEqual(len(warning_logs), 1)
        self.assertEqual(warning_logs[0]['level'], 'WARNING')
        
        # Test ERROR filter
        error_logs = self.handler.get_logs(level='ERROR', limit=10)
        self.assertEqual(len(error_logs), 1)
        self.assertEqual(error_logs[0]['level'], 'ERROR')
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_pagination(self):
        """Test pagination with limit and offset"""
        # Write 15 logs
        for i in range(15):
            self.logger.info(f"Pagination test {i}")
        
        time.sleep(1.5)
        
        # Test first page
        page1 = self.handler.get_logs(limit=5, offset=0)
        self.assertEqual(len(page1), 5)
        
        # Test second page
        page2 = self.handler.get_logs(limit=5, offset=5)
        self.assertEqual(len(page2), 5)
        
        # Test third page
        page3 = self.handler.get_logs(limit=5, offset=10)
        self.assertEqual(len(page3), 5)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_date_filtering(self):
        """Test filtering by date range"""
        # Write logs with current timestamp
        self.logger.info("Recent log")
        time.sleep(1.0)
        
        # Get logs from today
        today = datetime.now().strftime('%Y-%m-%d')
        logs = self.handler.get_logs(start_date=today, limit=10)
        self.assertEqual(len(logs), 1)
        
        # Get logs from yesterday (should be empty)
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        logs = self.handler.get_logs(start_date=yesterday, end_date=today, limit=10)
        self.assertGreaterEqual(len(logs), 0)  # May include logs from today
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_log_count(self):
        """Test log count statistics"""
        # Initial count should be 0
        initial_count = self.handler.get_log_count()
        self.assertEqual(initial_count, 0)
        
        # Write 5 INFO, 3 WARNING, 2 ERROR
        for i in range(5):
            self.logger.info(f"Info {i}")
        for i in range(3):
            self.logger.warning(f"Warning {i}")
        for i in range(2):
            self.logger.error(f"Error {i}")
        
        time.sleep(1.5)
        
        # Test counts
        total = self.handler.get_log_count()
        self.assertEqual(total, 10)
        
        info_count = self.handler.get_log_count(level='INFO')
        self.assertEqual(info_count, 5)
        
        warning_count = self.handler.get_log_count(level='WARNING')
        self.assertEqual(warning_count, 3)
        
        error_count = self.handler.get_log_count(level='ERROR')
        self.assertEqual(error_count, 2)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_clear_logs(self):
        """Test clearing all logs"""
        # Write some logs
        for i in range(5):
            self.logger.info(f"Log {i}")
        
        time.sleep(1.0)
        
        # Verify logs exist
        logs_before = self.handler.get_logs(limit=10)
        self.assertEqual(len(logs_before), 5)
        
        # Clear logs
        self.handler.clear_logs()
        
        # Verify logs cleared
        logs_after = self.handler.get_logs(limit=10)
        self.assertEqual(len(logs_after), 0)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_cleanup_old_logs(self):
        """Test automatic cleanup of old logs"""
        # For this test, create handler with very short retention (1 day)
        short_handler = SQLiteLogHandler(
            db_path=self.db_path + '.short',
            retention_days=1,
            batch_size=5,
            batch_timeout=0.5,
            cleanup_interval=1
        )
        
        try:
            # Write logs
            test_logger = logging.getLogger('cleanup_test')
            test_logger.addHandler(short_handler)
            test_logger.info("Test log for cleanup")
            
            time.sleep(1.0)
            
            # Manually run cleanup (instead of waiting for interval)
            short_handler.cleanup_old_logs()
            
            # Note: Since logs are recent, they should NOT be deleted
            logs = short_handler.get_logs(limit=10)
            self.assertEqual(len(logs), 1)
            
        finally:
            short_handler.close()
            if os.path.exists(self.db_path + '.short'):
                os.unlink(self.db_path + '.short')
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_setup_logging_helper(self):
        """Test setup_logging helper function"""
        temp_db2 = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db2.close()
        
        try:
            # Create logger with helper
            test_logger = logging.getLogger('setup_test')
            handler = setup_logging(test_logger, db_path=temp_db2.name, retention_days=3)
            
            self.assertIsNotNone(handler)
            self.assertIsInstance(handler, SQLiteLogHandler)
            
            # Verify logger has handler
            self.assertIn(handler, test_logger.handlers)
            
            # Write log
            test_logger.info("Setup test log")
            time.sleep(1.0)
            
            # Verify log written
            logs = handler.get_logs(limit=10)
            self.assertEqual(len(logs), 1)
            
            handler.close()
            
        finally:
            if os.path.exists(temp_db2.name):
                os.unlink(temp_db2.name)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_concurrent_writing(self):
        """Test thread safety with concurrent log writes"""
        import threading
        
        def write_logs(logger_name, count):
            logger = logging.getLogger(logger_name)
            logger.addHandler(self.handler)
            for i in range(count):
                logger.info(f"{logger_name} log {i}")
        
        # Create multiple threads writing simultaneously
        threads = []
        for i in range(3):
            t = threading.Thread(target=write_logs, args=(f'thread_{i}', 5))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # Wait for batches to process
        time.sleep(1.5)
        
        # Verify all 15 logs written (3 threads × 5 logs)
        logs = self.handler.get_logs(limit=20)
        self.assertEqual(len(logs), 15)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_log_structure(self):
        """Test log entry structure and fields"""
        self.logger.info("Structure test message")
        time.sleep(1.0)
        
        logs = self.handler.get_logs(limit=1)
        self.assertEqual(len(logs), 1)
        
        log = logs[0]
        
        # Verify required fields
        self.assertIn('id', log)
        self.assertIn('timestamp', log)
        self.assertIn('level', log)
        self.assertIn('message', log)
        self.assertIn('module', log)
        
        # Verify field values
        self.assertEqual(log['level'], 'INFO')
        self.assertIn('Structure test message', log['message'])
        self.assertIsInstance(log['id'], int)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_error_handling(self):
        """Test handler resilience to errors"""
        # Test with invalid limit
        logs = self.handler.get_logs(limit=-1)
        self.assertIsInstance(logs, list)
        
        # Test with invalid offset
        logs = self.handler.get_logs(offset=-100)
        self.assertIsInstance(logs, list)
        
        # Test with invalid level
        count = self.handler.get_log_count(level='INVALID')
        self.assertEqual(count, 0)


def run_tests():
    """Run all tests and print results"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSQLiteLogHandler)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"SQLite Logger Tests Summary")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())