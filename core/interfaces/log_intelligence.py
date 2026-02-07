"""
Log Intelligence Interface
==========================
Abstract interfaces for optional log integration into quality tools.

This module defines the contract for log adapters that can enhance
Feng Shui, Gu Wu, and Shi Fu with runtime intelligence. All tools
must work WITHOUT logs (graceful degradation).

Design Pattern: Adapter + Null Object
- Tools depend on interface, not implementation
- NullLogAdapter provides safe default (no-op)
- Real adapters enhance when logs available

Author: P2P Development Team
Version: 1.0.0
Date: 2026-02-07
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class LogAdapterInterface(ABC):
    """
    Abstract interface for log analysis adapters.
    
    All quality tools (Feng Shui, Gu Wu, Shi Fu) depend on this interface,
    not on concrete implementations. This ensures loose coupling and allows
    tools to work with or without logs.
    
    Implementations:
    - NullLogAdapter: Safe default (returns empty results)
    - FengShuiLogAdapter: Architecture violation detection
    - GuWuLogAdapter: Test-runtime correlation
    - ShiFuLogAdapter: Cross-domain pattern detection
    """
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if log data is available.
        
        Returns:
            True if logs are accessible, False otherwise
        """
        pass
    
    @abstractmethod
    def get_error_count(self, hours: int = 24, module: Optional[str] = None) -> int:
        """
        Get count of ERROR level logs.
        
        Args:
            hours: Look back period in hours
            module: Filter by module name (optional)
        
        Returns:
            Number of error logs found
        """
        pass
    
    @abstractmethod
    def get_error_rate(self, hours: int = 24, module: Optional[str] = None) -> float:
        """
        Calculate error rate (errors per hour).
        
        Args:
            hours: Look back period in hours
            module: Filter by module name (optional)
        
        Returns:
            Average errors per hour
        """
        pass
    
    @abstractmethod
    def detect_error_patterns(self, hours: int = 24) -> List[Dict]:
        """
        Detect recurring error patterns.
        
        Args:
            hours: Look back period in hours
        
        Returns:
            List of error patterns with metadata:
            [
                {
                    'pattern': 'AttributeError: NoneType has no attribute connection',
                    'count': 15,
                    'locations': ['module/file.py:45', ...],
                    'severity': 'HIGH',
                    'first_seen': '2026-02-07T10:00:00',
                    'last_seen': '2026-02-07T12:00:00'
                },
                ...
            ]
        """
        pass
    
    @abstractmethod
    def detect_performance_issues(self, threshold_ms: float = 1000, hours: int = 24) -> List[Dict]:
        """
        Detect slow operations from duration_ms logs.
        
        Args:
            threshold_ms: Minimum duration to flag (milliseconds)
            hours: Look back period in hours
        
        Returns:
            List of performance issues:
            [
                {
                    'location': 'module/file.py:123',
                    'avg_duration_ms': 2450.5,
                    'max_duration_ms': 5000.0,
                    'count': 23,
                    'severity': 'HIGH'
                },
                ...
            ]
        """
        pass
    
    @abstractmethod
    def get_module_health(self, module_name: str, hours: int = 24) -> Dict:
        """
        Calculate health metrics for a specific module.
        
        Args:
            module_name: Name of module to analyze
            hours: Look back period in hours
        
        Returns:
            Health metrics:
            {
                'error_count': 15,
                'warning_count': 45,
                'error_rate': 0.625,  # per hour
                'avg_duration_ms': 234.5,
                'health_score': 0.75,  # 0.0-1.0
                'status': 'WARNING'  # OK, WARNING, CRITICAL
            }
        """
        pass


class NullLogAdapter(LogAdapterInterface):
    """
    Null Object implementation of LogAdapterInterface.
    
    Provides safe default behavior when logs are not available.
    All methods return empty/zero values, allowing tools to work
    without logs (graceful degradation).
    
    This is the DEFAULT adapter used when:
    - Log database doesn't exist
    - Log service fails to initialize
    - Feature flag disables log intelligence
    - User hasn't configured logging
    
    Usage:
        # Tools always work, with or without logs
        adapter = NullLogAdapter()  # Safe default
        errors = adapter.get_error_count()  # Returns 0
        patterns = adapter.detect_error_patterns()  # Returns []
    """
    
    def is_available(self) -> bool:
        """
        Null adapter is never available (no real logs).
        
        Returns:
            False (always)
        """
        return False
    
    def get_error_count(self, hours: int = 24, module: Optional[str] = None) -> int:
        """
        Return zero errors (no logs available).
        
        Args:
            hours: Ignored
            module: Ignored
        
        Returns:
            0 (always)
        """
        return 0
    
    def get_error_rate(self, hours: int = 24, module: Optional[str] = None) -> float:
        """
        Return zero error rate (no logs available).
        
        Args:
            hours: Ignored
            module: Ignored
        
        Returns:
            0.0 (always)
        """
        return 0.0
    
    def detect_error_patterns(self, hours: int = 24) -> List[Dict]:
        """
        Return empty pattern list (no logs available).
        
        Args:
            hours: Ignored
        
        Returns:
            [] (always)
        """
        return []
    
    def detect_performance_issues(self, threshold_ms: float = 1000, hours: int = 24) -> List[Dict]:
        """
        Return empty performance issue list (no logs available).
        
        Args:
            threshold_ms: Ignored
            hours: Ignored
        
        Returns:
            [] (always)
        """
        return []
    
    def get_module_health(self, module_name: str, hours: int = 24) -> Dict:
        """
        Return healthy module status (no logs = assume OK).
        
        Args:
            module_name: Ignored
            hours: Ignored
        
        Returns:
            Dict with perfect health metrics
        """
        return {
            'error_count': 0,
            'warning_count': 0,
            'error_rate': 0.0,
            'avg_duration_ms': 0.0,
            'health_score': 1.0,  # Perfect health
            'status': 'OK'
        }


# Convenience function for creating adapters
def create_log_adapter(
    log_service=None,
    enable_logs: bool = True
) -> LogAdapterInterface:
    """
    Factory function to create appropriate log adapter.
    
    This function encapsulates the decision logic for which adapter to use.
    Tools can call this once and get the right adapter automatically.
    
    Args:
        log_service: LoggingService instance (optional)
        enable_logs: Feature flag for log intelligence (default: True)
    
    Returns:
        LogAdapterInterface implementation (Real or Null)
    
    Example:
        # In tool initialization
        from core.interfaces.log_intelligence import create_log_adapter
        
        log_adapter = create_log_adapter()  # Auto-detects
        agent = ArchitectAgent(log_adapter=log_adapter)
        
        # Agent works with OR without logs automatically
    """
    if not enable_logs:
        return NullLogAdapter()
    
    if log_service is None:
        # Try to create log service
        try:
            from modules.log_manager.backend.logging_service import LoggingService
            log_service = LoggingService()
        except Exception:
            # Log service unavailable - use null adapter
            return NullLogAdapter()
    
    # Import real adapter (will be created in Phase 2)
    try:
        from core.services.log_intelligence import LogIntelligenceService
        return LogIntelligenceService(log_service)
    except Exception:
        # Real adapter not available yet - use null adapter
        return NullLogAdapter()