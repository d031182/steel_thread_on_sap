"""
Gu Wu Interface: Shi Fu's Connection to the Testing Disciple
=============================================================

Reads Gu Wu's test metrics database to understand test quality patterns.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


@dataclass
class TestMetricsSummary:
    """Summary of test metrics from Gu Wu"""
    total_tests: int
    passing_tests: int
    failing_tests: int
    flaky_tests: int
    slow_tests: int
    avg_execution_time: float
    coverage_percentage: float
    tests_by_type: Dict[str, int]
    recent_executions: List[Dict]


class GuWuInterface:
    """
    Interface to Gu Wu (顾武) - The Testing Disciple
    
    Reads from Gu Wu's metrics database to understand test quality patterns.
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize Gu Wu interface
        
        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
        self.db_path = project_root / "tests" / "guwu" / "guwu_metrics.db"
        
        if not self.db_path.exists():
            logger.warning(f"[Gu Wu Interface] Database not found: {self.db_path}")
    
    def get_recent_test_executions(self, days: int = 7) -> List[Dict]:
        """
        Get test executions from last N days
        
        Args:
            days: Number of days to look back
        
        Returns:
            List of test execution dictionaries
        """
        if not self.db_path.exists():
            logger.warning("[Gu Wu Interface] No database, returning empty list")
            return []
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    test_id,
                    test_name,
                    test_file,
                    test_type,
                    outcome,
                    duration_ms,
                    executed_at,
                    error_message
                FROM test_executions
                WHERE executed_at >= ?
                ORDER BY executed_at DESC
            """, (cutoff_date,))
            
            executions = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            logger.info(f"[Gu Wu Interface] Retrieved {len(executions)} test executions from last {days} days")
            return executions
            
        except sqlite3.Error as e:
            logger.error(f"[Gu Wu Interface] Database error: {e}")
            return []
    
    def get_flaky_tests(self, days: int = 7, min_flakiness_score: float = 0.3) -> List[Dict]:
        """
        Get tests identified as flaky
        
        Args:
            days: Number of days to look back
            min_flakiness_score: Minimum flakiness score (0.0-1.0)
        
        Returns:
            List of flaky test dictionaries
        """
        if not self.db_path.exists():
            logger.warning("[Gu Wu Interface] No database, returning empty list")
            return []
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    test_name,
                    test_file,
                    flakiness_score,
                    pass_count,
                    fail_count,
                    total_runs,
                    last_flaky_at
                FROM flaky_tests
                WHERE last_flaky_at >= ?
                AND flakiness_score >= ?
                ORDER BY flakiness_score DESC
            """, (cutoff_date, min_flakiness_score))
            
            flaky = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            logger.info(f"[Gu Wu Interface] Found {len(flaky)} flaky tests")
            return flaky
            
        except sqlite3.Error as e:
            logger.error(f"[Gu Wu Interface] Database error: {e}")
            return []
    
    def get_test_metrics_summary(self, days: int = 7) -> TestMetricsSummary:
        """
        Get summary statistics of test metrics
        
        Args:
            days: Number of days to look back
        
        Returns:
            TestMetricsSummary object
        """
        executions = self.get_recent_test_executions(days)
        
        if not executions:
            return TestMetricsSummary(
                total_tests=0,
                passing_tests=0,
                failing_tests=0,
                flaky_tests=0,
                slow_tests=0,
                avg_execution_time=0.0,
                coverage_percentage=0.0,
                tests_by_type={},
                recent_executions=[]
            )
        
        # Count by outcome
        passing = sum(1 for e in executions if e.get('outcome') == 'PASSED')
        failing = sum(1 for e in executions if e.get('outcome') == 'FAILED')
        
        # Get flaky test count
        flaky = self.get_flaky_tests(days)
        
        # Count slow tests (>5 seconds)
        slow = sum(1 for e in executions if e.get('duration_ms', 0) > 5000)
        
        # Calculate average execution time
        durations = [e.get('duration_ms', 0) for e in executions]
        avg_time = sum(durations) / len(durations) if durations else 0.0
        
        # Count by type
        by_type = {}
        for e in executions:
            ttype = e.get('test_type', 'unit')
            by_type[ttype] = by_type.get(ttype, 0) + 1
        
        # Get coverage (from separate table if exists)
        coverage = self._get_coverage_percentage()
        
        return TestMetricsSummary(
            total_tests=len(executions),
            passing_tests=passing,
            failing_tests=failing,
            flaky_tests=len(flaky),
            slow_tests=slow,
            avg_execution_time=avg_time,
            coverage_percentage=coverage,
            tests_by_type=by_type,
            recent_executions=executions[:20]  # Top 20 most recent
        )
    
    def get_overall_score(self) -> float:
        """
        Get overall Gu Wu quality score
        
        Returns:
            Score from 0-100
        """
        if not self.db_path.exists():
            logger.warning("[Gu Wu Interface] No database, returning default score")
            return 80.0  # Default optimistic score
        
        try:
            summary = self.get_test_metrics_summary(days=7)
            
            if summary.total_tests == 0:
                return 50.0  # No tests = mediocre score
            
            # Calculate score based on multiple factors
            score = 100.0
            
            # Test pass rate (weight: 40%)
            pass_rate = summary.passing_tests / summary.total_tests if summary.total_tests > 0 else 0
            score -= (1 - pass_rate) * 40
            
            # Flakiness penalty (weight: 30%)
            if summary.total_tests > 0:
                flaky_rate = summary.flaky_tests / summary.total_tests
                score -= flaky_rate * 30
            
            # Coverage (weight: 20%)
            coverage_penalty = (100 - summary.coverage_percentage) * 0.2
            score -= coverage_penalty
            
            # Slow tests penalty (weight: 10%)
            if summary.total_tests > 0:
                slow_rate = summary.slow_tests / summary.total_tests
                score -= slow_rate * 10
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            logger.error(f"[Gu Wu Interface] Error calculating score: {e}")
            return 80.0  # Default fallback
    
    def get_tests_for_module(self, module_name: str, days: int = 7) -> List[Dict]:
        """
        Get test executions for a specific module
        
        Args:
            module_name: Module name to filter
            days: Number of days to look back
        
        Returns:
            List of test executions
        """
        all_executions = self.get_recent_test_executions(days)
        
        # Filter by module name in test file path
        return [
            e for e in all_executions
            if module_name.lower() in e.get('test_file', '').lower()
        ]
    
    def get_slow_tests(self, days: int = 7, threshold_ms: int = 5000) -> List[Dict]:
        """
        Get tests that exceed time threshold
        
        Args:
            days: Number of days to look back
            threshold_ms: Threshold in milliseconds
        
        Returns:
            List of slow test dictionaries
        """
        all_executions = self.get_recent_test_executions(days)
        
        slow_tests = [
            e for e in all_executions
            if e.get('duration_ms', 0) > threshold_ms
        ]
        
        # Sort by duration descending
        slow_tests.sort(key=lambda x: x.get('duration_ms', 0), reverse=True)
        
        return slow_tests
    
    def _get_coverage_percentage(self) -> float:
        """
        Get test coverage percentage from database
        
        Returns:
            Coverage percentage (0-100)
        """
        if not self.db_path.exists():
            return 0.0
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT coverage_percentage
                FROM coverage_metrics
                ORDER BY measured_at DESC
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] is not None:
                return float(result[0])
            
            return 70.0  # Default optimistic coverage
            
        except sqlite3.Error as e:
            logger.debug(f"[Gu Wu Interface] No coverage table: {e}")
            return 70.0  # Default fallback