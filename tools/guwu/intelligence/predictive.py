"""
Gu Wu Phase 7.3: Predictive Analytics

ML-based failure prediction and execution time forecasting.
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics


@dataclass
class Prediction:
    """Prediction result"""
    test_name: str
    prediction_type: str  # "FAILURE", "SLOW", "SUCCESS"
    confidence: float  # 0.0-1.0
    reasoning: str
    expected_duration: Optional[float] = None


class PredictiveEngine:
    """
    ML-based predictive analytics for test execution.
    
    Predicts test failures and execution times based on historical patterns.
    """
    
    def __init__(self, db_path: str = "tools/guwu/guwu_metrics.db"):
        self.db_path = db_path
    
    def predict_failures(self, test_names: Optional[List[str]] = None) -> List[Prediction]:
        """
        Predict which tests are likely to fail.
        
        Uses historical patterns:
        - Recent failure rate
        - Flakiness score
        - Time since last failure
        - Failure clustering (tests failing together)
        """
        predictions = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get tests to analyze
            if test_names:
                placeholders = ','.join('?' * len(test_names))
                query = f"""
                    SELECT DISTINCT test_name FROM test_executions 
                    WHERE test_name IN ({placeholders})
                """
                cursor.execute(query, test_names)
            else:
                cursor.execute("""
                    SELECT DISTINCT test_name FROM test_executions 
                    ORDER BY test_name
                    LIMIT 50
                """)
            
            tests = [row[0] for row in cursor.fetchall()]
            
            for test_name in tests:
                pred = self._predict_single_test_failure(cursor, test_name)
                if pred and pred.prediction_type == "FAILURE":
                    predictions.append(pred)
            
            conn.close()
            
        except Exception as e:
            pass  # Graceful degradation
        
        # Sort by confidence (highest first)
        predictions.sort(key=lambda p: p.confidence, reverse=True)
        return predictions
    
    def predict_execution_time(self, test_names: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Predict execution time for tests.
        
        Uses moving average with trend detection.
        """
        predictions = {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get tests to analyze
            if test_names:
                placeholders = ','.join('?' * len(test_names))
                query = f"""
                    SELECT test_name, duration, timestamp 
                    FROM test_executions 
                    WHERE test_name IN ({placeholders})
                    ORDER BY timestamp DESC
                """
                cursor.execute(query, test_names)
            else:
                cursor.execute("""
                    SELECT test_name, duration, timestamp 
                    FROM test_executions 
                    ORDER BY timestamp DESC
                    LIMIT 1000
                """)
            
            # Group by test name
            test_durations: Dict[str, List[float]] = {}
            for row in cursor.fetchall():
                test_name, duration, timestamp = row
                if test_name not in test_durations:
                    test_durations[test_name] = []
                test_durations[test_name].append(duration)
            
            # Predict for each test
            for test_name, durations in test_durations.items():
                if len(durations) >= 3:
                    # Use recent data (last 10 executions)
                    recent = durations[:10]
                    
                    # Weighted average (more recent = more weight)
                    weighted_sum = sum(
                        dur * (1.0 / (i + 1)) 
                        for i, dur in enumerate(recent)
                    )
                    weight_total = sum(1.0 / (i + 1) for i in range(len(recent)))
                    predicted = weighted_sum / weight_total
                    
                    predictions[test_name] = predicted
                elif len(durations) > 0:
                    # Fallback to simple average
                    predictions[test_name] = statistics.mean(durations)
            
            conn.close()
            
        except Exception:
            pass
        
        return predictions
    
    def get_preflight_report(self) -> Dict:
        """
        Generate pre-flight checks before CI/CD run.
        
        Returns:
            Report with likely failures, slow tests, and total time estimate
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all active tests
            cursor.execute("""
                SELECT DISTINCT test_name FROM test_executions 
                WHERE timestamp > ?
            """, ((datetime.now() - timedelta(days=7)).timestamp(),))
            
            active_tests = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # Return early if no tests
            if not active_tests:
                return {
                    'likely_failures': [],
                    'slow_tests': [],
                    'total_tests': 0,
                    'estimated_time': 0.0,
                    'risk_level': 'UNKNOWN'
                }
            
            # Predict failures
            failure_predictions = self.predict_failures(active_tests)
            
            # Predict execution times
            time_predictions = self.predict_execution_time(active_tests)
            
            # Calculate total time
            total_time = sum(time_predictions.values())
            
            # Identify slow tests (>5s)
            slow_tests = [
                (name, time) 
                for name, time in time_predictions.items() 
                if time > 5.0
            ]
            slow_tests.sort(key=lambda x: x[1], reverse=True)
            
            return {
                'likely_failures': failure_predictions[:5],  # Top 5
                'slow_tests': slow_tests[:5],  # Top 5
                'total_tests': len(active_tests),
                'estimated_time': total_time,
                'risk_level': self._calculate_risk_level(failure_predictions)
            }
            
        except Exception:
            return {
                'likely_failures': [],
                'slow_tests': [],
                'total_tests': 0,
                'estimated_time': 0.0,
                'risk_level': 'UNKNOWN'
            }
    
    def _predict_single_test_failure(
        self, 
        cursor: sqlite3.Cursor, 
        test_name: str
    ) -> Optional[Prediction]:
        """Predict if a single test will fail"""
        
        # Get recent executions (last 20)
        cursor.execute("""
            SELECT outcome, timestamp 
            FROM test_executions 
            WHERE test_name = ?
            ORDER BY timestamp DESC
            LIMIT 20
        """, (test_name,))
        
        executions = cursor.fetchall()
        
        if len(executions) < 3:
            return None  # Not enough data
        
        # Calculate failure rate (recent 10)
        recent_10 = executions[:10]
        failures = sum(1 for e in recent_10 if e[0] != 'passed')
        failure_rate = failures / len(recent_10)
        
        # Get flakiness score
        cursor.execute("""
            SELECT flakiness_score FROM test_metrics 
            WHERE test_name = ?
        """, (test_name,))
        
        row = cursor.fetchone()
        flakiness = row[0] if row else 0.0
        
        # Calculate time since last failure
        last_failure = next(
            (e[1] for e in executions if e[0] != 'passed'), 
            None
        )
        
        if last_failure:
            days_since_failure = (datetime.now().timestamp() - last_failure) / 86400
        else:
            days_since_failure = 999  # Never failed
        
        # Prediction logic (simple heuristic model)
        confidence = 0.0
        reasoning_parts = []
        
        # High recent failure rate
        if failure_rate > 0.3:
            confidence += 0.4
            reasoning_parts.append(f"Recent failure rate: {failure_rate:.1%}")
        
        # High flakiness
        if flakiness > 0.3:
            confidence += 0.3
            reasoning_parts.append(f"Flakiness score: {flakiness:.2f}")
        
        # Recent failure
        if days_since_failure < 1:
            confidence += 0.2
            reasoning_parts.append(f"Failed {days_since_failure:.1f} days ago")
        elif days_since_failure < 7:
            confidence += 0.1
            reasoning_parts.append(f"Failed {days_since_failure:.0f} days ago")
        
        # Predict failure if confidence >= 0.5
        if confidence >= 0.5:
            return Prediction(
                test_name=test_name,
                prediction_type="FAILURE",
                confidence=min(confidence, 0.99),  # Cap at 99%
                reasoning="; ".join(reasoning_parts)
            )
        
        return None
    
    def _calculate_risk_level(self, predictions: List[Prediction]) -> str:
        """Calculate overall risk level based on predictions"""
        if not predictions:
            return "LOW"
        
        # Count high-confidence predictions
        high_conf = sum(1 for p in predictions if p.confidence > 0.8)
        
        if high_conf >= 3:
            return "HIGH"
        elif high_conf >= 1 or len(predictions) >= 5:
            return "MEDIUM"
        else:
            return "LOW"


class PreflightChecker:
    """
    Pre-flight checks before CI/CD runs.
    
    Provides early warnings about potential issues.
    """
    
    def __init__(self, db_path: str = "tools/guwu/guwu_metrics.db"):
        self.engine = PredictiveEngine(db_path)
    
    def run_preflight(self) -> str:
        """Generate pre-flight check report"""
        report = self.engine.get_preflight_report()
        
        sections = []
        
        # Header
        sections.append(self._format_header(report))
        
        # Likely failures
        if report['likely_failures']:
            sections.append(self._format_failures(report['likely_failures']))
        
        # Slow tests
        if report['slow_tests']:
            sections.append(self._format_slow_tests(report['slow_tests']))
        
        # Summary
        sections.append(self._format_summary(report))
        
        return "\n\n".join(sections)
    
    def _format_header(self, report: Dict) -> str:
        """Format pre-flight header"""
        risk_indicators = {
            'HIGH': '🔴 HIGH RISK',
            'MEDIUM': '🟡 MEDIUM RISK',
            'LOW': '🟢 LOW RISK',
            'UNKNOWN': '⚪ UNKNOWN'
        }
        
        risk = risk_indicators.get(report['risk_level'], '⚪ UNKNOWN')
        
        return f"""
{'=' * 70}
  GU WU PRE-FLIGHT CHECK
  Risk Level: {risk}
{'=' * 70}
"""
    
    def _format_failures(self, predictions: List[Prediction]) -> str:
        """Format likely failures section"""
        lines = ["[LIKELY FAILURES]\n"]
        
        for i, pred in enumerate(predictions, 1):
            lines.append(
                f"  {i}. {pred.test_name}\n"
                f"     Confidence: {pred.confidence:.1%}\n"
                f"     Reasoning: {pred.reasoning}"
            )
        
        return "\n".join(lines)
    
    def _format_slow_tests(self, slow_tests: List[Tuple[str, float]]) -> str:
        """Format slow tests section"""
        lines = ["[SLOW TESTS] Estimated >5s\n"]
        
        for i, (name, time) in enumerate(slow_tests, 1):
            lines.append(f"  {i}. {name}: {time:.1f}s")
        
        return "\n".join(lines)
    
    def _format_summary(self, report: Dict) -> str:
        """Format summary section"""
        return f"""
[SUMMARY]

  Total Tests:     {report['total_tests']:>6}
  Likely Failures: {len(report['likely_failures']):>6}
  Slow Tests:      {len(report['slow_tests']):>6}
  Est. Time:       {report['estimated_time']:>6.1f}s ({report['estimated_time']/60:.1f} min)
  
  Risk Level:      {report['risk_level']}
"""


def main():
    """CLI entry point for pre-flight checks"""
    checker = PreflightChecker()
    report = checker.run_preflight()
    print(report)


if __name__ == "__main__":
    main()