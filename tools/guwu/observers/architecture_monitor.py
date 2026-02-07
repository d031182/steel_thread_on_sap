"""
Architecture Monitor Observer

Monitors for architecture violations during test execution.
Detects DI violations, module coupling issues, and architecture drift.
"""

from typing import Dict, List, Set
from datetime import datetime
import logging
import re

from .base import TestObserver, TestEvent, TestEventType

logger = logging.getLogger(__name__)


class ArchitectureMonitorObserver(TestObserver):
    """
    Monitor architecture health during testing
    
    Watches for:
    - DI violations (.connection, .service, .db_path direct access)
    - Module coupling violations (direct module imports)
    - Architecture drift (tests coupled to implementation)
    
    When violations detected:
    - Logs warning
    - Tracks violation count
    - Can trigger auto-fix (in future phases)
    
    Usage:
        monitor = ArchitectureMonitorObserver()
        subject.attach(monitor)
        
        # When test fails:
        subject.notify(TestEvent(
            event_type=TestEventType.TEST_FAILED,
            data={'test_id': 'test_api', 'error': 'AttributeError: .connection'}
        ))
        # → Monitor detects DI violation and logs warning
    """
    
    # DI violation patterns
    DI_VIOLATIONS = [
        r'\.connection\b',      # Direct .connection access
        r'\.service\b',         # Direct .service access
        r'\.db_path\b',         # Direct .db_path access
        r'\.session\b',         # Direct .session access (should use DI)
    ]
    
    # Module coupling patterns
    COUPLING_VIOLATIONS = [
        r'from modules\.\w+\.backend import',  # Direct module import
        r'import modules\.\w+\.backend',       # Direct module import
    ]
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize architecture monitor
        
        Args:
            strict_mode: If True, raises exception on violation (for CI/CD)
        """
        super().__init__("ArchitectureMonitor")
        self.strict_mode = strict_mode
        self._violations: List[Dict] = []
        self._violation_counts: Dict[str, int] = {}
        
        logger.info(
            f"[Architecture Monitor] Initialized (strict_mode={strict_mode})"
        )
    
    def update(self, event: TestEvent):
        """
        React to test event
        
        Args:
            event: TestEvent to process
        """
        # Only monitor test failures and architecture events
        if event.event_type not in [
            TestEventType.TEST_FAILED,
            TestEventType.DI_VIOLATION_DETECTED,
            TestEventType.ARCHITECTURE_DRIFT_DETECTED
        ]:
            return
        
        # Check for violations
        violations = self._detect_violations(event)
        
        if violations:
            self._handle_violations(event, violations)
    
    def _detect_violations(self, event: TestEvent) -> List[Dict]:
        """
        Detect architecture violations in event data
        
        Returns:
            List of violation dicts with type and details
        """
        violations = []
        
        # Get error message/traceback if available
        error_text = str(event.data.get('error', ''))
        traceback = event.data.get('traceback', '')
        test_source = event.data.get('test_source', '')
        
        full_text = f"{error_text}\n{traceback}\n{test_source}"
        
        # Check for DI violations
        for pattern in self.DI_VIOLATIONS:
            matches = re.findall(pattern, full_text)
            if matches:
                violations.append({
                    'type': 'di_violation',
                    'pattern': pattern,
                    'matches': matches,
                    'severity': 'high'
                })
        
        # Check for coupling violations
        for pattern in self.COUPLING_VIOLATIONS:
            matches = re.findall(pattern, full_text)
            if matches:
                violations.append({
                    'type': 'coupling_violation',
                    'pattern': pattern,
                    'matches': matches,
                    'severity': 'medium'
                })
        
        return violations
    
    def _handle_violations(self, event: TestEvent, violations: List[Dict]):
        """Handle detected violations"""
        test_id = event.data.get('test_id', 'unknown')
        
        for violation in violations:
            # Store violation
            violation_record = {
                'test_id': test_id,
                'timestamp': event.timestamp,
                'type': violation['type'],
                'pattern': violation['pattern'],
                'severity': violation['severity']
            }
            self._violations.append(violation_record)
            
            # Update counts
            vtype = violation['type']
            self._violation_counts[vtype] = self._violation_counts.get(vtype, 0) + 1
            
            # Log warning
            logger.warning(
                f"[Architecture Monitor] {violation['type'].upper()} in {test_id}: "
                f"Pattern '{violation['pattern']}' matched"
            )
            
            # Strict mode: raise exception
            if self.strict_mode:
                raise ArchitectureViolationError(
                    f"Architecture violation in {test_id}: {violation['type']}"
                )
    
    def get_violations(self, limit: int = 50) -> List[Dict]:
        """
        Get recent violations
        
        Args:
            limit: Maximum violations to return
        
        Returns:
            List of violation records (most recent last)
        """
        return self._violations[-limit:]
    
    def get_violation_summary(self) -> Dict:
        """
        Get summary of violations by type
        
        Returns:
            Dict with violation counts and top offenders
        """
        # Count violations per test
        test_violations = {}
        for v in self._violations:
            test_id = v['test_id']
            test_violations[test_id] = test_violations.get(test_id, 0) + 1
        
        # Top offenders (tests with most violations)
        top_offenders = sorted(
            test_violations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'total_violations': len(self._violations),
            'by_type': self._violation_counts.copy(),
            'top_offenders': [
                {'test_id': test_id, 'count': count}
                for test_id, count in top_offenders
            ]
        }
    
    def clear_violations(self):
        """Clear violation history (e.g., after fixes applied)"""
        self._violations = []
        self._violation_counts = {}
        logger.info("[Architecture Monitor] Violations cleared")


class ArchitectureViolationError(Exception):
    """Raised when architecture violation detected in strict mode"""
    pass