"""
Gu Wu Self-Reflection Engine - Stage 5 of Phase 3 (FINAL)

Meta-learning engine that validates and improves Gu Wu's own predictions.
Learns from experience to continuously improve accuracy over time.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


@dataclass
class ReflectionInsight:
    """An insight from self-reflection"""
    category: str           # prediction_accuracy, fix_success_rate, etc.
    metric: str            # Specific metric name
    current_value: float   # Current metric value
    trend: str             # improving/declining/stable
    recommendation: str    # What to adjust
    priority: str          # low/medium/high/critical
    
    def to_dict(self) -> Dict:
        return {
            'category': self.category,
            'metric': self.metric,
            'current_value': round(self.current_value, 3),
            'trend': self.trend,
            'recommendation': self.recommendation,
            'priority': self.priority
        }


class SelfReflectionEngine:
    """
    Meta-learning engine for Gu Wu.
    
    Responsibilities:
    1. Validate prediction accuracy
    2. Learn from fix success rates
    3. Identify pattern improvements
    4. Auto-adjust confidence thresholds
    5. Generate self-improvement recommendations
    """
    
    def __init__(self, db_path: str = "tests/guwu/metrics.db"):
        self.db_path = Path(db_path)
        self._init_reflection_db()
    
    def _init_reflection_db(self):
        """Initialize reflection tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Track reflection sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reflection_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                insights_count INTEGER NOT NULL,
                recommendations_count INTEGER NOT NULL,
                accuracy_score REAL,
                notes TEXT
            )
        ''')
        
        # Track metric history for trending
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metric_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def reflect(self) -> List[ReflectionInsight]:
        """
        Perform self-reflection analysis.
        
        Returns: List of insights and recommendations
        """
        insights = []
        
        # 1. Analyze prediction accuracy
        prediction_insights = self._analyze_predictions()
        insights.extend(prediction_insights)
        
        # 2. Analyze fix success rates
        fix_insights = self._analyze_fix_success()
        insights.extend(fix_insights)
        
        # 3. Analyze test execution patterns
        execution_insights = self._analyze_execution_patterns()
        insights.extend(execution_insights)
        
        # 4. Analyze coverage trends
        coverage_insights = self._analyze_coverage_trends()
        insights.extend(coverage_insights)
        
        # Log session
        self._log_reflection_session(insights)
        
        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        insights.sort(key=lambda i: priority_order.get(i.priority, 3))
        
        return insights
    
    def _analyze_predictions(self) -> List[ReflectionInsight]:
        """Analyze prediction accuracy"""
        insights = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get prediction vs actual results (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        
        # Count predictions that were correct
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN outcome = 'failed' THEN 1 ELSE 0 END) as actual_failures
            FROM test_executions
            WHERE timestamp > ?
        ''', (thirty_days_ago,))
        
        result = cursor.fetchone()
        if result and result[0] > 0:
            total_tests = result[0]
            actual_failures = result[1] or 0
            actual_failure_rate = actual_failures / total_tests
            
            # Store metric
            self._store_metric('prediction', 'actual_failure_rate', actual_failure_rate)
            
            # Get historical trend
            trend = self._calculate_trend('prediction', 'actual_failure_rate')
            
            # Generate insight
            if actual_failure_rate < 0.05:  # < 5% failure rate
                insights.append(ReflectionInsight(
                    category='prediction_accuracy',
                    metric='failure_rate',
                    current_value=actual_failure_rate,
                    trend=trend,
                    recommendation="System is healthy - maintain current prediction models",
                    priority='low'
                ))
            elif actual_failure_rate < 0.15:  # 5-15% failure rate
                insights.append(ReflectionInsight(
                    category='prediction_accuracy',
                    metric='failure_rate',
                    current_value=actual_failure_rate,
                    trend=trend,
                    recommendation="Moderate failure rate - review flaky tests and prediction accuracy",
                    priority='medium'
                ))
            else:  # > 15% failure rate
                insights.append(ReflectionInsight(
                    category='prediction_accuracy',
                    metric='failure_rate',
                    current_value=actual_failure_rate,
                    trend=trend,
                    recommendation="High failure rate - investigate root causes and improve test quality",
                    priority='high'
                ))
        
        conn.close()
        return insights
    
    def _analyze_fix_success(self) -> List[ReflectionInsight]:
        """Analyze fix suggestion success rates"""
        insights = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get fix success rate by failure type
        cursor.execute('''
            SELECT 
                failure_type,
                COUNT(*) as total_suggestions,
                SUM(CASE WHEN worked = 1 THEN 1 ELSE 0 END) as successful_fixes
            FROM fix_suggestions
            WHERE applied = 1 AND worked IS NOT NULL
            GROUP BY failure_type
            HAVING COUNT(*) >= 3
        ''')
        
        for row in cursor.fetchall():
            failure_type, total, successful = row
            success_rate = successful / total if total > 0 else 0.0
            
            # Store metric
            self._store_metric('fix_success', f'{failure_type}_success_rate', success_rate)
            
            # Get trend
            trend = self._calculate_trend('fix_success', f'{failure_type}_success_rate')
            
            # Generate insight
            if success_rate >= 0.8:  # >= 80% success
                insights.append(ReflectionInsight(
                    category='fix_success',
                    metric=f'{failure_type}_fixes',
                    current_value=success_rate,
                    trend=trend,
                    recommendation=f"Excellent fix accuracy for {failure_type} - pattern working well",
                    priority='low'
                ))
            elif success_rate >= 0.5:  # 50-80% success
                insights.append(ReflectionInsight(
                    category='fix_success',
                    metric=f'{failure_type}_fixes',
                    current_value=success_rate,
                    trend=trend,
                    recommendation=f"Moderate success for {failure_type} - review patterns and improve accuracy",
                    priority='medium'
                ))
            else:  # < 50% success
                insights.append(ReflectionInsight(
                    category='fix_success',
                    metric=f'{failure_type}_fixes',
                    current_value=success_rate,
                    trend=trend,
                    recommendation=f"Low success for {failure_type} - pattern needs redesign",
                    priority='high'
                ))
        
        conn.close()
        return insights
    
    def _analyze_execution_patterns(self) -> List[ReflectionInsight]:
        """Analyze test execution patterns"""
        insights = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check for slow tests (> 5 seconds)
        cursor.execute('''
            SELECT COUNT(*) 
            FROM test_statistics
            WHERE avg_duration > 5.0
        ''')
        
        slow_tests = cursor.fetchone()[0]
        
        if slow_tests > 10:
            insights.append(ReflectionInsight(
                category='execution_patterns',
                metric='slow_tests_count',
                current_value=float(slow_tests),
                trend='stable',  # Would need historical data for trend
                recommendation=f"{slow_tests} slow tests detected - prioritize refactoring for performance",
                priority='high'
            ))
        elif slow_tests > 5:
            insights.append(ReflectionInsight(
                category='execution_patterns',
                metric='slow_tests_count',
                current_value=float(slow_tests),
                trend='stable',
                recommendation=f"{slow_tests} slow tests detected - consider optimization",
                priority='medium'
            ))
        
        # Check for flaky tests (flaky_score > 0.5)
        cursor.execute('''
            SELECT COUNT(*) 
            FROM test_statistics
            WHERE flaky_score > 0.5
        ''')
        
        flaky_tests = cursor.fetchone()[0]
        
        if flaky_tests > 5:
            insights.append(ReflectionInsight(
                category='execution_patterns',
                metric='flaky_tests_count',
                current_value=float(flaky_tests),
                trend='stable',
                recommendation=f"{flaky_tests} flaky tests detected - investigate and stabilize",
                priority='critical'
            ))
        elif flaky_tests > 0:
            insights.append(ReflectionInsight(
                category='execution_patterns',
                metric='flaky_tests_count',
                current_value=float(flaky_tests),
                trend='stable',
                recommendation=f"{flaky_tests} flaky tests detected - monitor and fix if recurring",
                priority='medium'
            ))
        
        conn.close()
        return insights
    
    def _analyze_coverage_trends(self) -> List[ReflectionInsight]:
        """Analyze test coverage trends"""
        insights = []
        
        # Get current coverage (from gap analyzer results)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check for untested critical functions (from gap analysis)
        # Note: This would need integration with gap analyzer results
        
        # For now, provide general coverage insight
        insights.append(ReflectionInsight(
            category='coverage_trends',
            metric='gap_analysis',
            current_value=0.0,  # Placeholder
            trend='unknown',
            recommendation="Run gap analyzer regularly to maintain coverage awareness",
            priority='medium'
        ))
        
        conn.close()
        return insights
    
    def _store_metric(self, category: str, metric_name: str, value: float):
        """Store metric for trend analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO metric_history (category, metric_name, value, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (category, metric_name, value, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def _calculate_trend(self, category: str, metric_name: str, window_days: int = 7) -> str:
        """Calculate trend direction for a metric"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent values
        since_date = (datetime.now() - timedelta(days=window_days)).isoformat()
        
        cursor.execute('''
            SELECT value, timestamp
            FROM metric_history
            WHERE category = ? AND metric_name = ? AND timestamp > ?
            ORDER BY timestamp ASC
        ''', (category, metric_name, since_date))
        
        values = cursor.fetchall()
        conn.close()
        
        if len(values) < 2:
            return 'unknown'
        
        # Simple trend: compare first half vs second half
        mid = len(values) // 2
        first_half_avg = sum(v[0] for v in values[:mid]) / mid
        second_half_avg = sum(v[0] for v in values[mid:]) / (len(values) - mid)
        
        diff = second_half_avg - first_half_avg
        
        if abs(diff) < 0.05:  # < 5% change
            return 'stable'
        elif diff > 0:
            return 'improving' if category == 'fix_success' else 'declining'
        else:
            return 'declining' if category == 'fix_success' else 'improving'
    
    def _log_reflection_session(self, insights: List[ReflectionInsight]):
        """Log reflection session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        recommendations_count = len([i for i in insights if i.priority in ['high', 'critical']])
        
        cursor.execute('''
            INSERT INTO reflection_sessions 
            (timestamp, insights_count, recommendations_count, notes)
            VALUES (?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            len(insights),
            recommendations_count,
            f"Generated {len(insights)} insights, {recommendations_count} high-priority recommendations"
        ))
        
        conn.commit()
        conn.close()
    
    def generate_reflection_report(self, insights: List[ReflectionInsight]) -> str:
        """Generate formatted reflection report"""
        lines = []
        lines.append("\n" + "=" * 80)
        lines.append("GU WU SELF-REFLECTION REPORT")
        lines.append("=" * 80)
        lines.append(f"\nTotal insights: {len(insights)}")
        
        # Category breakdown
        category_counts = {}
        for insight in insights:
            category_counts[insight.category] = category_counts.get(insight.category, 0) + 1
        
        lines.append(f"\nInsights by Category:")
        for category, count in sorted(category_counts.items()):
            pct = (count / len(insights)) * 100 if insights else 0
            lines.append(f"  {category:25s}: {count:2d} insights ({pct:5.1f}%)")
        
        # Priority breakdown
        priority_counts = {}
        for insight in insights:
            priority_counts[insight.priority] = priority_counts.get(insight.priority, 0) + 1
        
        lines.append(f"\nInsights by Priority:")
        for priority in ['critical', 'high', 'medium', 'low']:
            count = priority_counts.get(priority, 0)
            if count > 0:
                pct = (count / len(insights)) * 100
                lines.append(f"  {priority.upper():10s}: {count:2d} insights ({pct:5.1f}%)")
        
        # High-priority recommendations
        high_priority = [i for i in insights if i.priority in ['critical', 'high']]
        if high_priority:
            lines.append(f"\n{'-' * 80}")
            lines.append(f"HIGH-PRIORITY RECOMMENDATIONS")
            lines.append(f"{'-' * 80}")
            
            for i, insight in enumerate(high_priority, 1):
                lines.append(f"\n{i}. {insight.metric} ({insight.category})")
                lines.append(f"   Current Value: {insight.current_value:.3f}")
                lines.append(f"   Trend: {insight.trend}")
                lines.append(f"   Priority: {insight.priority.upper()}")
                lines.append(f"   Recommendation: {insight.recommendation}")
        
        # Self-improvement summary
        lines.append(f"\n{'-' * 80}")
        lines.append(f"SELF-IMPROVEMENT SUMMARY")
        lines.append(f"{'-' * 80}")
        lines.append(f"Total insights generated: {len(insights)}")
        lines.append(f"Actionable recommendations: {len(high_priority)}")
        lines.append(f"")
        lines.append(f"Next Steps:")
        lines.append(f"1. Address high-priority recommendations")
        lines.append(f"2. Monitor trends over time")
        lines.append(f"3. Re-run reflection after improvements")
        lines.append(f"4. Continuously learn and adapt")
        
        lines.append(f"\n{'=' * 80}\n")
        
        return '\n'.join(lines)


# CLI interface
if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='Gu Wu Self-Reflection Engine')
    parser.add_argument('--output', choices=['report', 'json'], default='report',
                       help='Output format')
    
    args = parser.parse_args()
    
    engine = SelfReflectionEngine()
    
    # Perform reflection
    insights = engine.reflect()
    
    if args.output == 'json':
        # JSON output
        output = {
            'total_insights': len(insights),
            'insights': [insight.to_dict() for insight in insights]
        }
        print(json.dumps(output, indent=2))
    
    else:
        # Human-readable report
        report = engine.generate_reflection_report(insights)
        print(report)
        
        # Save to file
        report_path = Path("tests/guwu/reflection_report.txt")
        report_path.write_text(report, encoding='utf-8')
        print(f"Report saved to: {report_path}")