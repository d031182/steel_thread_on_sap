"""
Logging Modes Configuration
============================
Controls logging behavior based on mode (default vs flight_recorder)

Modes:
- DEFAULT: Business-level logging only (production)
- FLIGHT_RECORDER: Comprehensive debugging logs (development)
"""

import os
from enum import Enum
from typing import Optional


class LoggingMode(Enum):
    """Logging mode enumeration"""
    DEFAULT = "default"
    FLIGHT_RECORDER = "flight_recorder"


class LoggingModeManager:
    """
    Manages logging mode configuration
    
    Supports three configuration sources (priority order):
    1. Instance override (runtime)
    2. Environment variable (deployment)
    3. Default (fallback)
    """
    
    def __init__(self, mode: Optional[LoggingMode] = None):
        """
        Initialize logging mode manager
        
        Args:
            mode: Optional initial mode (overrides environment)
        """
        self._mode = mode or self._get_mode_from_env()
    
    def _get_mode_from_env(self) -> LoggingMode:
        """
        Get logging mode from environment variable
        
        Environment: LOGGING_MODE=default|flight_recorder
        Default: default
        """
        mode_str = os.getenv('LOGGING_MODE', 'default').lower()
        try:
            return LoggingMode(mode_str)
        except ValueError:
            return LoggingMode.DEFAULT
    
    @property
    def mode(self) -> LoggingMode:
        """Current logging mode"""
        return self._mode
    
    @mode.setter
    def mode(self, value: LoggingMode):
        """Set logging mode"""
        if not isinstance(value, LoggingMode):
            raise ValueError(f"Invalid mode type: {type(value)}")
        self._mode = value
    
    def is_flight_recorder(self) -> bool:
        """Check if flight recorder mode is active"""
        return self._mode == LoggingMode.FLIGHT_RECORDER
    
    def is_default(self) -> bool:
        """Check if default mode is active"""
        return self._mode == LoggingMode.DEFAULT
    
    def should_log_request_details(self) -> bool:
        """
        Should log full request details? (payload, headers)
        
        DEFAULT: No (business-level only)
        FLIGHT_RECORDER: Yes (everything)
        """
        return self.is_flight_recorder()
    
    def should_log_response_details(self) -> bool:
        """
        Should log full response details? (payload, timing)
        
        DEFAULT: No (business-level only)
        FLIGHT_RECORDER: Yes (everything)
        """
        return self.is_flight_recorder()
    
    def should_accept_frontend_logs(self) -> bool:
        """
        Should accept frontend logs via /api/logs/client?
        
        DEFAULT: Yes (errors only)
        FLIGHT_RECORDER: Yes (everything)
        
        Note: Always returns True - filtering done by log level
        """
        return True
    
    def should_log_performance_metrics(self) -> bool:
        """
        Should log detailed performance metrics?
        
        DEFAULT: No (unless threshold exceeded)
        FLIGHT_RECORDER: Yes (all operations)
        """
        return self.is_flight_recorder()
    
    def get_frontend_log_filter(self) -> str:
        """
        Get frontend log level filter
        
        DEFAULT: ERROR only
        FLIGHT_RECORDER: ALL (INFO, WARN, ERROR)
        """
        return 'ALL' if self.is_flight_recorder() else 'ERROR'
    
    def to_dict(self) -> dict:
        """Export configuration as dictionary"""
        return {
            'mode': self._mode.value,
            'is_flight_recorder': self.is_flight_recorder(),
            'is_default': self.is_default(),
            'features': {
                'request_details': self.should_log_request_details(),
                'response_details': self.should_log_response_details(),
                'frontend_logs': self.should_accept_frontend_logs(),
                'performance_metrics': self.should_log_performance_metrics(),
                'frontend_filter': self.get_frontend_log_filter()
            }
        }


# Global instance (singleton pattern)
logging_mode_manager = LoggingModeManager()