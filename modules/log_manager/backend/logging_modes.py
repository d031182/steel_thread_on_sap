"""
Logging Modes Configuration
============================
Controls logging behavior based on mode (default vs flight_recorder)

This module provides the LoggingModeManager that determines how verbose
logging should be. Two modes are supported:

1. DEFAULT Mode (Production):
   - Business-level activities only (auth, API calls, errors)
   - Minimal overhead, audit-focused
   - ~500 logs/day for 10 users

2. FLIGHT_RECORDER Mode (Debug):
   - Everything logged (clicks, console, network, full payloads)
   - Complete E2E tracing for debugging
   - ~50,000 logs/day per active debug session
   - Frontend activities sent to backend via /api/logs/client

Configuration Priority:
1. Runtime override (via API)
2. Environment variable (LOGGING_MODE)
3. Default (production mode)

Author: P2P Development Team
Version: 1.0.0
Date: 2026-02-07
"""

import os
from enum import Enum
from typing import Optional


class LoggingMode(Enum):
    """Logging mode enumeration"""
    DEFAULT = "default"
    FLIGHT_RECORDER = "flight_recorder"
    
    @classmethod
    def from_string(cls, value: str) -> 'LoggingMode':
        """
        Convert string to LoggingMode enum.
        
        Args:
            value: Mode string ("default" or "flight_recorder")
        
        Returns:
            LoggingMode enum value
        
        Raises:
            ValueError: If value is invalid
        """
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(
                f"Invalid logging mode: {value}. "
                f"Must be 'default' or 'flight_recorder'"
            )


class LoggingModeManager:
    """
    Manages logging mode configuration and behavior.
    
    This singleton-like class controls how verbose logging should be
    throughout the application. It determines:
    - Whether to log request/response details
    - Whether to accept frontend logs
    - Whether to log performance metrics
    - Log retention policies
    
    Usage:
        from modules.log_manager.backend.logging_modes import logging_mode_manager
        
        if logging_mode_manager.is_flight_recorder():
            # Log detailed information
            logger.info("Request payload", extra={'payload': request.json})
        else:
            # Log business-level only
            logger.info("API call: POST /api/data-products")
    """
    
    def __init__(self):
        """Initialize logging mode manager"""
        self._mode = self._get_mode_from_env()
        self._runtime_override: Optional[LoggingMode] = None
    
    def _get_mode_from_env(self) -> LoggingMode:
        """
        Get logging mode from environment variable.
        
        Reads LOGGING_MODE environment variable. If not set or invalid,
        defaults to DEFAULT mode (production).
        
        Returns:
            LoggingMode enum value
        """
        mode_str = os.getenv('LOGGING_MODE', 'default').lower()
        try:
            return LoggingMode(mode_str)
        except ValueError:
            # Invalid value in env var - log warning and use default
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Invalid LOGGING_MODE in environment: {mode_str}. "
                f"Using default mode."
            )
            return LoggingMode.DEFAULT
    
    @property
    def mode(self) -> LoggingMode:
        """
        Current logging mode (with runtime override support).
        
        Returns:
            Active LoggingMode (runtime override takes precedence)
        """
        return self._runtime_override or self._mode
    
    def set_mode(self, mode: LoggingMode) -> None:
        """
        Set logging mode at runtime.
        
        This override persists until application restart or cleared.
        Useful for temporary debug sessions.
        
        Args:
            mode: New logging mode to activate
        """
        self._runtime_override = mode
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"Logging mode changed to: {mode.value} "
            f"(runtime override active)"
        )
    
    def clear_override(self) -> None:
        """
        Clear runtime mode override.
        
        Returns to environment-configured mode.
        """
        if self._runtime_override:
            old_mode = self._runtime_override.value
            self._runtime_override = None
            
            import logging
            logger = logging.getLogger(__name__)
            logger.info(
                f"Logging mode override cleared. "
                f"Was: {old_mode}, Now: {self._mode.value}"
            )
    
    def is_flight_recorder(self) -> bool:
        """
        Check if flight recorder mode is active.
        
        Returns:
            True if FLIGHT_RECORDER mode, False if DEFAULT mode
        """
        return self.mode == LoggingMode.FLIGHT_RECORDER
    
    def is_default(self) -> bool:
        """
        Check if default mode is active.
        
        Returns:
            True if DEFAULT mode, False if FLIGHT_RECORDER mode
        """
        return self.mode == LoggingMode.DEFAULT
    
    # Behavior Methods - What to log based on mode
    
    def should_log_request_details(self) -> bool:
        """
        Should log full request details (headers, payload)?
        
        DEFAULT: No (only endpoint and user)
        FLIGHT_RECORDER: Yes (full details for debugging)
        
        Returns:
            True if should log request details
        """
        return self.is_flight_recorder()
    
    def should_log_response_details(self) -> bool:
        """
        Should log full response details (payload, size)?
        
        DEFAULT: No (only status code and duration)
        FLIGHT_RECORDER: Yes (full details for debugging)
        
        Returns:
            True if should log response details
        """
        return self.is_flight_recorder()
    
    def should_accept_frontend_logs(self) -> bool:
        """
        Should accept frontend logs via /api/logs/client?
        
        DEFAULT: Errors only (for production error reporting)
        FLIGHT_RECORDER: All logs (clicks, console, network)
        
        Note: This returns True for both modes, but filtering
        happens at the endpoint level based on log level.
        
        Returns:
            True (always accept, endpoint filters by mode)
        """
        return True
    
    def should_log_frontend_activity(self, level: str) -> bool:
        """
        Should log frontend activity based on level?
        
        DEFAULT: ERROR only
        FLIGHT_RECORDER: All levels (INFO, WARNING, ERROR)
        
        Args:
            level: Log level (INFO, WARNING, ERROR)
        
        Returns:
            True if should log this frontend activity
        """
        if self.is_flight_recorder():
            return True
        
        # Default mode: Only errors from frontend
        return level.upper() == 'ERROR'
    
    def should_log_performance_metrics(self) -> bool:
        """
        Should log detailed performance metrics?
        
        DEFAULT: No (unless threshold exceeded)
        FLIGHT_RECORDER: Yes (all operations)
        
        Returns:
            True if should log performance metrics
        """
        return self.is_flight_recorder()
    
    def get_performance_threshold_ms(self) -> float:
        """
        Get performance threshold for logging slow operations.
        
        DEFAULT: 1000ms (log only slow operations)
        FLIGHT_RECORDER: 0ms (log all operations)
        
        Returns:
            Threshold in milliseconds
        """
        return 0.0 if self.is_flight_recorder() else 1000.0
    
    def get_frontend_log_retention_days(self) -> int:
        """
        Get retention period for frontend logs.
        
        DEFAULT: 7 days (standard INFO retention)
        FLIGHT_RECORDER: 2 days (high volume, shorter retention)
        
        Returns:
            Retention period in days
        """
        return 2 if self.is_flight_recorder() else 7
    
    # Status Methods
    
    def get_status(self) -> dict:
        """
        Get current logging mode status.
        
        Returns:
            Status dictionary with mode details
        """
        return {
            'mode': self.mode.value,
            'is_flight_recorder': self.is_flight_recorder(),
            'is_default': self.is_default(),
            'has_runtime_override': self._runtime_override is not None,
            'env_mode': self._mode.value,
            'behavior': {
                'log_request_details': self.should_log_request_details(),
                'log_response_details': self.should_log_response_details(),
                'log_performance_metrics': self.should_log_performance_metrics(),
                'performance_threshold_ms': self.get_performance_threshold_ms(),
                'frontend_log_retention_days': self.get_frontend_log_retention_days()
            }
        }


# Global singleton instance
# Import this in other modules: from modules.log_manager.backend.logging_modes import logging_mode_manager
logging_mode_manager = LoggingModeManager()