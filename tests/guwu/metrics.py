"""
Gu Wu Metrics Collector - Self-Learning Component

Collects and analyzes test execution metrics to enable autonomous optimization.
Similar to how Feng Shui analyzes code patterns, Gu Wu analyzes test patterns.
"""

import sqlite3
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class TestMetric:
    """Single test execution metric"""
    test_id: str           # Unique test identifier (nodeid)
    test_name: str         # Human-readable test name
    module: str            # Module being tested
    layer: str             # unit/integration/e2e
    duration: float        # Execution time (seconds)
    outcome: str           # passed/failed/skipped/error
    timestamp: str         # ISO format timestamp
    markers: str           # Comma-separated markers
    coverage_delta: float  # Change in coverage (if available)
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return asdict(self)


class MetricsCollector:
    """
    Collects test execution metrics for Gu Wu self-optimization.
    
    Features:
        - Tracks every test execution (timing, outcome, coverage)
        - Identifies patterns (flaky tests, slow tests, coverage trends)
        - Persists historical data for learning
        - Enables autonomous optimization decisions
    """
    
    def __init__(self, db_path: str = "tests/guwu/metrics.db"):
        """Initialize metrics collector with SQLite backend"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # In-memory cache for current session
        self.session_metrics: List[TestMetric] = []
        self.session_start = time.time()
    
    def _init_database(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test execution history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id TEXT NOT NULL,
                test_name TEXT NOT NULL,
                module TEXT NOT NULL,
                layer TEXT NOT NULL,
                duration REAL NOT NULL,
                outcome TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                markers TEXT,
                coverage_delta REAL,
                error_message TEXT,
                session_id TEXT
            )
        ''')
        
        # Test statistics (aggregated)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_statistics (
                test_id TEXT PRIMARY KEY,
                test_name TEXT NOT NULL,
                total_runs INTEGER DEFAULT 0,
                total_passes INTEGER DEFAULT 0,
                total_failures INTEGER DEFAULT 0,
                total_errors INTEGER DEFAULT 0,
                avg_duration REAL,
                min_duration REAL,
                max_duration REAL,
                flaky_score REAL DEFAULT 0.0,
                last_failure TEXT,
                last_run TEXT
            )
        ''')
        
        # Session summary
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_sessions (
                session_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                total_tests INTEGER,
                passed INTEGER,
                failed INTEGER,
                errors INTEGER,
                skipped INTEGER,
                duration REAL,
                coverage REAL,
                pyramid_score REAL
            )
        ''')
        
        # Gu Wu insights (autonomous learning)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guwu_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_type TEXT NOT NULL,
                test_id TEXT,
                description TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                confidence REAL NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_test_id ON test_executions(test_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON test_executions(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_outcome ON test_executions(outcome)')
        
        conn.commit()
        conn.close()
    
    def record_test(self, metric: TestMetric):
        """Record a single test execution"""
        self.session_metrics.append(metric)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert execution record
        cursor.execute('''
            INSERT INTO test_executions 
            (test_id, test_name, module, layer, duration, outcome, timestamp, 
             markers, coverage_delta, error_message, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metric.test_id, metric.test_name, metric.module, metric.layer,
            metric.duration, metric.outcome, metric.timestamp, metric.markers,
            metric.coverage_delta, metric.error_message, self.get_session_id()
        ))
        
        # Update statistics
        self._update_statistics(cursor, metric)
        
        conn.commit()
        conn.close()
    
    def _update_statistics(self, cursor, metric: TestMetric):
        """Update aggregated test statistics"""
        # Get current stats
        cursor.execute('''
            SELECT total_runs, total_passes, total_failures, total_errors,
                   avg_duration, min_duration, max_duration, flaky_score
            FROM test_statistics
            WHERE test_id = ?
        ''', (metric.test_id,))
        
        row = cursor.fetchone()
        
        if row:
            # Update existing stats
            total_runs, passes, failures, errors, avg_dur, min_dur, max_dur, flaky = row
            
            total_runs += 1
            if metric.outcome == 'passed':
                passes += 1
            elif metric.outcome == 'failed':
                failures += 1
            elif metric.outcome == 'error':
                errors += 1
            
            # Update duration stats
            avg_dur = ((avg_dur * (total_runs - 1)) + metric.duration) / total_runs
            min_dur = min(min_dur, metric.duration)
            max_dur = max(max_dur, metric.duration)
            
            # Calculate flaky score (higher = more flaky)
            # Flaky = alternating pass/fail pattern
            recent_outcomes = self._get_recent_outcomes(cursor, metric.test_id, limit=10)
            flaky = self._calculate_flaky_score(recent_outcomes)
            
            cursor.execute('''
                UPDATE test_statistics
                SET total_runs = ?, total_passes = ?, total_failures = ?, total_errors = ?,
                    avg_duration = ?, min_duration = ?, max_duration = ?, flaky_score = ?,
                    last_failure = ?, last_run = ?
                WHERE test_id = ?
            ''', (
                total_runs, passes, failures, errors, avg_dur, min_dur, max_dur, flaky,
                metric.timestamp if metric.outcome in ['failed', 'error'] else None,
                metric.timestamp, metric.test_id
            ))
        else:
            # Create new stats entry
            cursor.execute('''
                INSERT INTO test_statistics
                (test_id, test_name, total_runs, total_passes, total_failures, total_errors,
                 avg_duration, min_duration, max_duration, flaky_score, last_run)
                VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?, 0.0, ?)
            ''', (
                metric.test_id, metric.test_name,
                1 if metric.outcome == 'passed' else 0,
                1 if metric.outcome == 'failed' else 0,
                1 if metric.outcome == 'error' else 0,
                metric.duration, metric.duration, metric.duration,
                metric.timestamp
            ))
    
    def _get_recent_outcomes(self, cursor, test_id: str, limit: int = 10) -> List[str]:
        """Get recent test outcomes for flaky detection"""
        cursor.execute('''
            SELECT outcome FROM test_executions
            WHERE test_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (test_id, limit))
        
        return [row[0] for row in cursor.fetchall()]
    
    def _calculate_flaky_score(self, outcomes: List[str]) -> float:
        """
        Calculate flaky score (0.0 = stable, 1.0 = very flaky)
        
        Flaky pattern: pass → fail → pass → fail (alternating)
        Stable pattern: pass → pass → pass OR fail → fail → fail
        """
        if len(outcomes) < 2:
            return 0.0
        
        # Count transitions (pass→fail or fail→pass)
        transitions = 0
        for i in range(len(outcomes) - 1):
            if outcomes[i] != outcomes[i + 1]:
                transitions += 1
        
        # Flaky score = transitions / possible_transitions
        # Example: [pass, fail, pass, fail] = 3 transitions / 3 possible = 1.0 (very flaky)
        # Example: [pass, pass, pass, pass] = 0 transitions / 3 possible = 0.0 (stable)
        flaky_score = transitions / (len(outcomes) - 1)
        
        return round(flaky_score, 2)
    
    def get_session_id(self) -> str:
        """Generate session ID (timestamp-based)"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def get_flaky_tests(self, threshold: float = 0.5) -> List[Dict]:
        """
        Get tests identified as flaky by Gu Wu.
        
        Args:
            threshold: Flaky score threshold (default 0.5)
        
        Returns:
            List of flaky tests with details
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT test_id, test_name, total_runs, total_passes, total_failures,
                   flaky_score, last_failure
            FROM test_statistics
            WHERE flaky_score >= ? AND total_runs >= 3
            ORDER BY flaky_score DESC
        ''', (threshold,))
        
        flaky_tests = []
        for row in cursor.fetchall():
            flaky_tests.append({
                'test_id': row[0],
                'test_name': row[1],
                'total_runs': row[2],
                'total_passes': row[3],
                'total_failures': row[4],
                'flaky_score': row[5],
                'last_failure': row[6]
            })
        
        conn.close()
        return flaky_tests
    
    def get_slow_tests(self, threshold: float = 5.0) -> List[Dict]:
        """
        Get tests identified as slow by Gu Wu.
        
        Args:
            threshold: Duration threshold in seconds (default 5.0)
        
        Returns:
            List of slow tests with average duration
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT test_id, test_name, avg_duration, max_duration, total_runs
            FROM test_statistics
            WHERE avg_duration >= ?
            ORDER BY avg_duration DESC
        ''', (threshold,))
        
        slow_tests = []
        for row in cursor.fetchall():
            slow_tests.append({
                'test_id': row[0],
                'test_name': row[1],
                'avg_duration': round(row[2], 2),
                'max_duration': round(row[3], 2),
                'total_runs': row[4]
            })
        
        conn.close()
        return slow_tests
    
    def get_test_priorities(self) -> List[Tuple[str, float]]:
        """
        Calculate test priorities for auto-reordering.
        
        Priority = failure_rate * recency_weight * criticality
        
        Returns:
            List of (test_id, priority_score) sorted by priority (highest first)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                test_id,
                test_name,
                total_runs,
                total_failures,
                total_errors,
                last_failure
            FROM test_statistics
            WHERE total_runs > 0
        ''')
        
        priorities = []
        now = datetime.now()
        
        for row in cursor.fetchall():
            test_id, test_name, runs, failures, errors, last_failure = row
            
            # Failure rate (0.0 - 1.0)
            failure_rate = (failures + errors) / runs if runs > 0 else 0.0
            
            # Recency weight (tests that failed recently = higher priority)
            recency = 1.0
            if last_failure:
                last_fail_dt = datetime.fromisoformat(last_failure)
                days_since = (now - last_fail_dt).days
                recency = 1.0 / (1 + days_since) if days_since >= 0 else 1.0
            
            # Criticality (marked as critical = always high priority)
            criticality = 2.0 if 'critical' in test_name.lower() else 1.0
            
            # Calculate priority
            priority = failure_rate * recency * criticality
            
            priorities.append((test_id, priority))
        
        conn.close()
        
        # Sort by priority (highest first)
        priorities.sort(key=lambda x: x[1], reverse=True)
        
        return priorities
    
    def get_pyramid_compliance(self) -> Dict[str, float]:
        """
        Calculate Test Pyramid compliance.
        
        Target: 70% unit, 20% integration, 10% e2e
        
        Returns:
            Dict with actual percentages and compliance score
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get test counts by layer (from most recent session)
        cursor.execute('''
            SELECT layer, COUNT(*) as count
            FROM test_executions
            WHERE session_id = (
                SELECT session_id FROM test_executions
                ORDER BY timestamp DESC LIMIT 1
            )
            GROUP BY layer
        ''')
        
        layer_counts = {row[0]: row[1] for row in cursor.fetchall()}
        total = sum(layer_counts.values())
        
        if total == 0:
            conn.close()
            return {
                'unit_pct': 0,
                'integration_pct': 0,
                'e2e_pct': 0,
                'compliance_score': 0.0
            }
        
        # Calculate percentages
        unit_pct = (layer_counts.get('unit', 0) / total) * 100
        integration_pct = (layer_counts.get('integration', 0) / total) * 100
        e2e_pct = (layer_counts.get('e2e', 0) / total) * 100
        
        # Compliance score (0.0 - 1.0, higher = better)
        # Perfect: 70/20/10, Score = 1.0
        # Actual deviation from ideal
        unit_diff = abs(unit_pct - 70)
        int_diff = abs(integration_pct - 20)
        e2e_diff = abs(e2e_pct - 10)
        
        avg_deviation = (unit_diff + int_diff + e2e_diff) / 3
        compliance_score = max(0.0, 1.0 - (avg_deviation / 100))
        
        conn.close()
        
        return {
            'unit_pct': round(unit_pct, 1),
            'integration_pct': round(integration_pct, 1),
            'e2e_pct': round(e2e_pct, 1),
            'compliance_score': round(compliance_score, 2),
            'target': '70/20/10',
            'status': 'compliant' if compliance_score >= 0.8 else 'needs_improvement'
        }
    
    def generate_insights(self) -> List[Dict]:
        """
        Generate autonomous insights based on collected metrics.
        
        This is where Gu Wu "learns" and suggests improvements.
        
        Returns:
            List of insights with recommendations
        """
        insights = []
        
        # 1. Flaky Test Insights
        flaky_tests = self.get_flaky_tests(threshold=0.5)
        if flaky_tests:
            for test in flaky_tests[:5]:  # Top 5
                insights.append({
                    'type': 'flaky_test',
                    'severity': 'high',
                    'test_id': test['test_id'],
                    'description': f"Test '{test['test_name']}' is flaky (score: {test['flaky_score']})",
                    'recommendation': "Review test for race conditions, timing issues, or external dependencies. Consider adding retries or improving isolation.",
                    'confidence': test['flaky_score']
                })
        
        # 2. Slow Test Insights
        slow_tests = self.get_slow_tests(threshold=5.0)
        if slow_tests:
            for test in slow_tests[:5]:  # Top 5
                insights.append({
                    'type': 'slow_test',
                    'severity': 'medium',
                    'test_id': test['test_id'],
                    'description': f"Test '{test['test_name']}' is slow (avg: {test['avg_duration']}s)",
                    'recommendation': "Consider mocking external dependencies, reducing test data size, or moving to integration layer if appropriate.",
                    'confidence': min(1.0, test['avg_duration'] / 10)
                })
        
        # 3. Pyramid Compliance Insights
        pyramid = self.get_pyramid_compliance()
        if pyramid['compliance_score'] < 0.8:
            insights.append({
                'type': 'pyramid_imbalance',
                'severity': 'high',
                'test_id': None,
                'description': f"Test pyramid imbalanced: {pyramid['unit_pct']}% unit, {pyramid['integration_pct']}% integration, {pyramid['e2e_pct']}% e2e (target: 70/20/10)",
                'recommendation': self._get_pyramid_recommendation(pyramid),
                'confidence': 1.0 - pyramid['compliance_score']
            })
        
        # 4. Coverage Trend Insights
        coverage_trend = self._analyze_coverage_trend()
        if coverage_trend['dropping']:
            insights.append({
                'type': 'coverage_drop',
                'severity': 'high',
                'test_id': None,
                'description': f"Code coverage dropped {coverage_trend['drop_pct']}% in last 5 sessions",
                'recommendation': "Add unit tests for recently added code. Focus on modules with < 70% coverage.",
                'confidence': abs(coverage_trend['drop_pct']) / 10
            })
        
        # Store insights in database for tracking
        self._store_insights(insights)
        
        return insights
    
    def _get_pyramid_recommendation(self, pyramid: Dict) -> str:
        """Generate specific recommendation for pyramid imbalance"""
        unit_pct = pyramid['unit_pct']
        int_pct = pyramid['integration_pct']
        e2e_pct = pyramid['e2e_pct']
        
        if unit_pct < 60:
            return f"Add more unit tests (currently {unit_pct}%, target 70%). Focus on testing individual functions/methods in isolation."
        elif int_pct < 15:
            return f"Add integration tests (currently {int_pct}%, target 20%). Test module interactions and API contracts."
        elif e2e_pct > 15:
            return f"Reduce E2E tests (currently {e2e_pct}%, target 10%). Move some E2E tests to integration or unit layer."
        else:
            return "Rebalance test distribution towards 70/20/10 target."
    
    def _analyze_coverage_trend(self) -> Dict:
        """Analyze coverage trend over recent sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get last 5 sessions with coverage data
        cursor.execute('''
            SELECT coverage FROM test_sessions
            WHERE coverage IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 5
        ''')
        
        coverages = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if len(coverages) < 2:
            return {'dropping': False, 'drop_pct': 0}
        
        # Check if coverage is dropping
        recent_avg = sum(coverages[:2]) / 2
        older_avg = sum(coverages[2:]) / len(coverages[2:]) if len(coverages) > 2 else recent_avg
        
        drop_pct = older_avg - recent_avg
        
        return {
            'dropping': drop_pct > 5,  # > 5% drop
            'drop_pct': round(drop_pct, 1),
            'recent_avg': round(recent_avg, 1),
            'older_avg': round(older_avg, 1)
        }
    
    def _store_insights(self, insights: List[Dict]):
        """Store insights in database for tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        for insight in insights:
            cursor.execute('''
                INSERT INTO guwu_insights
                (insight_type, test_id, description, recommendation, confidence, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                insight['type'],
                insight.get('test_id'),
                insight['description'],
                insight['recommendation'],
                insight['confidence'],
                timestamp
            ))
        
        conn.commit()
        conn.close()
    
    def finalize_session(self, session_summary: Dict):
        """Record session summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO test_sessions
            (session_id, timestamp, total_tests, passed, failed, errors, skipped,
             duration, coverage, pyramid_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.get_session_id(),
            datetime.now().isoformat(),
            session_summary.get('total', 0),
            session_summary.get('passed', 0),
            session_summary.get('failed', 0),
            session_summary.get('errors', 0),
            session_summary.get('skipped', 0),
            session_summary.get('duration', 0),
            session_summary.get('coverage'),
            session_summary.get('pyramid_score')
        ))
        
        conn.commit()
        conn.close()


# Singleton instance
_collector = None


def get_collector(db_path: str = "tests/guwu/metrics.db") -> MetricsCollector:
    """Get or create metrics collector singleton"""
    global _collector
    if _collector is None:
        _collector = MetricsCollector(db_path)
    return _collector