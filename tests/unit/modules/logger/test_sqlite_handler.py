"""
Unit tests for SQLite logging handler

Tests async batch processing, retention policies, and thread safety.

Author: P2P Development Team
Version: 1.0.0
Date: 2026-02-10
"""

import pytest
import asyncio
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from modules.logger.backend.sqlite_handler import SQLiteLogHandler


@pytest.fixture
def temp_db(tmp_path):
    """Create temporary database for testing"""
    db_path = tmp_path / "test_logs.db"
    return str(db_path)


@pytest.fixture
def handler(temp_db):
    """Create handler instance"""
    return SQLiteLogHandler(temp_db)


@pytest.mark.unit
@pytest.mark.fast
def test_handler_initialization(handler, temp_db):
    """Test handler creates database and tables on init"""
    # ARRANGE & ACT (done in fixture)
    
    # ASSERT
    assert Path(temp_db).exists()
    
    # Verify table structure
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='logs'")
    result = cursor.fetchone()
    conn.close()
    
    assert result is not None
    assert result[0] == 'logs'


@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.asyncio
async def test_log_single_entry(handler):
    """Test logging single entry"""
    # ARRANGE
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'level': 'INFO',
        'message': 'Test message',
        'module': 'test_module',
        'function': 'test_function',
        'line_no': 42
    }
    
    # ACT
    await handler.log(log_data)
    await handler.flush()  # Force write
    
    # ASSERT
    logs = handler.get_logs(limit=10)
    assert len(logs) == 1
    assert logs[0]['message'] == 'Test message'
    assert logs[0]['level'] == 'INFO'


@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.asyncio
async def test_batch_processing(handler):
    """Test batch processing with 100+ logs"""
    # ARRANGE
    log_count = 150
    
    # ACT
    for i in range(log_count):
        await handler.log({
            'timestamp': datetime.now().isoformat(),
            'level': 'INFO',
            'message': f'Batch log {i}',
            'module': 'test',
            'function': 'test',
            'line_no': i
        })
    
    await handler.flush()
    
    # ASSERT
    logs = handler.get_logs(limit=200)
    assert len(logs) == log_count


@pytest.mark.unit
@pytest.mark.fast
def test_retention_policy_error_30_days(handler):
    """Test ERROR logs retained for 30 days"""
    # ARRANGE
    conn = sqlite3.connect(handler.db_path)
    cursor = conn.cursor()
    
    # Insert old ERROR log (31 days ago)
    old_date = (datetime.now() - timedelta(days=31)).isoformat()
    cursor.execute("""
        INSERT INTO logs (timestamp, level, message, module, function, line_no)
        VALUES (?, 'ERROR', 'Old error', 'test', 'test', 1)
    """, (old_date,))
    conn.commit()
    conn.close()
    
    # ACT
    deleted = handler.cleanup_old_logs()
    
    # ASSERT
    assert deleted > 0
    logs = handler.get_logs(level='ERROR')
    assert len(logs) == 0


@pytest.mark.unit
@pytest.mark.fast
def test_retention_policy_warning_14_days(handler):
    """Test WARNING logs retained for 14 days"""
    # ARRANGE
    conn = sqlite3.connect(handler.db_path)
    cursor = conn.cursor()
    
    # Insert old WARNING log (15 days ago)
    old_date = (datetime.now() - timedelta(days=15)).isoformat()
    cursor.execute("""
        INSERT INTO logs (timestamp, level, message, module, function, line_no)
        VALUES (?, 'WARNING', 'Old warning', 'test', 'test', 1)
    """, (old_date,))
    conn.commit()
    conn.close()
    
    # ACT
    deleted = handler.cleanup_old_logs()
    
    # ASSERT
    assert deleted > 0
    logs = handler.get_logs(level='WARNING')
    assert len(logs) == 0


@pytest.mark.unit
@pytest.mark.fast
def test_get_logs_with_filters(handler):
    """Test get_logs with level filtering"""
    # ARRANGE
    conn = sqlite3.connect(handler.db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO logs (timestamp, level, message, module, function, line_no)
        VALUES (?, 'ERROR', 'Error message', 'test', 'test', 1)
    """, (datetime.now().isoformat(),))
    cursor.execute("""
        INSERT INTO logs (timestamp, level, message, module, function, line_no)
        VALUES (?, 'INFO', 'Info message', 'test', 'test', 2)
    """, (datetime.now().isoformat(),))
    conn.commit()
    conn.close()
    
    # ACT
    error_logs = handler.get_logs(level='ERROR')
    info_logs = handler.get_logs(level='INFO')
    
    # ASSERT
    assert len(error_logs) == 1
    assert len(info_logs) == 1
    assert error_logs[0]['level'] == 'ERROR'
    assert info_logs[0]['level'] == 'INFO'


@pytest.mark.unit
@pytest.mark.fast
def test_get_stats(handler):
    """Test statistics generation"""
    # ARRANGE
    conn = sqlite3.connect(handler.db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO logs (timestamp, level, message, module, function, line_no)
        VALUES (?, 'ERROR', 'Error', 'test', 'test', 1)
    """, (datetime.now().isoformat(),))
    cursor.execute("""
        INSERT INTO logs (timestamp, level, message, module, function, line_no)
        VALUES (?, 'WARNING', 'Warning', 'test', 'test', 2)
    """, (datetime.now().isoformat(),))
    cursor.execute("""
        INSERT INTO logs (timestamp, level, message, module, function, line_no)
        VALUES (?, 'INFO', 'Info', 'test', 'test', 3)
    """, (datetime.now().isoformat(),))
    conn.commit()
    conn.close()
    
    # ACT
    stats = handler.get_stats()
    
    # ASSERT
    assert stats['total'] == 3
    assert stats['by_level']['ERROR'] == 1
    assert stats['by_level']['WARNING'] == 1
    assert stats['by_level']['INFO'] == 1


@pytest.mark.unit
@pytest.mark.fast
def test_clear_logs(handler):
    """Test clearing all logs"""
    # ARRANGE
    conn = sqlite3.connect(handler.db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO logs (timestamp, level, message, module, function, line_no)
        VALUES (?, 'INFO', 'Test', 'test', 'test', 1)
    """, (datetime.now().isoformat(),))
    conn.commit()
    conn.close()
    
    # ACT
    deleted = handler.clear_logs()
    
    # ASSERT
    assert deleted == 1
    logs = handler.get_logs()
    assert len(logs) == 0


@pytest.mark.unit
@pytest.mark.slow
@pytest.mark.asyncio
async def test_concurrent_logging(handler):
    """Test thread-safety with concurrent logging"""
    # ARRANGE
    concurrent_logs = 50
    
    # ACT
    tasks = []
    for i in range(concurrent_logs):
        task = handler.log({
            'timestamp': datetime.now().isoformat(),
            'level': 'INFO',
            'message': f'Concurrent log {i}',
            'module': 'test',
            'function': 'test',
            'line_no': i
        })
        tasks.append(task)
    
    await asyncio.gather(*tasks)
    await handler.flush()
    
    # ASSERT
    logs = handler.get_logs(limit=100)
    assert len(logs) == concurrent_logs