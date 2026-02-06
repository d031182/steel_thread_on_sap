"""
Unit Tests for Gu Wu Observer Pattern

Tests Observer, Subject, ArchitectureMonitor, and TestHealthMonitor.
"""

import pytest
from datetime import datetime

from tests.guwu.observers import (
    TestEvent,
    TestEventType,
    TestObserver,
    TestSubject,
    ArchitectureMonitorObserver,
    ArchitectureViolationError,
    TestHealthMonitorObserver
)


# Test Observer Implementation for testing
class MockObserver(TestObserver):
    """Mock observer for testing"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.events_received = []
    
    def update(self, event: TestEvent):
        self.events_received.append(event)


class TestTestSubject:
    """Test TestSubject (publisher) functionality"""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_attach_observer(self):
        """Test attaching observer to subject"""
        # ARRANGE
        subject = TestSubject()
        observer = MockObserver("test_observer")
        
        # ACT
        subject.attach(observer)
        
        # ASSERT
        assert observer in subject.get_observers()
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_detach_observer(self):
        """Test detaching observer from subject"""
        # ARRANGE
        subject = TestSubject()
        observer = MockObserver("test_observer")
        subject.attach(observer)
        
        # ACT
        subject.detach(observer)
        
        # ASSERT
        assert observer not in subject.get_observers()
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_notify_observers(self):
        """Test notifying all attached observers"""
        # ARRANGE
        subject = TestSubject()
        observer1 = MockObserver("observer1")
        observer2 = MockObserver("observer2")
        subject.attach(observer1)
        subject.attach(observer2)
        
        event = TestEvent(
            event_type=TestEventType.TEST_FAILED,
            timestamp=datetime.now(),
            data={'test_id': 'test_api'}
        )
        
        # ACT
        subject.notify(event)
        
        # ASSERT
        assert len(observer1.events_received) == 1
        assert len(observer2.events_received) == 1
        assert observer1.events_received[0] == event
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_disabled_observer_not_notified(self):
        """Test disabled observers don't receive events"""
        # ARRANGE
        subject = TestSubject()
        observer = MockObserver("observer")
        subject.attach(observer)
        observer.disable()
        
        event = TestEvent(
            event_type=TestEventType.TEST_PASSED,
            timestamp=datetime.now(),
            data={}
        )
        
        # ACT
        subject.notify(event)
        
        # ASSERT
        assert len(observer.events_received) == 0
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_event_filter(self):
        """Test event filtering for specific observer"""
        # ARRANGE
        subject = TestSubject()
        observer = MockObserver("filtered_observer")
        subject.attach(observer)
        
        # Only receive TEST_FAILED events
        subject.set_event_filter(
            "filtered_observer",
            lambda e: e.event_type == TestEventType.TEST_FAILED
        )
        
        # ACT
        subject.notify(TestEvent(TestEventType.TEST_PASSED, datetime.now(), {}))
        subject.notify(TestEvent(TestEventType.TEST_FAILED, datetime.now(), {}))
        
        # ASSERT
        assert len(observer.events_received) == 1
        assert observer.events_received[0].event_type == TestEventType.TEST_FAILED


class TestArchitectureMonitorObserver:
    """Test ArchitectureMonitorObserver"""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_detect_di_violation(self):
        """Test detection of DI violation"""
        # ARRANGE
        monitor = ArchitectureMonitorObserver()
        event = TestEvent(
            event_type=TestEventType.TEST_FAILED,
            timestamp=datetime.now(),
            data={
                'test_id': 'test_api',
                'error': 'AttributeError: .connection not found'
            }
        )
        
        # ACT
        monitor.update(event)
        violations = monitor.get_violations()
        
        # ASSERT
        assert len(violations) == 1
        assert violations[0]['type'] == 'di_violation'
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_strict_mode_raises_exception(self):
        """Test strict mode raises exception on violation"""
        # ARRANGE
        monitor = ArchitectureMonitorObserver(strict_mode=True)
        event = TestEvent(
            event_type=TestEventType.TEST_FAILED,
            timestamp=datetime.now(),
            data={
                'test_id': 'test_bad',
                'error': '.service access detected'
            }
        )
        
        # ACT & ASSERT
        with pytest.raises(ArchitectureViolationError):
            monitor.update(event)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_violation_summary(self):
        """Test getting violation summary"""
        # ARRANGE
        monitor = ArchitectureMonitorObserver()
        
        # Create multiple violations
        for i in range(3):
            event = TestEvent(
                event_type=TestEventType.TEST_FAILED,
                timestamp=datetime.now(),
                data={'test_id': f'test_{i}', 'error': '.connection access'}
            )
            monitor.update(event)
        
        # ACT
        summary = monitor.get_violation_summary()
        
        # ASSERT
        assert summary['total_violations'] == 3
        assert 'di_violation' in summary['by_type']


class TestHealthMonitor:
    """Test TestHealthMonitorObserver"""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_health_score_calculation(self):
        """Test health score calculation"""
        # ARRANGE
        monitor = TestHealthMonitorObserver()
        event = TestEvent(
            event_type=TestEventType.SUITE_FINISHED,
            timestamp=datetime.now(),
            data={
                'total': 100,
                'passed': 95,
                'failed': 5,
                'skipped': 0,
                'duration': 25.0,
                'coverage': 85.0
            }
        )
        
        # ACT
        monitor.update(event)
        score = monitor.get_health_score()
        
        # ASSERT
        assert score > 80  # Good health
        assert score <= 100
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_trend_analysis(self):
        """Test trend analysis over multiple runs"""
        # ARRANGE
        monitor = TestHealthMonitorObserver()
        
        # Simulate degrading performance
        for i in range(3):
            event = TestEvent(
                event_type=TestEventType.SUITE_FINISHED,
                timestamp=datetime.now(),
                data={
                    'total': 100,
                    'passed': 95 - i * 5,  # Pass rate dropping
                    'failed': 5 + i * 5,
                    'skipped': 0,
                    'duration': 30.0,
                    'coverage': 80.0
                }
            )
            monitor.update(event)
        
        # ACT
        trends = monitor.get_trends()
        
        # ASSERT
        assert trends['pass_rate'] == 'degrading'
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_summary(self):
        """Test getting comprehensive health summary"""
        # ARRANGE
        monitor = TestHealthMonitorObserver()
        event = TestEvent(
            event_type=TestEventType.SUITE_FINISHED,
            timestamp=datetime.now(),
            data={
                'total': 50,
                'passed': 48,
                'failed': 2,
                'skipped': 0,
                'duration': 20.0,
                'coverage': 90.0
            }
        )
        monitor.update(event)
        
        # ACT
        summary = monitor.get_summary()
        
        # ASSERT
        assert 'health_score' in summary
        assert 'status' in summary
        assert summary['status'] in ['excellent', 'good', 'fair', 'poor']
        assert 'recommendations' in summary


class TestIntegration:
    """Integration tests for observer pattern"""
    
    @pytest.mark.integration
    def test_multiple_observers_on_single_subject(self):
        """Test multiple observers working together"""
        # ARRANGE
        subject = TestSubject()
        arch_monitor = ArchitectureMonitorObserver()
        health_monitor = TestHealthMonitorObserver()
        
        subject.attach(arch_monitor)
        subject.attach(health_monitor)
        
        # ACT
        # Simulate suite completion
        subject.notify(TestEvent(
            event_type=TestEventType.SUITE_FINISHED,
            timestamp=datetime.now(),
            data={'total': 10, 'passed': 9, 'failed': 1, 'duration': 15.0, 'coverage': 85.0}
        ))
        
        # Simulate test failure with DI violation
        subject.notify(TestEvent(
            event_type=TestEventType.TEST_FAILED,
            timestamp=datetime.now(),
            data={'test_id': 'test_bad', 'error': '.connection access'}
        ))
        
        # ASSERT
        assert arch_monitor.get_event_count() == 2
        assert health_monitor.get_event_count() == 2
        assert len(arch_monitor.get_violations()) == 1
        assert health_monitor.get_health_score() > 0