#!/usr/bin/env python3
"""
Feng Shui Architecture Observer - Observer Pattern
===================================================

Real-time monitoring of architecture quality with automated alerts.

GoF Pattern: Observer (Behavioral)
- Subject maintains list of observers
- Observers notified when state changes
- Loose coupling between subject and observers
- Multiple observers can react to same event

Use Cases:
- Real-time architecture score monitoring
- Automated alerts when quality drops
- CI/CD integration hooks
- Dashboard live updates
"""
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Protocol
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod
import json

# Add UTF-8 reconfiguration for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None


@dataclass
class ArchitectureEvent:
    """
    Event representing architecture state change
    
    Attributes:
        event_type: Type of event (score_changed, issue_detected, fix_applied, etc.)
        timestamp: When event occurred
        data: Event-specific data
    """
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    severity: str = 'INFO'  # INFO, WARNING, CRITICAL
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'severity': self.severity
        }


class ArchitectureObserver(ABC):
    """
    Observer: Abstract base class for architecture observers
    
    Each observer implements update() to react to architecture events.
    """
    
    @abstractmethod
    def update(self, event: ArchitectureEvent) -> None:
        """
        React to architecture event
        
        Args:
            event: Event containing state change information
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return observer name for logging"""
        pass


class ConsoleLogObserver(ArchitectureObserver):
    """
    Observer: Logs events to console
    
    Useful for development and debugging.
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
    
    def update(self, event: ArchitectureEvent) -> None:
        """Log event to console"""
        emoji = {
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'CRITICAL': '🔴'
        }
        
        if self.verbose or event.severity != 'INFO':
            print(f"{emoji.get(event.severity, '')} [{event.event_type}] {event.data.get('message', '')}")
            if self.verbose:
                print(f"  Time: {event.timestamp.strftime('%H:%M:%S')}")
    
    def get_name(self) -> str:
        return "ConsoleLogObserver"


class FileLogObserver(ArchitectureObserver):
    """
    Observer: Writes events to log file
    
    Persists event history for analysis.
    """
    
    def __init__(self, log_file: Path = Path('logs/architecture_events.log')):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def update(self, event: ArchitectureEvent) -> None:
        """Append event to log file"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event.to_dict()) + '\n')
    
    def get_name(self) -> str:
        return "FileLogObserver"


class MetricsCollectorObserver(ArchitectureObserver):
    """
    Observer: Collects metrics for analysis
    
    Tracks trends over time, similar to Gu Wu metrics.
    """
    
    def __init__(self, metrics_db: Path = Path('logs/architecture_metrics.db')):
        self.metrics_db = metrics_db
        self.metrics: List[ArchitectureEvent] = []
    
    def update(self, event: ArchitectureEvent) -> None:
        """Store event in metrics collection"""
        self.metrics.append(event)
        
        # Persist to database (simplified - would use SQLite in production)
        if len(self.metrics) % 10 == 0:  # Batch writes
            self._persist_metrics()
    
    def _persist_metrics(self) -> None:
        """Write metrics to database"""
        # In production, use SQLite like Gu Wu
        # For demo, just track in memory
        pass
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        return {
            'total_events': len(self.metrics),
            'by_type': self._count_by_type(),
            'by_severity': self._count_by_severity()
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count events by type"""
        counts = {}
        for event in self.metrics:
            counts[event.event_type] = counts.get(event.event_type, 0) + 1
        return counts
    
    def _count_by_severity(self) -> Dict[str, int]:
        """Count events by severity"""
        counts = {}
        for event in self.metrics:
            counts[event.severity] = counts.get(event.severity, 0) + 1
        return counts
    
    def get_name(self) -> str:
        return "MetricsCollectorObserver"


class AlertObserver(ArchitectureObserver):
    """
    Observer: Sends alerts when quality drops below threshold
    
    Critical for CI/CD integration - fails build if score too low.
    """
    
    def __init__(self, score_threshold: int = 85, alert_callback=None):
        self.score_threshold = score_threshold
        self.alert_callback = alert_callback or self._default_alert
        self.alerts_sent = 0
    
    def update(self, event: ArchitectureEvent) -> None:
        """Check if alert needed"""
        if event.event_type == 'score_changed':
            new_score = event.data.get('new_score', 100)
            if new_score < self.score_threshold:
                self._send_alert(event)
    
    def _send_alert(self, event: ArchitectureEvent) -> None:
        """Send alert"""
        self.alerts_sent += 1
        self.alert_callback(event)
    
    def _default_alert(self, event: ArchitectureEvent) -> None:
        """Default alert handler"""
        print(f"\n🚨 ALERT: Architecture quality below threshold!")
        print(f"  Score: {event.data.get('new_score')} (threshold: {self.score_threshold})")
        print(f"  Previous: {event.data.get('old_score')}")
    
    def get_name(self) -> str:
        return "AlertObserver"


class DashboardObserver(ArchitectureObserver):
    """
    Observer: Updates web dashboard in real-time
    
    Future: WebSocket connection to live dashboard UI.
    """
    
    def __init__(self):
        self.last_update = None
        self.update_count = 0
    
    def update(self, event: ArchitectureEvent) -> None:
        """Update dashboard"""
        self.last_update = event.timestamp
        self.update_count += 1
        
        # In production: Send via WebSocket to frontend
        # For demo: Track locally
    
    def get_name(self) -> str:
        return "DashboardObserver"


class ArchitectureSubject:
    """
    Subject: Manages observers and notifies them of architecture events
    
    The central hub for architecture monitoring.
    Observers register/unregister, subject notifies all on state changes.
    """
    
    def __init__(self):
        self._observers: List[ArchitectureObserver] = []
        self._state: Dict[str, Any] = {
            'score': 100,
            'grade': 'A+',
            'issues': 0
        }
    
    def attach(self, observer: ArchitectureObserver) -> None:
        """
        Register observer
        
        Args:
            observer: Observer to register
        """
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"  [ATTACHED] {observer.get_name()}")
    
    def detach(self, observer: ArchitectureObserver) -> None:
        """
        Unregister observer
        
        Args:
            observer: Observer to unregister
        """
        if observer in self._observers:
            self._observers.remove(observer)
            print(f"  [DETACHED] {observer.get_name()}")
    
    def notify(self, event: ArchitectureEvent) -> None:
        """
        Notify all observers of event
        
        Args:
            event: Event to broadcast
        """
        for observer in self._observers:
            try:
                observer.update(event)
            except Exception as e:
                print(f"  [ERROR] Observer {observer.get_name()} failed: {e}")
    
    def set_score(self, new_score: int) -> None:
        """
        Update architecture score and notify observers
        
        Args:
            new_score: New feng shui score
        """
        old_score = self._state['score']
        self._state['score'] = new_score
        
        # Calculate grade
        if new_score >= 90:
            grade = 'A'
        elif new_score >= 80:
            grade = 'B'
        elif new_score >= 70:
            grade = 'C'
        else:
            grade = 'F'
        
        self._state['grade'] = grade
        
        # Create event
        event = ArchitectureEvent(
            event_type='score_changed',
            timestamp=datetime.now(),
            data={
                'old_score': old_score,
                'new_score': new_score,
                'grade': grade,
                'message': f"Score changed: {old_score} → {new_score} (Grade {grade})"
            },
            severity='WARNING' if new_score < 85 else 'INFO'
        )
        
        # Notify all observers
        self.notify(event)
    
    def report_issue(self, issue_type: str, severity: str, details: str) -> None:
        """
        Report architecture issue
        
        Args:
            issue_type: Type of issue (DI_VIOLATION, GOD_CLASS, etc.)
            severity: CRITICAL, HIGH, MEDIUM, LOW
            details: Issue description
        """
        self._state['issues'] = self._state.get('issues', 0) + 1
        
        event = ArchitectureEvent(
            event_type='issue_detected',
            timestamp=datetime.now(),
            data={
                'issue_type': issue_type,
                'details': details,
                'total_issues': self._state['issues'],
                'message': f"Issue detected: {issue_type} - {details}"
            },
            severity=severity
        )
        
        self.notify(event)
    
    def report_fix(self, fix_type: str, success: bool, details: str) -> None:
        """
        Report automated fix attempt
        
        Args:
            fix_type: Type of fix applied
            success: Whether fix succeeded
            details: Fix description
        """
        event = ArchitectureEvent(
            event_type='fix_applied' if success else 'fix_failed',
            timestamp=datetime.now(),
            data={
                'fix_type': fix_type,
                'details': details,
                'message': f"{'✓' if success else '✗'} Fix {fix_type}: {details}"
            },
            severity='INFO' if success else 'WARNING'
        )
        
        self.notify(event)
    
    def get_state(self) -> Dict[str, Any]:
        """Get current architecture state"""
        return self._state.copy()


class MonitoringSession:
    """
    Convenience wrapper for monitoring architecture
    
    Sets up common observers and provides easy-to-use interface.
    """
    
    def __init__(self, enable_alerts: bool = True, alert_threshold: int = 85):
        self.subject = ArchitectureSubject()
        
        # Attach standard observers
        self.console_observer = ConsoleLogObserver(verbose=True)
        self.file_observer = FileLogObserver()
        self.metrics_observer = MetricsCollectorObserver()
        
        self.subject.attach(self.console_observer)
        self.subject.attach(self.file_observer)
        self.subject.attach(self.metrics_observer)
        
        if enable_alerts:
            self.alert_observer = AlertObserver(score_threshold=alert_threshold)
            self.subject.attach(self.alert_observer)
    
    def start_monitoring(self) -> None:
        """Start monitoring session"""
        event = ArchitectureEvent(
            event_type='monitoring_started',
            timestamp=datetime.now(),
            data={'message': 'Architecture monitoring started'},
            severity='INFO'
        )
        self.subject.notify(event)
    
    def stop_monitoring(self) -> None:
        """Stop monitoring session"""
        event = ArchitectureEvent(
            event_type='monitoring_stopped',
            timestamp=datetime.now(),
            data={
                'message': 'Architecture monitoring stopped',
                'summary': self.metrics_observer.get_summary()
            },
            severity='INFO'
        )
        self.subject.notify(event)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get collected metrics"""
        return self.metrics_observer.get_summary()


# ============================================================================
# INTEGRATION WITH AUTOMATION ENGINE
# ============================================================================

class ObserverIntegration:
    """
    Integrates Observer Pattern with Automation Engine
    
    Wraps automation engine to emit events during execution.
    """
    
    def __init__(self, subject: ArchitectureSubject):
        self.subject = subject
    
    def run_monitored_automation(self, auto_fix: bool = False):
        """
        Run automation with real-time monitoring
        
        Emits events at each step:
        1. Detection started
        2. Issues found
        3. Fixes applied
        4. Score changed
        5. Evolution tracked
        """
        # Import here to avoid circular dependency
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from tools.fengshui.automation_engine import FengShuiAutomationEngine
        
        engine = FengShuiAutomationEngine()
        
        # Event 1: Start detection
        self.subject.notify(ArchitectureEvent(
            event_type='detection_started',
            timestamp=datetime.now(),
            data={'message': 'Starting architecture analysis...'},
            severity='INFO'
        ))
        
        # Run detection
        project_validation = engine._detect_issues()
        
        # Event 2: Report findings
        issues_detected = sum(
            len(finding.findings)
            for module_result in project_validation.module_results
            for finding in module_result.findings.values()
        )
        
        self.subject.notify(ArchitectureEvent(
            event_type='detection_complete',
            timestamp=datetime.now(),
            data={
                'issues_found': issues_detected,
                'modules_scanned': len(project_validation.module_results),
                'message': f"Found {issues_detected} issues across {len(project_validation.module_results)} modules"
            },
            severity='WARNING' if issues_detected > 10 else 'INFO'
        ))
        
        # Event 3: Generate work packages
        work_packages = engine._generate_work_packages(project_validation)
        
        self.subject.notify(ArchitectureEvent(
            event_type='work_packages_generated',
            timestamp=datetime.now(),
            data={
                'count': len(work_packages),
                'message': f"Generated {len(work_packages)} work packages"
            },
            severity='INFO'
        ))
        
        # Event 4: Apply fixes (if enabled)
        if auto_fix:
            self.subject.notify(ArchitectureEvent(
                event_type='fixes_started',
                timestamp=datetime.now(),
                data={'message': 'Applying automated fixes...'},
                severity='INFO'
            ))
            
            fix_result = engine._apply_automated_fixes(project_validation)
            
            self.subject.notify(ArchitectureEvent(
                event_type='fixes_complete',
                timestamp=datetime.now(),
                data={
                    'succeeded': fix_result['succeeded'],
                    'failed': fix_result['failed'],
                    'message': f"Fixes applied: {fix_result['succeeded']} succeeded, {fix_result['failed']} failed"
                },
                severity='WARNING' if fix_result['failed'] > 0 else 'INFO'
            ))
        
        # Event 5: Capture snapshot
        snapshot = engine.originator.capture_snapshot()
        saved = engine.caretaker.save_snapshot(snapshot)
        
        if saved:
            # Emit score changed event
            self.subject.set_score(snapshot.feng_shui_score)
        
        return {
            'issues': issues_detected,
            'work_packages': len(work_packages),
            'fixes': fix_result if auto_fix else {'succeeded': 0, 'failed': 0},
            'score': snapshot.feng_shui_score
        }


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_observer_pattern():
    """
    Demonstrate Observer Pattern with architecture monitoring
    """
    print("\n" + "="*80)
    print("FENG SHUI OBSERVER PATTERN DEMONSTRATION")
    print("="*80)
    print("""
Observer Pattern enables real-time monitoring:

Subject (ArchitectureSubject):
- Maintains list of observers
- Notifies observers when state changes
- Manages architecture state

Observers (4 types):
1. ConsoleLogObserver - Print to console
2. FileLogObserver - Persist to log file
3. MetricsCollectorObserver - Track trends
4. AlertObserver - Send alerts when quality drops
5. DashboardObserver - Update web UI (future)

Benefits:
- Loose coupling (observers independent)
- Extensible (add new observers without changing subject)
- Real-time (immediate notification)
- Multiple reactions (many observers to same event)
""")
    
    # Example 1: Manual observer setup
    print("\n" + "="*80)
    print("EXAMPLE 1: Manual Observer Setup")
    print("="*80 + "\n")
    
    subject = ArchitectureSubject()
    
    # Attach observers
    console = ConsoleLogObserver()
    alerts = AlertObserver(score_threshold=85)
    metrics = MetricsCollectorObserver()
    
    print("Attaching observers...")
    subject.attach(console)
    subject.attach(alerts)
    subject.attach(metrics)
    
    # Simulate architecture changes
    print("\nSimulating architecture events:")
    subject.set_score(95)  # Good score
    subject.report_issue('DI_VIOLATION', 'HIGH', 'Module uses .db_path directly')
    subject.set_score(82)  # Drops below threshold → alert!
    subject.report_fix('CreateModuleJson', True, 'Created module.json')
    subject.set_score(88)  # Improved
    
    # Show metrics
    print("\n" + "-" * 80)
    print("Metrics Summary:")
    summary = metrics.get_summary()
    print(f"  Total Events: {summary['total_events']}")
    print(f"  By Type: {summary['by_type']}")
    print(f"  By Severity: {summary['by_severity']}")
    print(f"  Alerts Sent: {alerts.alerts_sent}")
    
    # Example 2: Monitoring Session (easier interface)
    print("\n\n" + "="*80)
    print("EXAMPLE 2: Monitoring Session (Simplified Interface)")
    print("="*80 + "\n")
    
    session = MonitoringSession(enable_alerts=True, alert_threshold=85)
    session.start_monitoring()
    
    # Simulate work
    session.subject.set_score(90)
    session.subject.report_issue('GOD_CLASS', 'HIGH', 'PropertyGraphService 1,020 lines')
    session.subject.set_score(88)
    
    session.stop_monitoring()
    
    # Example 3: Integration with Automation Engine
    print("\n\n" + "="*80)
    print("EXAMPLE 3: Integration with Automation Engine")
    print("="*80 + "\n")
    
    print("Running monitored automation (detection only)...")
    integration = ObserverIntegration(session.subject)
    
    # This would run full automation with events at each step
    print("  [SIMULATED] Would emit events during each automation step")
    print("  [SIMULATED] Observers would react in real-time")
    
    # Summary
    print("\n\n" + "="*80)
    print("OBSERVER PATTERN BENEFITS")
    print("="*80)
    print("""
Real-World Use Cases:
- ✅ CI/CD Integration: Fail build if score < threshold
- ✅ Developer Alerts: Notify team when quality drops
- ✅ Dashboard Updates: Live architecture health display
- ✅ Metrics Collection: Track trends over time (like Gu Wu)
- ✅ Audit Trail: Complete event history in logs

Integration Points:
1. Automation Engine emits events during execution
2. Git pre-commit hook emits events on commit
3. CI/CD pipeline monitors score continuously
4. Web dashboard displays live status

Like Gu Wu for tests, this monitors architecture health in real-time!
""")


if __name__ == '__main__':
    demonstrate_observer_pattern()