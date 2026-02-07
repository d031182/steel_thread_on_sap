"""
Base Observer Pattern Components for Gu Wu

Provides the core Observer pattern interface and event system.
Following GoF Observer pattern for event-driven architecture monitoring.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TestEventType(Enum):
    """Types of test events that can be observed"""
    
    # Test execution events
    TEST_STARTED = "test_started"
    TEST_PASSED = "test_passed"
    TEST_FAILED = "test_failed"
    TEST_SKIPPED = "test_skipped"
    
    # Test suite events
    SUITE_STARTED = "suite_started"
    SUITE_FINISHED = "suite_finished"
    
    # Architecture events
    DI_VIOLATION_DETECTED = "di_violation_detected"
    MODULE_COUPLING_CHANGED = "module_coupling_changed"
    ARCHITECTURE_DRIFT_DETECTED = "architecture_drift_detected"
    
    # Quality events
    COVERAGE_DROPPED = "coverage_dropped"
    FLAKINESS_INCREASED = "flakiness_increased"
    PERFORMANCE_DEGRADED = "performance_degraded"
    
    # Self-healing events
    AUTO_FIX_APPLIED = "auto_fix_applied"
    LEARNING_EVENT = "learning_event"


@dataclass
class TestEvent:
    """
    Event that occurs during testing
    
    This is the message passed from Subject to Observers.
    Contains all context needed for observers to react appropriately.
    """
    
    event_type: TestEventType
    timestamp: datetime
    data: Dict[str, Any]
    source: str = "unknown"           # Which component generated event
    severity: str = "info"            # info, warning, error, critical
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'source': self.source,
            'severity': self.severity
        }
    
    def __repr__(self) -> str:
        return (
            f"TestEvent(type={self.event_type.value}, "
            f"source={self.source}, severity={self.severity})"
        )


class TestObserver(ABC):
    """
    Abstract Observer (GoF Observer Pattern)
    
    Observers subscribe to TestSubject and react to events.
    Each observer implements its own reaction logic.
    
    Benefits:
    - Loose coupling: Observers don't know about each other
    - Easy to add new observers without changing existing code
    - Can enable/disable observers at runtime
    - Each observer has single responsibility
    
    Usage:
        class MyObserver(TestObserver):
            def update(self, event: TestEvent):
                if event.event_type == TestEventType.TEST_FAILED:
                    print(f"Test failed: {event.data['test_id']}")
    """
    
    def __init__(self, name: str):
        """
        Initialize observer
        
        Args:
            name: Human-readable observer name (for logging)
        """
        self.name = name
        self.enabled = True
        self._event_count = 0
    
    @abstractmethod
    def update(self, event: TestEvent):
        """
        React to event from subject
        
        This is called by the Subject when an event occurs.
        Each observer implements its own reaction logic.
        
        Args:
            event: TestEvent containing event details
        """
        pass
    
    def enable(self):
        """Enable this observer"""
        self.enabled = True
        logger.info(f"[Observer] {self.name} enabled")
    
    def disable(self):
        """Disable this observer"""
        self.enabled = False
        logger.info(f"[Observer] {self.name} disabled")
    
    def get_event_count(self) -> int:
        """Get number of events this observer has processed"""
        return self._event_count
    
    def _record_event(self):
        """Internal: Track that event was processed"""
        self._event_count += 1


class TestSubject:
    """
    Subject/Observable (GoF Observer Pattern)
    
    Maintains list of observers and notifies them of events.
    This is the "publisher" in pub/sub terminology.
    
    Benefits:
    - Centralized event distribution
    - Observers can subscribe/unsubscribe dynamically
    - Subject doesn't need to know observer details
    - Can filter which observers get which events
    
    Usage:
        subject = TestSubject()
        subject.attach(MyObserver("monitor1"))
        subject.attach(AnotherObserver("monitor2"))
        
        # Later when event occurs:
        subject.notify(TestEvent(
            event_type=TestEventType.TEST_FAILED,
            timestamp=datetime.now(),
            data={'test_id': 'test_api'}
        ))
    """
    
    def __init__(self):
        """Initialize subject with empty observer list"""
        self._observers: List[TestObserver] = []
        self._event_filters: Dict[str, Callable[[TestEvent], bool]] = {}
        self._event_history: List[TestEvent] = []
        self._max_history = 1000  # Keep last 1000 events
    
    def attach(self, observer: TestObserver):
        """
        Attach observer to receive events
        
        Args:
            observer: Observer to attach
        """
        if observer not in self._observers:
            self._observers.append(observer)
            logger.info(f"[Subject] Attached observer: {observer.name}")
    
    def detach(self, observer: TestObserver):
        """
        Detach observer from receiving events
        
        Args:
            observer: Observer to detach
        """
        if observer in self._observers:
            self._observers.remove(observer)
            logger.info(f"[Subject] Detached observer: {observer.name}")
    
    def notify(self, event: TestEvent):
        """
        Notify all observers of event
        
        This is the core of the Observer pattern - when something
        interesting happens, tell all interested parties.
        
        Args:
            event: TestEvent to send to observers
        """
        # Store in history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        logger.debug(
            f"[Subject] Notifying {len(self._observers)} observers "
            f"of event: {event.event_type.value}"
        )
        
        # Notify each enabled observer
        for observer in self._observers:
            if not observer.enabled:
                continue
            
            # Check event filter if configured
            if observer.name in self._event_filters:
                filter_func = self._event_filters[observer.name]
                if not filter_func(event):
                    continue
            
            try:
                observer.update(event)
                observer._record_event()
            except Exception as e:
                logger.error(
                    f"[Subject] Observer {observer.name} failed: {e}",
                    exc_info=True
                )
    
    def set_event_filter(
        self,
        observer_name: str,
        filter_func: Callable[[TestEvent], bool]
    ):
        """
        Set event filter for specific observer
        
        Allows filtering which events an observer receives.
        Useful for performance (reduce unnecessary notifications).
        
        Args:
            observer_name: Name of observer to filter
            filter_func: Function that returns True if observer should receive event
        
        Example:
            # Only notify about failed tests
            subject.set_event_filter(
                "my_observer",
                lambda e: e.event_type == TestEventType.TEST_FAILED
            )
        """
        self._event_filters[observer_name] = filter_func
        logger.info(f"[Subject] Set event filter for: {observer_name}")
    
    def get_observers(self) -> List[TestObserver]:
        """Get list of attached observers"""
        return self._observers.copy()
    
    def get_event_history(self, limit: int = 100) -> List[TestEvent]:
        """
        Get recent event history
        
        Args:
            limit: Maximum number of events to return
        
        Returns:
            List of recent events (most recent last)
        """
        return self._event_history[-limit:]
    
    def clear_event_history(self):
        """Clear event history (e.g., at session start)"""
        self._event_history = []
        logger.info("[Subject] Event history cleared")
    
    def get_observer_stats(self) -> Dict[str, Dict]:
        """
        Get statistics about observer activity
        
        Returns:
            Dict mapping observer name to stats
        """
        return {
            observer.name: {
                'enabled': observer.enabled,
                'events_processed': observer.get_event_count()
            }
            for observer in self._observers
        }