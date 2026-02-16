"""
Unit Tests: LoggingModeManager
==============================
Tests for dual-mode logging configuration
"""

import pytest
import os
from modules.log.backend.logging_modes import (
    LoggingMode,
    LoggingModeManager
)


@pytest.mark.unit
class TestLoggingMode:
    """Test LoggingMode enum"""
    
    def test_enum_values(self):
        """Test enum has correct values"""
        assert LoggingMode.DEFAULT.value == "default"
        assert LoggingMode.FLIGHT_RECORDER.value == "flight_recorder"
    
    def test_enum_from_string(self):
        """Test creating enum from string"""
        assert LoggingMode("default") == LoggingMode.DEFAULT
        assert LoggingMode("flight_recorder") == LoggingMode.FLIGHT_RECORDER
    
    def test_enum_invalid_value(self):
        """Test invalid enum value raises error"""
        with pytest.raises(ValueError):
            LoggingMode("invalid")


@pytest.mark.unit
class TestLoggingModeManager:
    """Test LoggingModeManager configuration"""
    
    def test_default_mode(self):
        """Test default mode is DEFAULT"""
        manager = LoggingModeManager()
        assert manager.mode == LoggingMode.DEFAULT
        assert manager.is_default()
        assert not manager.is_flight_recorder()
    
    def test_explicit_mode(self):
        """Test explicit mode override"""
        manager = LoggingModeManager(mode=LoggingMode.FLIGHT_RECORDER)
        assert manager.mode == LoggingMode.FLIGHT_RECORDER
        assert manager.is_flight_recorder()
        assert not manager.is_default()
    
    def test_environment_variable(self, monkeypatch):
        """Test mode from environment variable"""
        monkeypatch.setenv('LOGGING_MODE', 'flight_recorder')
        manager = LoggingModeManager()
        assert manager.mode == LoggingMode.FLIGHT_RECORDER
    
    def test_invalid_environment_defaults(self, monkeypatch):
        """Test invalid env value falls back to default"""
        monkeypatch.setenv('LOGGING_MODE', 'invalid')
        manager = LoggingModeManager()
        assert manager.mode == LoggingMode.DEFAULT
    
    def test_mode_setter(self):
        """Test mode can be changed via setter"""
        manager = LoggingModeManager()
        assert manager.mode == LoggingMode.DEFAULT
        
        manager.mode = LoggingMode.FLIGHT_RECORDER
        assert manager.mode == LoggingMode.FLIGHT_RECORDER
    
    def test_mode_setter_validation(self):
        """Test setter validates input type"""
        manager = LoggingModeManager()
        with pytest.raises(ValueError):
            manager.mode = "invalid"


@pytest.mark.unit
class TestLoggingModeFeatures:
    """Test mode-specific feature flags"""
    
    def test_default_mode_features(self):
        """Test DEFAULT mode feature flags"""
        manager = LoggingModeManager(mode=LoggingMode.DEFAULT)
        
        assert not manager.should_log_request_details()
        assert not manager.should_log_response_details()
        assert manager.should_accept_frontend_logs()  # Always true
        assert not manager.should_log_performance_metrics()
        assert manager.get_frontend_log_filter() == 'ERROR'
    
    def test_flight_recorder_mode_features(self):
        """Test FLIGHT_RECORDER mode feature flags"""
        manager = LoggingModeManager(mode=LoggingMode.FLIGHT_RECORDER)
        
        assert manager.should_log_request_details()
        assert manager.should_log_response_details()
        assert manager.should_accept_frontend_logs()
        assert manager.should_log_performance_metrics()
        assert manager.get_frontend_log_filter() == 'ALL'
    
    def test_to_dict_default(self):
        """Test dictionary export for DEFAULT mode"""
        manager = LoggingModeManager(mode=LoggingMode.DEFAULT)
        config = manager.to_dict()
        
        assert config['mode'] == 'default'
        assert config['is_default'] is True
        assert config['is_flight_recorder'] is False
        assert config['features']['request_details'] is False
        assert config['features']['frontend_filter'] == 'ERROR'
    
    def test_to_dict_flight_recorder(self):
        """Test dictionary export for FLIGHT_RECORDER mode"""
        manager = LoggingModeManager(mode=LoggingMode.FLIGHT_RECORDER)
        config = manager.to_dict()
        
        assert config['mode'] == 'flight_recorder'
        assert config['is_default'] is False
        assert config['is_flight_recorder'] is True
        assert config['features']['request_details'] is True
        assert config['features']['frontend_filter'] == 'ALL'