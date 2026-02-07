"""
Unit Tests for Log Intelligence Service
========================================
Tests for optional log analysis integration with quality tools.

Tests cover three scenarios:
1. No logs available (NullLogAdapter)
2. Logs available (LogIntelligenceService)
3. Graceful degradation (service failures)

Author: P2P Development Team
Version: 1.0.0
Date: 2026-02-07
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from core.interfaces.log_intelligence import (
    LogAdapterInterface,
    NullLogAdapter,
    create_log_adapter
)
from core.services.log_intelligence import LogIntelligenceService


class TestNullLogAdapter:
    """Test NullLogAdapter provides safe defaults."""
    
    def test_is_never_available(self):
        """Null adapter is never available."""
        adapter = NullLogAdapter()
        assert adapter.is_available() is False
    
    def test_get_error_count_returns_zero(self):
        """Null adapter returns zero errors."""
        adapter = NullLogAdapter()
        assert adapter.get_error_count() == 0
        assert adapter.get_error_count(hours=48, module='test') == 0
    
    def test_get_error_rate_returns_zero(self):
        """Null adapter returns zero error rate."""
        adapter = NullLogAdapter()
        assert adapter.get_error_rate() == 0.0
        assert adapter.get_error_rate(hours=48, module='test') == 0.0
    
    def test_detect_error_patterns_returns_empty(self):
        """Null adapter returns empty pattern list."""
        adapter = NullLogAdapter()
        patterns = adapter.detect_error_patterns()
        assert patterns == []
        assert isinstance(patterns, list)
    
    def test_detect_performance_issues_returns_empty(self):
        """Null adapter returns empty performance list."""
        adapter = NullLogAdapter()
        issues = adapter.detect_performance_issues()
        assert issues == []
        assert isinstance(issues, list)
    
    def test_get_module_health_returns_perfect(self):
        """Null adapter returns perfect health."""
        adapter = NullLogAdapter()
        health = adapter.get_module_health('test_module')
        
        assert health['error_count'] == 0
        assert health['warning_count'] == 0
        assert health['error_rate'] == 0.0
        assert health['health_score'] == 1.0
        assert health['status'] == 'OK'


class TestLogIntelligenceService:
    """Test LogIntelligenceService with real log analysis."""
    
    @pytest.fixture
    def mock_log_service(self):
        """Create mock log service."""
        service = Mock()
        service.get_log_count.return_value = 100
        service.get_logs.return_value = []
        return service
    
    @pytest.fixture
    def intelligence(self, mock_log_service):
        """Create LogIntelligenceService with mock."""
        return LogIntelligenceService(mock_log_service)
    
    def test_is_available_when_logs_accessible(self, intelligence):
        """Service is available when logs work."""
        assert intelligence.is_available() is True
    
    def test_is_not_available_when_logs_fail(self):
        """Service gracefully handles log failures."""
        failing_service = Mock()
        failing_service.get_log_count.side_effect = Exception("DB error")
        
        intelligence = LogIntelligenceService(failing_service)
        assert intelligence.is_available() is False
    
    def test_get_error_count_no_errors(self, intelligence, mock_log_service):
        """Count errors when none exist."""
        mock_log_service.get_logs.return_value = []
        
        count = intelligence.get_error_count(hours=24)
        assert count == 0
    
    def test_get_error_count_with_errors(self, intelligence, mock_log_service):
        """Count errors when they exist."""
        mock_log_service.get_logs.return_value = [
            {'message': 'Error 1', 'timestamp': '2026-02-07T10:00:00'},
            {'message': 'Error 2', 'timestamp': '2026-02-07T11:00:00'},
            {'message': 'Error 3', 'timestamp': '2026-02-07T12:00:00'}
        ]
        
        count = intelligence.get_error_count(hours=24)
        assert count == 3
    
    def test_get_error_count_filters_by_module(self, intelligence, mock_log_service):
        """Filter errors by module name."""
        mock_log_service.get_logs.return_value = [
            {'message': 'Error in knowledge_graph module', 'logger': 'app', 'timestamp': '2026-02-07T10:00:00'},
            {'message': 'Error in data_products module', 'logger': 'app', 'timestamp': '2026-02-07T11:00:00'},
            {'message': 'Generic error', 'logger': 'knowledge_graph', 'timestamp': '2026-02-07T12:00:00'}
        ]
        
        count = intelligence.get_error_count(hours=24, module='knowledge_graph')
        assert count == 2  # First and third match
    
    def test_get_error_rate(self, intelligence, mock_log_service):
        """Calculate error rate correctly."""
        mock_log_service.get_logs.return_value = [
            {'message': f'Error {i}', 'timestamp': '2026-02-07T10:00:00'}
            for i in range(12)  # 12 errors
        ]
        
        rate = intelligence.get_error_rate(hours=24)
        assert rate == 0.5  # 12 errors / 24 hours = 0.5 per hour
    
    def test_detect_error_patterns_no_errors(self, intelligence, mock_log_service):
        """No patterns when no errors."""
        mock_log_service.get_logs.return_value = []
        
        patterns = intelligence.detect_error_patterns(hours=24)
        assert patterns == []
    
    def test_detect_error_patterns_groups_similar(self, intelligence, mock_log_service):
        """Group similar errors into patterns."""
        mock_log_service.get_logs.return_value = [
            {'message': 'AttributeError: NoneType has no attribute connection at module/file.py:45', 'timestamp': '2026-02-07T10:00:00'},
            {'message': 'AttributeError: NoneType has no attribute connection at module/file.py:45', 'timestamp': '2026-02-07T11:00:00'},
            {'message': 'AttributeError: NoneType has no attribute connection at module/file.py:47', 'timestamp': '2026-02-07T12:00:00'},
            {'message': 'ValueError: Invalid input', 'timestamp': '2026-02-07T13:00:00'}
        ]
        
        patterns = intelligence.detect_error_patterns(hours=24)
        
        assert len(patterns) >= 1  # At least AttributeError pattern
        attr_pattern = [p for p in patterns if 'AttributeError' in p['pattern']][0]
        assert attr_pattern['count'] == 3
        assert attr_pattern['severity'] == 'CRITICAL'  # DI violation
    
    def test_detect_performance_issues_no_issues(self, intelligence, mock_log_service):
        """No issues when no slow operations."""
        mock_log_service.get_logs.return_value = []
        
        issues = intelligence.detect_performance_issues(threshold_ms=1000, hours=24)
        assert issues == []
    
    def test_detect_performance_issues_finds_slow_ops(self, intelligence, mock_log_service):
        """Find slow operations from logs."""
        mock_log_service.get_logs.return_value = [
            {'message': 'Slow query at module/query.py:123', 'duration_ms': 2500, 'timestamp': '2026-02-07T10:00:00'},
            {'message': 'Slow query at module/query.py:123', 'duration_ms': 3000, 'timestamp': '2026-02-07T11:00:00'},
            {'message': 'Fast operation at module/fast.py:10', 'duration_ms': 500, 'timestamp': '2026-02-07T12:00:00'}
        ]
        
        issues = intelligence.detect_performance_issues(threshold_ms=1000, hours=24)
        
        assert len(issues) == 1
        assert issues[0]['location'] == 'module/query.py:123'
        assert issues[0]['count'] == 2
        assert issues[0]['avg_duration_ms'] == 2750.0
        assert issues[0]['max_duration_ms'] == 3000.0
    
    def test_get_module_health_no_issues(self, intelligence, mock_log_service):
        """Module health is perfect when no issues."""
        mock_log_service.get_logs.return_value = []
        intelligence.get_error_count = Mock(return_value=0)
        
        health = intelligence.get_module_health('test_module', hours=24)
        
        assert health['error_count'] == 0
        assert health['warning_count'] == 0
        assert health['health_score'] == 1.0
        assert health['status'] == 'OK'
    
    def test_get_module_health_with_errors(self, intelligence, mock_log_service):
        """Module health degrades with errors."""
        # Mock error count
        intelligence.get_error_count = Mock(return_value=10)
        
        # Mock warnings
        mock_log_service.get_logs.return_value = [
            {'message': 'Warning in test_module', 'logger': 'test_module', 'duration_ms': None}
            for _ in range(5)
        ]
        
        health = intelligence.get_module_health('test_module', hours=24)
        
        assert health['error_count'] == 10
        assert health['warning_count'] == 5
        assert health['health_score'] < 1.0
        assert health['status'] in ['WARNING', 'CRITICAL']
    
    def test_graceful_degradation_on_error(self, intelligence, mock_log_service):
        """Service degrades gracefully when operations fail."""
        mock_log_service.get_logs.side_effect = Exception("DB error")
        
        # Should return safe defaults, not crash
        assert intelligence.get_error_count() == 0
        assert intelligence.detect_error_patterns() == []
        assert intelligence.detect_performance_issues() == []


class TestCreateLogAdapter:
    """Test factory function for creating adapters."""
    
    def test_creates_null_when_disabled(self):
        """Create NullLogAdapter when feature disabled."""
        adapter = create_log_adapter(enable_logs=False)
        
        assert isinstance(adapter, NullLogAdapter)
        assert adapter.is_available() is False
    
    def test_creates_null_when_no_service(self):
        """Create NullLogAdapter when log service unavailable."""
        with patch('modules.log_manager.backend.logging_service.LoggingService', side_effect=Exception("No logs")):
            adapter = create_log_adapter(log_service=None, enable_logs=True)
            
            assert isinstance(adapter, NullLogAdapter)
    
    def test_creates_real_when_service_provided(self):
        """Create LogIntelligenceService when service provided."""
        mock_service = Mock()
        mock_service.get_log_count.return_value = 100
        
        adapter = create_log_adapter(log_service=mock_service, enable_logs=True)
        
        assert isinstance(adapter, LogIntelligenceService)
        assert adapter.is_available() is True
    
    def test_creates_real_when_service_available(self):
        """Create LogIntelligenceService when service auto-detected."""
        with patch('modules.log_manager.backend.logging_service.LoggingService') as MockService:
            mock_instance = Mock()
            mock_instance.get_log_count.return_value = 100
            MockService.return_value = mock_instance
            
            adapter = create_log_adapter(enable_logs=True)
            
            assert isinstance(adapter, LogIntelligenceService)


class TestLogIntelligenceIntegration:
    """Integration tests with tools (demonstrate usage)."""
    
    def test_tool_works_without_logs(self):
        """Tools work with NullLogAdapter (no logs)."""
        # Simulate tool initialization
        log_adapter = NullLogAdapter()
        
        # Tool can call all methods safely
        assert log_adapter.get_error_count() == 0
        assert log_adapter.detect_error_patterns() == []
        
        # Tool logic continues normally
        violations = []  # Core analysis
        if log_adapter.is_available():
            violations.extend(log_adapter.detect_error_patterns())  # Never called
        
        assert violations == []  # Works without logs
    
    def test_tool_enhanced_with_logs(self):
        """Tools enhanced with LogIntelligenceService (logs available)."""
        # Simulate tool initialization
        mock_service = Mock()
        mock_service.get_log_count.return_value = 100
        mock_service.get_logs.return_value = [
            {'message': 'AttributeError: connection', 'timestamp': '2026-02-07T10:00:00'},
            {'message': 'AttributeError: connection', 'timestamp': '2026-02-07T11:00:00'}
        ]
        
        log_adapter = LogIntelligenceService(mock_service)
        
        # Tool can call all methods
        violations = []  # Core analysis
        if log_adapter.is_available():
            patterns = log_adapter.detect_error_patterns()
            violations.extend(patterns)  # Enhanced with runtime data
        
        assert len(violations) >= 1  # Enhanced with logs
    
    def test_tool_degrades_gracefully_on_failure(self):
        """Tools degrade gracefully when log operations fail."""
        # Simulate log service failure
        failing_service = Mock()
        failing_service.get_log_count.side_effect = Exception("DB error")
        
        log_adapter = LogIntelligenceService(failing_service)
        
        # Tool checks availability first
        violations = []  # Core analysis
        if log_adapter.is_available():  # Returns False
            violations.extend(log_adapter.detect_error_patterns())  # Never called
        
        assert violations == []  # Degraded gracefully


# Pytest markers
pytestmark = [
    pytest.mark.unit,
    pytest.mark.fast
]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])