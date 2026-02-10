"""
Unit tests for LoggingService

Tests service layer business logic and retention policies.

Author: P2P Development Team
Version: 1.0.0
Date: 2026-02-10
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from modules.logger.backend.service import LoggingService


@pytest.fixture
def mock_handler():
    """Create mock SQLite handler"""
    handler = Mock()
    handler.log = AsyncMock()
    handler.flush = AsyncMock()
    handler.get_logs = Mock(return_value=[])
    handler.get_stats = Mock(return_value={'total': 0, 'by_level': {}})
    handler.clear_logs = Mock(return_value=0)
    handler.cleanup_old_logs = Mock(return_value=0)
    return handler


@pytest.fixture
def service(mock_handler):
    """Create service instance with mock handler"""
    return LoggingService(mock_handler)


@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.asyncio
async def test_log_info(service, mock_handler):
    """Test logging INFO level message"""
    # ARRANGE
    message = "Test info message"
    
    # ACT
    await service.log_info(message, module="test", function="test_func", line_no=10)
    
    # ASSERT
    mock_handler.log.assert_called_once()
    call_args = mock_handler.log.call_args[0][0]
    assert call_args['level'] == 'INFO'
    assert call_args['message'] == message
    assert call_args['module'] == 'test'


@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.asyncio
async def test_log_warning(service, mock_handler):
    """Test logging WARNING level message"""
    # ARRANGE
    message = "Test warning"
    
    # ACT
    await service.log_warning(message, module="test")
    
    # ASSERT
    mock_handler.log.assert_called_once()
    call_args = mock_handler.log.call_args[0][0]
    assert call_args['level'] == 'WARNING'
    assert call_args['message'] == message


@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.asyncio
async def test_log_error(service, mock_handler):
    """Test logging ERROR level message"""
    # ARRANGE
    message = "Test error"
    
    # ACT
    await service.log_error(message, module="test")
    
    # ASSERT
    mock_handler.log.assert_called_once()
    call_args = mock_handler.log.call_args[0][0]
    assert call_args['level'] == 'ERROR'
    assert call_args['message'] == message


@pytest.mark.unit
@pytest.mark.fast
def test_get_logs_delegates_to_handler(service, mock_handler):
    """Test get_logs delegates to handler"""
    # ARRANGE
    expected_logs = [{'id': 1, 'message': 'Test'}]
    mock_handler.get_logs.return_value = expected_logs
    
    # ACT
    result = service.get_logs(limit=10, level='INFO')
    
    # ASSERT
    mock_handler.get_logs.assert_called_once_with(limit=10, level='INFO')
    assert result == expected_logs


@pytest.mark.unit
@pytest.mark.fast
def test_get_stats_delegates_to_handler(service, mock_handler):
    """Test get_stats delegates to handler"""
    # ARRANGE
    expected_stats = {'total': 42, 'by_level': {'INFO': 42}}
    mock_handler.get_stats.return_value = expected_stats
    
    # ACT
    result = service.get_stats()
    
    # ASSERT
    mock_handler.get_stats.assert_called_once()
    assert result == expected_stats


@pytest.mark.unit
@pytest.mark.fast
def test_clear_logs_delegates_to_handler(service, mock_handler):
    """Test clear_logs delegates to handler"""
    # ARRANGE
    mock_handler.clear_logs.return_value = 10
    
    # ACT
    result = service.clear_logs()
    
    # ASSERT
    mock_handler.clear_logs.assert_called_once()
    assert result == 10


@pytest.mark.unit
@pytest.mark.fast
def test_cleanup_old_logs_delegates_to_handler(service, mock_handler):
    """Test cleanup_old_logs delegates to handler"""
    # ARRANGE
    mock_handler.cleanup_old_logs.return_value = 5
    
    # ACT
    result = service.cleanup_old_logs()
    
    # ASSERT
    mock_handler.cleanup_old_logs.assert_called_once()
    assert result == 5


@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.asyncio
async def test_log_includes_timestamp(service, mock_handler):
    """Test log entries include ISO timestamp"""
    # ACT
    await service.log_info("Test")
    
    # ASSERT
    mock_handler.log.assert_called_once()
    call_args = mock_handler.log.call_args[0][0]
    assert 'timestamp' in call_args
    # Verify it's ISO format
    datetime.fromisoformat(call_args['timestamp'])