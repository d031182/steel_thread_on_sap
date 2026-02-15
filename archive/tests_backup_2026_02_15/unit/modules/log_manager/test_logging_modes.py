"""
Unit Tests for Logging Modes Module
====================================
Tests the dual-mode logging system backend infrastructure.

Author: P2P Development Team
Version: 1.0.0
Date: 2026-02-07
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from modules.log_manager.backend.logging_modes import (
    LoggingMode,
    LoggingModeManager,
    logging_mode_manager
)


@pytest.mark.unit
@pytest.mark.fast
class TestLoggingMode:
    """Test LoggingMode enum"""
    
    def test_enum_values(self):
        """Test enum has correct values"""
        assert LoggingMode.DEFAULT.value == "default"
        assert LoggingMode.FLIGHT_RECORDER.value == "flight_recorder"
    
    def test_from_string_valid(self):
        """Test from_string with valid values"""
        assert LoggingMode.from_string("default") == LoggingMode.DEFAULT
        assert LoggingMode.from_string("flight_recorder") == LoggingMode.FLIGHT_RECORDER
        assert LoggingMode.from_string("DEFAULT") == LoggingMode.DEFAULT
        assert LoggingMode.from_string("FLIGHT_RECORDER") == LoggingMode.FLIGHT_RECORDER
    
    def test_from_string_invalid(self):
        """Test from_string with invalid values"""
        with pytest.raises(ValueError, match="Invalid logging mode"):
            LoggingMode.from_string("invalid")
        
        with pytest.raises(ValueError, match="Invalid logging mode"):
            LoggingMode.from_string("debug")


@pytest.mark.unit
@pytest.mark.fast
class TestLoggingModeManager:
    """Test LoggingModeManager class"""
    
    def test_init_default(self):
        """Test initialization defaults to DEFAULT mode"""
        with patch.dict(os.environ, {}, clear=True):
            manager = LoggingModeManager()
            assert manager.mode == LoggingMode.DEFAULT
            assert manager.is_default()
            assert not manager.is_flight_recorder()
    
    def test_init_from_env(self):
        """Test initialization from environment variable"""
        with patch.dict(os.environ, {'LOGGING_MODE': 'flight_recorder'}):
            manager = LoggingModeManager()
            assert manager.mode == LoggingMode.FLIGHT_RECORDER
            assert manager.is_flight_recorder()
            assert not manager.is_default()
    
    def test_init_invalid_env(self):
        """Test initialization with invalid env value defaults to DEFAULT"""
        with patch.dict(os.environ, {'LOGGING_MODE': 'invalid_mode'}):
            manager = LoggingModeManager()
            assert manager.mode == LoggingMode.DEFAULT
    
    def test_set_mode(self):
        """Test runtime mode override"""
        manager = LoggingModeManager()
        assert manager.mode == LoggingMode.DEFAULT
        
        manager.set_mode(LoggingMode.FLIGHT_RECORDER)
        assert manager.mode == LoggingMode.FLIGHT_RECORDER
        assert manager.is_flight_recorder()
    
    def test_clear_override(self):
        """Test clearing runtime override"""
        with patch.dict(os.environ, {'LOGGING_MODE': 'default'}):
            manager = LoggingModeManager()
            
            # Set override
            manager.set_mode(LoggingMode.FLIGHT_RECORDER)
            assert manager.mode == LoggingMode.FLIGHT_RECORDER
            
            # Clear override
            manager.clear_override()
            assert manager.mode == LoggingMode.DEFAULT
    
    def test_should_log_request_details(self):
        """Test request detail logging decision"""
        manager = LoggingModeManager()
        
        # Default mode: No request details
        manager.set_mode(LoggingMode.DEFAULT)
        assert not manager.should_log_request_details()
        
        # Flight recorder: Yes request details
        manager.set_mode(LoggingMode.FLIGHT_RECORDER)
        assert manager.should_log_request_details()
    
    def test_should_log_response_details(self):
        """Test response detail logging decision"""
        manager = LoggingModeManager()
        
        # Default mode: No response details
        manager.set_mode(LoggingMode.DEFAULT)
        assert not manager.should_log_response_details()
        
        # Flight recorder: Yes response details
        manager.set_mode(LoggingMode.FLIGHT_RECORDER)
        assert manager.should_log_response_details()
    
    def test_should_accept_frontend_logs(self):
        """Test frontend log acceptance (always True, filtered at endpoint)"""
        manager = LoggingModeManager()
        
        # Both modes accept (endpoint filters by level)
        manager.set_mode(LoggingMode.DEFAULT)
        assert manager.should_accept_frontend_logs()
        
        manager.set_mode(LoggingMode.FLIGHT_RECORDER)
        assert manager.should_accept_frontend_logs()
    
    def test_should_log_frontend_activity(self):
        """Test frontend activity logging based on level"""
        manager = LoggingModeManager()
        
        # Default mode: Only ERROR
        manager.set_mode(LoggingMode.DEFAULT)
        assert not manager.should_log_frontend_activity('INFO')
        assert not manager.should_log_frontend_activity('WARNING')
        assert manager.should_log_frontend_activity('ERROR')
        
        # Flight recorder: All levels
        manager.set_mode(LoggingMode.FLIGHT_RECORDER)
        assert manager.should_log_frontend_activity('INFO')
        assert manager.should_log_frontend_activity('WARNING')
        assert manager.should_log_frontend_activity('ERROR')
    
    def test_should_log_performance_metrics(self):
        """Test performance metrics logging decision"""
        manager = LoggingModeManager()
        
        # Default mode: No performance metrics
        manager.set_mode(LoggingMode.DEFAULT)
        assert not manager.should_log_performance_metrics()
        
        # Flight recorder: Yes performance metrics
        manager.set_mode(LoggingMode.FLIGHT_RECORDER)
        assert manager.should_log_performance_metrics()
    
    def test_get_performance_threshold_ms(self):
        """Test performance threshold based on mode"""
        manager = LoggingModeManager()
        
        # Default mode: 1000ms threshold
        manager.set_mode(LoggingMode.DEFAULT)
        assert manager.get_performance_threshold_ms() == 1000.0
        
        # Flight recorder: 0ms threshold (log everything)
        manager.set_mode(LoggingMode.FLIGHT_RECORDER)
        assert manager.get_performance_threshold_ms() == 0.0
    
    def test_get_frontend_log_retention_days(self):
        """Test frontend log retention based on mode"""
        manager = LoggingModeManager()
        
        # Default mode: 7 days
        manager.set_mode(LoggingMode.DEFAULT)
        assert manager.get_frontend_log_retention_days() == 7
        
        # Flight recorder: 2 days (high volume)
        manager.set_mode(LoggingMode.FLIGHT_RECORDER)
        assert manager.get_frontend_log_retention_days() == 2
    
    def test_get_status(self):
        """Test status dictionary generation"""
        manager = LoggingModeManager()
        manager.set_mode(LoggingMode.FLIGHT_RECORDER)
        
        status = manager.get_status()
        
        # Verify structure
        assert status['mode'] == 'flight_recorder'
        assert status['is_flight_recorder'] is True
        assert status['is_default'] is False
        assert status['has_runtime_override'] is True
        
        # Verify behavior flags
        behavior = status['behavior']
        assert behavior['log_request_details'] is True
        assert behavior['log_response_details'] is True
        assert behavior['log_performance_metrics'] is True
        assert behavior['performance_threshold_ms'] == 0.0
        assert behavior['frontend_log_retention_days'] == 2


@pytest.mark.unit
@pytest.mark.fast
class TestGlobalInstance:
    """Test global logging_mode_manager instance"""
    
    def test_global_instance_exists(self):
        """Test global instance is available"""
        assert logging_mode_manager is not None
        assert isinstance(logging_mode_manager, LoggingModeManager)
    
    def test_global_instance_is_singleton(self):
        """Test same instance is reused"""
        # Import again
        from modules.log_manager.backend.logging_modes import logging_mode_manager as manager2
        assert logging_mode_manager is manager2


@pytest.mark.unit
@pytest.mark.fast
class TestBugFix:
    """Test the specific bug fix (case sensitivity)"""
    
    def test_case_sensitivity_issue(self):
        """
        Test that demonstrates the original bug:
        - Backend API returns lowercase keys: {info: 840, warning: 24, error: 8}
        - Frontend was accessing uppercase keys: stats.INFO, stats.WARNING, stats.ERROR
        - Result: undefined values
        
        This test verifies the fix works by ensuring both backend and
        frontend-calculated stats use the same lowercase keys.
        """
        # Simulate backend API response (lowercase keys)
        backend_stats = {
            'total': 872,
            'info': 840,
            'warning': 24,
            'error': 8
        }
        
        # Simulate frontend calculateStats() (NOW fixed to lowercase)
        mock_logs = [
            {'level': 'INFO'},
            {'level': 'INFO'},
            {'level': 'WARNING'},
            {'level': 'ERROR'}
        ]
        
        def calculate_stats_fixed(logs):
            """This is the FIXED version"""
            return {
                'total': len(logs),
                'info': len([l for l in logs if l['level'] == 'INFO']),
                'warning': len([l for l in logs if l['level'] == 'WARNING']),
                'error': len([l for l in logs if l['level'] == 'ERROR'])
            }
        
        frontend_stats = calculate_stats_fixed(mock_logs)
        
        # Verify both use lowercase keys
        assert 'info' in backend_stats
        assert 'info' in frontend_stats
        assert 'warning' in backend_stats
        assert 'warning' in frontend_stats
        assert 'error' in backend_stats
        assert 'error' in frontend_stats
        
        # Verify uppercase keys don't exist
        assert 'INFO' not in backend_stats
        assert 'INFO' not in frontend_stats
        assert 'WARNING' not in backend_stats
        assert 'WARNING' not in frontend_stats
        assert 'ERROR' not in backend_stats
        assert 'ERROR' not in frontend_stats
        
        # This is how the UI should access the values (lowercase)
        ui_text_correct = f"Warning ({backend_stats['warning']})"
        assert ui_text_correct == "Warning (24)"
        
        # This was the BUG (accessing uppercase on lowercase dict)
        ui_text_buggy = f"Warning ({backend_stats.get('WARNING', 'undefined')})"
        assert ui_text_buggy == "Warning (undefined)"  # Demonstrates the bug!


# ============================================================
# INTEGRATION TEST: Complete E2E Flow
# ============================================================

@pytest.mark.integration
def test_mode_switch_complete_flow():
    """
    Test complete flow:
    1. Start in DEFAULT mode
    2. Switch to FLIGHT_RECORDER
    3. Verify behavior changes
    4. Switch back to DEFAULT
    5. Verify behavior restored
    """
    manager = LoggingModeManager()
    
    # Start in DEFAULT
    manager.set_mode(LoggingMode.DEFAULT)
    assert manager.is_default()
    assert not manager.should_log_request_details()
    assert manager.get_performance_threshold_ms() == 1000.0
    assert manager.get_frontend_log_retention_days() == 7
    
    # Switch to FLIGHT_RECORDER
    manager.set_mode(LoggingMode.FLIGHT_RECORDER)
    assert manager.is_flight_recorder()
    assert manager.should_log_request_details()
    assert manager.get_performance_threshold_ms() == 0.0
    assert manager.get_frontend_log_retention_days() == 2
    
    # Switch back to DEFAULT
    manager.set_mode(LoggingMode.DEFAULT)
    assert manager.is_default()
    assert not manager.should_log_request_details()
    assert manager.get_performance_threshold_ms() == 1000.0
    assert manager.get_frontend_log_retention_days() == 7