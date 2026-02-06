"""
Feng Shui Reflector - Meta-Learning Engine

Tracks fix attempts, analyzes patterns, generates insights.
Inspired by Gu Wu Phase 6 reflection capabilities.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class SuccessRateAnalysis:
    """Analysis of fix success rates"""
    fix_type: str
    total_attempts: int
    success_count: int
    success_rate: float
    predicted_rate: float
    calibration_error: float  # Difference between predicted and actual


@dataclass
class StrategyAnalysis:
    """Analysis of strategy performance over time"""
    strategy_name: str
    total_attempts: int
    success_rate: float
    avg_time_ms: float
    trend: str  # IMPROVING/STABLE/DECLINING


@dataclass
class CalibrationIssue:
    """Confidence calibration issue"""
    fix_type: str
    predicted_success: float
    actual_success: float
    error: float  # abs(predicted - actual)
    severity: str  # CRITICAL if error > 0.3, HIGH if > 0.15


@dataclass
class RecurringPattern:
    """Recurring violation pattern"""
    violation_type: str
    modules_affected: List[str]
    frequency: int
    recommendation: str


@dataclass
class ReflectionInsight:
    """Actionable insight from reflection"""
    priority: str  # CRITICAL/HIGH/MEDIUM/LOW
    category: str  # STRATEGY/CALIBRATION/PATTERN/PERFORMANCE
    description: str
    recommendation: str
    impact: str  # Expected impact if followed


class FengShuiReflector:
    """Meta-learning engine for Feng Shui self-improvement"""
    
    def __init__(self, db_path: Path = None):
        """
        Initialize reflector with database
        
        Args:
            db_path: Path to reflection database (default: tools/fengshui/reflection.db)
        """
        if db_path is None:
            db_path = Path(__file__).parent / 'reflection.db'
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with schema"""
        # Read schema from reflection_schema.sql
        schema_path = Path(__file__).parent / 'reflection_schema.sql'
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Execute schema
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        conn.close()
    
    def record_fix_attempt(
        self,
        fix_type: str,
        predicted_success: float,
        actual_success: bool,
        module_name: str,
        strategy_used: str,
        execution_time_ms: int = 0,
        error_message: str = None
    ):
        """
        Track each fix attempt for learning
        
        This is the core data collection mechanism.
        
        Args:
            fix_type: Type of fix applied (e.g., 'DI_VIOLATION', 'BLUEPRINT')
            predicted_success: Confidence prediction (0.0-1.0)
            actual_success: Whether fix actually succeeded
            module_name: Module being fixed
            strategy_used: Strategy that was used
            execution_time_ms: Time taken to execute
            error_message: Error if fix failed
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO fix_attempts 
            (timestamp, fix_type, module_name, strategy_used, 
             predicted_success, actual_success, execution_time_ms, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            fix_type,
            module_name,
            strategy_used,
            predicted_success,
            1 if actual_success else 0,
            execution_time_ms,
            error_message
        ))
        
        conn.commit()
        conn.close()
        
        # Update strategy performance
        self._update_strategy_performance(strategy_used, actual_success, execution_time_ms)
    
    def analyze_fix_success_rates(self) -> Dict[str, SuccessRateAnalysis]:
        """
        Calculate actual vs predicted success rates
        
        Returns:
            Analysis showing calibration accuracy per fix type
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                fix_type,
                COUNT(*) as total,
                SUM(actual_success) as successes,
                AVG(predicted_success) as avg_predicted,
                AVG(actual_success) as avg_actual
            FROM fix_attempts
            GROUP BY fix_type
            HAVING COUNT(*) >= 3
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        analyses = {}
        for row in rows:
            fix_type, total, successes, avg_predicted, avg_actual = row
            success_rate = avg_actual  # Already 0.0-1.0
            predicted_rate = avg_predicted
            calibration_error = abs(predicted_rate - success_rate)
            
            analyses[fix_type] = SuccessRateAnalysis(
                fix_type=fix_type,
                total_attempts=total,
                success_count=successes,
                success_rate=success_rate,
                predicted_rate=predicted_rate,
                calibration_error=calibration_error
            )
        
        return analyses
    
    def analyze_strategy_performance(self) -> List[StrategyAnalysis]:
        """
        Track which strategies work best over time
        
        Returns:
            Strategies with IMPROVING/STABLE/DECLINING trends
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                strategy_name,
                total_attempts,
                success_count,
                avg_execution_time_ms,
                trend
            FROM strategy_performance
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        analyses = []
        for row in rows:
            strategy_name, total, successes, avg_time, trend = row
            success_rate = successes / total if total > 0 else 0.0
            
            analyses.append(StrategyAnalysis(
                strategy_name=strategy_name,
                total_attempts=total,
                success_rate=success_rate,
                avg_time_ms=avg_time,
                trend=trend
            ))
        
        return analyses
    
    def calibrate_confidence(self) -> List[CalibrationIssue]:
        """
        Detect confidence miscalibrations (>15% error)
        
        Returns:
            Issues requiring confidence adjustment
        """
        success_rates = self.analyze_fix_success_rates()
        issues = []
        
        for fix_type, analysis in success_rates.items():
            if analysis.calibration_error > 0.15:
                severity = 'CRITICAL' if analysis.calibration_error > 0.3 else 'HIGH'
                issues.append(CalibrationIssue(
                    fix_type=fix_type,
                    predicted_success=analysis.predicted_rate,
                    actual_success=analysis.success_rate,
                    error=analysis.calibration_error,
                    severity=severity
                ))
        
        return issues
    
    def recognize_patterns(self) -> List[RecurringPattern]:
        """
        Identify recurring violations across modules
        
        Returns:
            Patterns suggesting systemic issues
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find fix types that appear in multiple modules
        cursor.execute("""
            SELECT 
                fix_type,
                COUNT(DISTINCT module_name) as module_count,
                GROUP_CONCAT(DISTINCT module_name) as modules,
                COUNT(*) as frequency
            FROM fix_attempts
            WHERE timestamp >= datetime('now', '-30 days')
            GROUP BY fix_type
            HAVING module_count >= 3
            ORDER BY frequency DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        patterns = []
        for row in rows:
            fix_type, module_count, modules_str, frequency = row
            modules = modules_str.split(',') if modules_str else []
            
            # Generate recommendation based on pattern
            if frequency >= 10:
                recommendation = f"SYSTEMIC ISSUE: {fix_type} appears in {module_count} modules. Consider project-wide refactoring."
            else:
                recommendation = f"Recurring {fix_type} in {module_count} modules. May indicate architectural issue."
            
            patterns.append(RecurringPattern(
                violation_type=fix_type,
                modules_affected=modules,
                frequency=frequency,
                recommendation=recommendation
            ))
        
        return patterns
    
    def generate_insights(self) -> List[ReflectionInsight]:
        """
        Synthesize all analyses into actionable recommendations
        
        Returns:
            Prioritized insights (CRITICAL/HIGH/MEDIUM/LOW)
        """
        insights = []
        
        # 1. Check calibration issues
        calibration_issues = self.calibrate_confidence()
        for issue in calibration_issues:
            insights.append(ReflectionInsight(
                priority=issue.severity,
                category='CALIBRATION',
                description=f"Confidence miscalibration for {issue.fix_type}",
                recommendation=f"Adjust predicted success from {issue.predicted_success:.2f} to {issue.actual_success:.2f}",
                impact="Improved action selection accuracy"
            ))
        
        # 2. Check strategy performance
        strategies = self.analyze_strategy_performance()
        for strategy in strategies:
            if strategy.trend == 'DECLINING':
                insights.append(ReflectionInsight(
                    priority='HIGH',
                    category='STRATEGY',
                    description=f"Strategy '{strategy.strategy_name}' performance declining",
                    recommendation=f"Consider switching to alternative strategy (current rate: {strategy.success_rate:.1%})",
                    impact="Improved fix success rate"
                ))
            elif strategy.trend == 'IMPROVING':
                insights.append(ReflectionInsight(
                    priority='LOW',
                    category='STRATEGY',
                    description=f"Strategy '{strategy.strategy_name}' performing well",
                    recommendation=f"Continue using this strategy (success rate: {strategy.success_rate:.1%})",
                    impact="Maintain current effectiveness"
                ))
        
        # 3. Check recurring patterns
        patterns = self.recognize_patterns()
        for pattern in patterns:
            priority = 'HIGH' if pattern.frequency >= 10 else 'MEDIUM'
            insights.append(ReflectionInsight(
                priority=priority,
                category='PATTERN',
                description=f"Recurring {pattern.violation_type} across {len(pattern.modules_affected)} modules",
                recommendation=pattern.recommendation,
                impact="Address systemic architectural issue"
            ))
        
        # 4. Performance insights
        slow_fixes = self._identify_slow_fixes()
        for fix_type, avg_time in slow_fixes:
            insights.append(ReflectionInsight(
                priority='MEDIUM',
                category='PERFORMANCE',
                description=f"Fix type '{fix_type}' averaging {avg_time:.0f}ms",
                recommendation=f"Consider optimizing {fix_type} fix implementation",
                impact="Faster autonomous improvement cycles"
            ))
        
        # Sort by priority
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        insights.sort(key=lambda x: priority_order[x.priority])
        
        # Store insights in database
        self._store_insights(insights)
        
        return insights
    
    def get_strategy_success_rate(self, strategy_name: str) -> float:
        """
        Get success rate for a specific strategy
        
        Args:
            strategy_name: Strategy to query
            
        Returns:
            Success rate (0.0-1.0), or 0.5 if no data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT success_count, total_attempts
            FROM strategy_performance
            WHERE strategy_name = ?
        """, (strategy_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row[1] > 0:
            return row[0] / row[1]
        return 0.5  # Default 50% if no history
    
    def _update_strategy_performance(self, strategy: str, success: bool, time_ms: int):
        """Update strategy performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if strategy exists
        cursor.execute("""
            SELECT total_attempts, success_count, avg_execution_time_ms
            FROM strategy_performance
            WHERE strategy_name = ?
        """, (strategy,))
        
        row = cursor.fetchone()
        
        if row:
            # Update existing
            total, successes, avg_time = row
            new_total = total + 1
            new_successes = successes + (1 if success else 0)
            # Running average for execution time
            new_avg_time = ((avg_time * total) + time_ms) / new_total
            
            # Calculate trend (compare last 10 vs previous 10)
            trend = self._calculate_trend(strategy, new_successes, new_total)
            
            cursor.execute("""
                UPDATE strategy_performance
                SET total_attempts = ?,
                    success_count = ?,
                    avg_execution_time_ms = ?,
                    trend = ?,
                    last_updated = ?
                WHERE strategy_name = ?
            """, (new_total, new_successes, new_avg_time, trend, datetime.now().isoformat(), strategy))
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO strategy_performance
                (strategy_name, total_attempts, success_count, avg_execution_time_ms, trend, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (strategy, 1, 1 if success else 0, time_ms, 'STABLE', datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def _calculate_trend(self, strategy: str, current_successes: int, current_total: int) -> str:
        """
        Calculate performance trend for strategy
        
        Compares recent success rate vs historical average.
        
        Args:
            strategy: Strategy name
            current_successes: Total successes so far
            current_total: Total attempts so far
            
        Returns:
            'IMPROVING', 'STABLE', or 'DECLINING'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get last 10 attempts
        cursor.execute("""
            SELECT actual_success
            FROM fix_attempts
            WHERE strategy_used = ?
            ORDER BY timestamp DESC
            LIMIT 10
        """, (strategy,))
        
        recent_rows = cursor.fetchall()
        conn.close()
        
        if len(recent_rows) < 10:
            return 'STABLE'  # Not enough data for trend
        
        # Calculate recent success rate
        recent_successes = sum(row[0] for row in recent_rows)
        recent_rate = recent_successes / 10
        
        # Calculate overall success rate
        overall_rate = current_successes / current_total if current_total > 0 else 0.0
        
        # Compare
        if recent_rate > overall_rate + 0.1:
            return 'IMPROVING'
        elif recent_rate < overall_rate - 0.1:
            return 'DECLINING'
        else:
            return 'STABLE'
    
    def _identify_slow_fixes(self, threshold_ms: int = 10000) -> List[tuple]:
        """
        Identify fix types that take longer than threshold
        
        Args:
            threshold_ms: Time threshold in milliseconds
            
        Returns:
            List of (fix_type, avg_time_ms) tuples
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT fix_type, AVG(execution_time_ms) as avg_time
            FROM fix_attempts
            GROUP BY fix_type
            HAVING avg_time > ?
            ORDER BY avg_time DESC
        """, (threshold_ms,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return rows
    
    def _store_insights(self, insights: List[ReflectionInsight]):
        """Store generated insights in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for insight in insights:
            cursor.execute("""
                INSERT INTO reflection_insights
                (timestamp, insight_type, priority, description, recommendation, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                insight.category,
                insight.priority,
                insight.description,
                insight.recommendation,
                'OPEN'
            ))
        
        conn.commit()
        conn.close()
    
    def get_open_insights(self, priority: str = None) -> List[ReflectionInsight]:
        """
        Get open insights (not yet resolved)
        
        Args:
            priority: Filter by priority (None = all priorities)
            
        Returns:
            List of open insights
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if priority:
            cursor.execute("""
                SELECT insight_type, priority, description, recommendation
                FROM reflection_insights
                WHERE status = 'OPEN' AND priority = ?
                ORDER BY timestamp DESC
            """, (priority,))
        else:
            cursor.execute("""
                SELECT insight_type, priority, description, recommendation
                FROM reflection_insights
                WHERE status = 'OPEN'
                ORDER BY 
                    CASE priority
                        WHEN 'CRITICAL' THEN 0
                        WHEN 'HIGH' THEN 1
                        WHEN 'MEDIUM' THEN 2
                        WHEN 'LOW' THEN 3
                    END,
                    timestamp DESC
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        insights = []
        for row in rows:
            insights.append(ReflectionInsight(
                category=row[0],
                priority=row[1],
                description=row[2],
                recommendation=row[3],
                impact=""  # Not stored in DB
            ))
        
        return insights
    
    def mark_insight_resolved(self, description: str):
        """
        Mark an insight as resolved
        
        Args:
            description: Description of insight to mark resolved
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE reflection_insights
            SET status = 'RESOLVED'
            WHERE description = ? AND status = 'OPEN'
        """, (description,))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self) -> Dict:
        """
        Get overall reflection statistics
        
        Returns:
            Dict with counts and metrics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total attempts
        cursor.execute("SELECT COUNT(*) FROM fix_attempts")
        total_attempts = cursor.fetchone()[0]
        
        # Success rate
        cursor.execute("SELECT AVG(actual_success) FROM fix_attempts")
        overall_success_rate = cursor.fetchone()[0] or 0.0
        
        # Open insights by priority
        cursor.execute("""
            SELECT priority, COUNT(*)
            FROM reflection_insights
            WHERE status = 'OPEN'
            GROUP BY priority
        """)
        insights_by_priority = dict(cursor.fetchall())
        
        # Strategy count
        cursor.execute("SELECT COUNT(*) FROM strategy_performance")
        strategy_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_attempts': total_attempts,
            'overall_success_rate': overall_success_rate,
            'open_insights': insights_by_priority,
            'strategies_tracked': strategy_count
        }


def main():
    """CLI entry point for reflection analysis"""
    import sys
    
    reflector = FengShuiReflector()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--analyze':
        # Generate and display insights
        print("\n" + "="*60)
        print("Feng Shui Reflection Analysis")
        print("="*60 + "\n")
        
        insights = reflector.generate_insights()
        
        if not insights:
            print("✅ No insights - system performing well!")
        else:
            for insight in insights:
                icon = {'CRITICAL': '🔴', 'HIGH': '🟡', 'MEDIUM': '🔵', 'LOW': '⚪'}.get(insight.priority, '⚪')
                print(f"{icon} [{insight.priority}] {insight.category}")
                print(f"   {insight.description}")
                print(f"   → {insight.recommendation}")
                print()
        
        # Show statistics
        stats = reflector.get_statistics()
        print("\n" + "="*60)
        print(f"Total attempts: {stats['total_attempts']}")
        print(f"Success rate: {stats['overall_success_rate']:.1%}")
        print(f"Strategies tracked: {stats['strategies_tracked']}")
        print(f"Open insights: {sum(stats['open_insights'].values())}")
        print("="*60 + "\n")
    
    else:
        print("Usage: python -m tools.fengshui.reflector --analyze")
        sys.exit(1)


if __name__ == '__main__':
    main()