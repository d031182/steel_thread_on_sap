"""
Gu Wu Phase 6: Enhanced Reflection Pattern
Meta-learning engine that learns from execution history and improves decision-making over time.

Philosophy: "Learn from experience, adapt strategies, calibrate confidence"
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class ReflectionInsightType(Enum):
    """Types of insights the reflector can generate"""
    STRATEGY_PERFORMANCE = "strategy_performance"
    CONFIDENCE_CALIBRATION = "confidence_calibration"
    PATTERN_RECOGNITION = "pattern_recognition"
    EXECUTION_EFFICIENCY = "execution_efficiency"
    LEARNING_RATE = "learning_rate"


@dataclass
class ReflectionInsight:
    """A meta-learning insight discovered through reflection"""
    insight_type: ReflectionInsightType
    description: str
    confidence: float  # 0.0-1.0
    supporting_data: Dict
    recommendation: str
    priority: str  # LOW, MEDIUM, HIGH, CRITICAL
    created_at: str


@dataclass
class StrategyPerformance:
    """Performance metrics for a strategy over time"""
    strategy_name: str
    total_uses: int
    success_count: int
    failure_count: int
    avg_duration: float
    success_rate: float
    avg_confidence: float
    trend: str  # IMPROVING, STABLE, DECLINING


@dataclass
class ConfidenceCalibration:
    """Calibration analysis for confidence predictions"""
    confidence_range: str  # e.g., "80-90%"
    predicted_success_rate: float
    actual_success_rate: float
    calibration_error: float
    sample_size: int
    recommendation: str


class GuWuReflector:
    """
    Enhanced Reflection Pattern Implementation
    
    Learns from execution history and improves Gu Wu's decision-making:
    - Tracks strategy performance over time
    - Calibrates confidence predictions
    - Recognizes success/failure patterns
    - Optimizes execution efficiency
    - Measures learning rate
    
    This is meta-learning: Gu Wu reflecting on its own performance.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize reflector with execution history database"""
        if db_path is None:
            db_path = str(Path(__file__).parent.parent / "execution_history.db")
        
        self.db_path = db_path
        self._init_reflection_tables()
    
    def _init_reflection_tables(self):
        """Create tables for tracking reflection insights"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Execution history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                goal TEXT NOT NULL,
                strategy_used TEXT,
                action_type TEXT,
                confidence REAL,
                success BOOLEAN,
                duration_ms REAL,
                error_message TEXT,
                context TEXT,
                executed_at TEXT NOT NULL
            )
        """)
        
        # Reflection insights table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reflection_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_type TEXT NOT NULL,
                description TEXT NOT NULL,
                confidence REAL NOT NULL,
                supporting_data TEXT,
                recommendation TEXT,
                priority TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        # Strategy performance tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                total_uses INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                avg_duration REAL DEFAULT 0,
                avg_confidence REAL DEFAULT 0,
                last_updated TEXT NOT NULL,
                UNIQUE(strategy_name)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def record_execution(
        self,
        session_id: str,
        goal: str,
        strategy_used: str,
        action_type: str,
        confidence: float,
        success: bool,
        duration_ms: float,
        error_message: Optional[str] = None,
        context: Optional[Dict] = None
    ):
        """Record an execution for future reflection"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO execution_history (
                session_id, goal, strategy_used, action_type, confidence,
                success, duration_ms, error_message, context, executed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            goal,
            strategy_used,
            action_type,
            confidence,
            success,
            duration_ms,
            error_message,
            json.dumps(context) if context else None,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        # Update strategy performance
        self._update_strategy_performance(strategy_used, success, duration_ms, confidence)
    
    def _update_strategy_performance(
        self,
        strategy_name: str,
        success: bool,
        duration_ms: float,
        confidence: float
    ):
        """Update performance metrics for a strategy"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current stats
        cursor.execute("""
            SELECT total_uses, success_count, failure_count, avg_duration, avg_confidence
            FROM strategy_performance WHERE strategy_name = ?
        """, (strategy_name,))
        
        row = cursor.fetchone()
        
        if row:
            total, success_count, failure_count, avg_dur, avg_conf = row
            new_total = total + 1
            new_success = success_count + (1 if success else 0)
            new_failure = failure_count + (0 if success else 1)
            new_avg_dur = (avg_dur * total + duration_ms) / new_total
            new_avg_conf = (avg_conf * total + confidence) / new_total
            
            cursor.execute("""
                UPDATE strategy_performance
                SET total_uses = ?, success_count = ?, failure_count = ?,
                    avg_duration = ?, avg_confidence = ?, last_updated = ?
                WHERE strategy_name = ?
            """, (new_total, new_success, new_failure, new_avg_dur, new_avg_conf,
                  datetime.now().isoformat(), strategy_name))
        else:
            cursor.execute("""
                INSERT INTO strategy_performance (
                    strategy_name, total_uses, success_count, failure_count,
                    avg_duration, avg_confidence, last_updated
                ) VALUES (?, 1, ?, ?, ?, ?, ?)
            """, (
                strategy_name,
                1 if success else 0,
                0 if success else 1,
                duration_ms,
                confidence,
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def analyze_strategy_performance(
        self,
        days: int = 30
    ) -> List[StrategyPerformance]:
        """Analyze how each strategy is performing over time"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get overall performance
        cursor.execute("""
            SELECT strategy_name, total_uses, success_count, failure_count,
                   avg_duration, avg_confidence
            FROM strategy_performance
            WHERE last_updated >= datetime('now', '-{} days')
        """.format(days))
        
        performances = []
        for row in cursor.fetchall():
            strategy, total, success, failure, avg_dur, avg_conf = row
            success_rate = success / total if total > 0 else 0.0
            
            # Determine trend by comparing recent vs older performance
            trend = self._calculate_trend(strategy, days)
            
            performances.append(StrategyPerformance(
                strategy_name=strategy,
                total_uses=total,
                success_count=success,
                failure_count=failure,
                avg_duration=avg_dur,
                success_rate=success_rate,
                avg_confidence=avg_conf,
                trend=trend
            ))
        
        conn.close()
        return performances
    
    def _calculate_trend(self, strategy_name: str, days: int) -> str:
        """Calculate if strategy performance is improving, stable, or declining"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent success rate (last 7 days)
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes
            FROM execution_history
            WHERE strategy_used = ?
              AND executed_at >= datetime('now', '-7 days')
        """, (strategy_name,))
        
        recent = cursor.fetchone()
        recent_rate = recent[1] / recent[0] if recent and recent[0] > 0 else None
        
        # Get older success rate (7-30 days ago)
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes
            FROM execution_history
            WHERE strategy_used = ?
              AND executed_at >= datetime('now', '-{} days')
              AND executed_at < datetime('now', '-7 days')
        """.format(days), (strategy_name,))
        
        older = cursor.fetchone()
        older_rate = older[1] / older[0] if older and older[0] > 0 else None
        
        conn.close()
        
        if recent_rate is None or older_rate is None:
            return "INSUFFICIENT_DATA"
        
        diff = recent_rate - older_rate
        if diff > 0.1:
            return "IMPROVING"
        elif diff < -0.1:
            return "DECLINING"
        else:
            return "STABLE"
    
    def calibrate_confidence(
        self,
        bins: int = 10
    ) -> List[ConfidenceCalibration]:
        """
        Analyze how well confidence predictions match actual outcomes
        
        Calibration error = |predicted_success_rate - actual_success_rate|
        Perfect calibration = 0.0 error
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        calibrations = []
        bin_size = 1.0 / bins
        
        for i in range(bins):
            lower = i * bin_size
            upper = (i + 1) * bin_size
            
            cursor.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
                       AVG(confidence) as avg_confidence
                FROM execution_history
                WHERE confidence >= ? AND confidence < ?
            """, (lower, upper))
            
            row = cursor.fetchone()
            total, successes, avg_conf = row
            
            if total and total > 0:
                actual_rate = successes / total
                predicted_rate = avg_conf if avg_conf else (lower + upper) / 2
                error = abs(predicted_rate - actual_rate)
                
                # Generate recommendation
                if error > 0.2:
                    rec = f"CRITICAL: Confidence in {lower:.0%}-{upper:.0%} range is poorly calibrated (±{error:.1%})"
                elif error > 0.1:
                    rec = f"Moderate miscalibration in {lower:.0%}-{upper:.0%} range (±{error:.1%})"
                else:
                    rec = f"Good calibration in {lower:.0%}-{upper:.0%} range"
                
                calibrations.append(ConfidenceCalibration(
                    confidence_range=f"{lower:.0%}-{upper:.0%}",
                    predicted_success_rate=predicted_rate,
                    actual_success_rate=actual_rate,
                    calibration_error=error,
                    sample_size=total,
                    recommendation=rec
                ))
        
        conn.close()
        return calibrations
    
    def recognize_patterns(self) -> List[ReflectionInsight]:
        """
        Recognize patterns in execution history
        
        Patterns to detect:
        - Actions that consistently fail with certain contexts
        - Time-of-day performance variations
        - Goal complexity correlations
        - Strategy combination effects
        """
        insights = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Pattern 1: Consistently failing action types
        cursor.execute("""
            SELECT action_type, COUNT(*) as total,
                   SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failures
            FROM execution_history
            WHERE executed_at >= datetime('now', '-30 days')
            GROUP BY action_type
            HAVING failures > 5 AND (failures * 1.0 / total) > 0.5
        """)
        
        for row in cursor.fetchall():
            action_type, total, failures = row
            failure_rate = failures / total
            
            insights.append(ReflectionInsight(
                insight_type=ReflectionInsightType.PATTERN_RECOGNITION,
                description=f"Action type '{action_type}' has high failure rate ({failure_rate:.1%})",
                confidence=min(0.9, total / 20),  # More samples = higher confidence
                supporting_data={
                    "action_type": action_type,
                    "total_executions": total,
                    "failures": failures,
                    "failure_rate": failure_rate
                },
                recommendation=f"Review '{action_type}' implementation or consider alternative actions",
                priority="HIGH" if failure_rate > 0.7 else "MEDIUM",
                created_at=datetime.now().isoformat()
            ))
        
        # Pattern 2: Goal complexity impact
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN LENGTH(goal) < 50 THEN 'SIMPLE'
                    WHEN LENGTH(goal) < 150 THEN 'MODERATE'
                    ELSE 'COMPLEX'
                END as complexity,
                COUNT(*) as total,
                AVG(CASE WHEN success = 1 THEN 1.0 ELSE 0.0 END) as success_rate,
                AVG(duration_ms) as avg_duration
            FROM execution_history
            WHERE executed_at >= datetime('now', '-30 days')
            GROUP BY complexity
        """)
        
        complexity_data = {row[0]: (row[1], row[2], row[3]) for row in cursor.fetchall()}
        
        if len(complexity_data) >= 2:
            insights.append(ReflectionInsight(
                insight_type=ReflectionInsightType.PATTERN_RECOGNITION,
                description="Goal complexity impacts success rate and duration",
                confidence=0.85,
                supporting_data=complexity_data,
                recommendation="Break complex goals into smaller sub-goals for better success rates",
                priority="MEDIUM",
                created_at=datetime.now().isoformat()
            ))
        
        conn.close()
        return insights
    
    def generate_learning_insights(self) -> List[ReflectionInsight]:
        """
        Generate comprehensive meta-learning insights
        
        Combines all reflection analyses into actionable insights
        """
        all_insights = []
        
        # 1. Strategy performance insights
        performances = self.analyze_strategy_performance()
        for perf in performances:
            if perf.trend == "DECLINING":
                all_insights.append(ReflectionInsight(
                    insight_type=ReflectionInsightType.STRATEGY_PERFORMANCE,
                    description=f"Strategy '{perf.strategy_name}' performance declining",
                    confidence=0.8,
                    supporting_data=asdict(perf),
                    recommendation=f"Review '{perf.strategy_name}' implementation or reduce usage",
                    priority="HIGH" if perf.success_rate < 0.5 else "MEDIUM",
                    created_at=datetime.now().isoformat()
                ))
            elif perf.trend == "IMPROVING":
                all_insights.append(ReflectionInsight(
                    insight_type=ReflectionInsightType.STRATEGY_PERFORMANCE,
                    description=f"Strategy '{perf.strategy_name}' performance improving",
                    confidence=0.9,
                    supporting_data=asdict(perf),
                    recommendation=f"Increase usage of '{perf.strategy_name}' strategy",
                    priority="LOW",
                    created_at=datetime.now().isoformat()
                ))
        
        # 2. Confidence calibration insights
        calibrations = self.calibrate_confidence()
        poorly_calibrated = [c for c in calibrations if c.calibration_error > 0.15]
        
        if poorly_calibrated:
            all_insights.append(ReflectionInsight(
                insight_type=ReflectionInsightType.CONFIDENCE_CALIBRATION,
                description=f"Confidence predictions poorly calibrated in {len(poorly_calibrated)} ranges",
                confidence=0.95,
                supporting_data={"poorly_calibrated_ranges": [asdict(c) for c in poorly_calibrated]},
                recommendation="Adjust confidence calculation algorithm to better match actual outcomes",
                priority="HIGH",
                created_at=datetime.now().isoformat()
            ))
        
        # 3. Pattern recognition insights
        pattern_insights = self.recognize_patterns()
        all_insights.extend(pattern_insights)
        
        # 4. Learning rate insight
        learning_rate = self._calculate_learning_rate()
        if learning_rate:
            all_insights.append(learning_rate)
        
        # Store insights
        self._store_insights(all_insights)
        
        return all_insights
    
    def _calculate_learning_rate(self) -> Optional[ReflectionInsight]:
        """Calculate how quickly Gu Wu is improving over time"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Compare first week vs last week success rates
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN success = 1 THEN 1.0 ELSE 0.0 END) / COUNT(*) as success_rate
            FROM (
                SELECT success FROM execution_history
                ORDER BY executed_at ASC
                LIMIT (SELECT COUNT(*) / 4 FROM execution_history)
            )
        """)
        
        early_rate = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN success = 1 THEN 1.0 ELSE 0.0 END) / COUNT(*) as success_rate
            FROM (
                SELECT success FROM execution_history
                ORDER BY executed_at DESC
                LIMIT (SELECT COUNT(*) / 4 FROM execution_history)
            )
        """)
        
        recent_rate = cursor.fetchone()[0]
        
        conn.close()
        
        if early_rate and recent_rate:
            improvement = recent_rate - early_rate
            
            if abs(improvement) > 0.05:  # Significant change
                return ReflectionInsight(
                    insight_type=ReflectionInsightType.LEARNING_RATE,
                    description=f"Overall success rate {'improved' if improvement > 0 else 'declined'} by {abs(improvement):.1%}",
                    confidence=0.9,
                    supporting_data={
                        "early_success_rate": early_rate,
                        "recent_success_rate": recent_rate,
                        "improvement": improvement
                    },
                    recommendation="Continue current learning approach" if improvement > 0 else "Review recent changes that may have impacted performance",
                    priority="HIGH" if improvement < -0.1 else "MEDIUM" if improvement < 0 else "LOW",
                    created_at=datetime.now().isoformat()
                )
        
        return None
    
    def _store_insights(self, insights: List[ReflectionInsight]):
        """Store insights in database for future reference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for insight in insights:
            cursor.execute("""
                INSERT INTO reflection_insights (
                    insight_type, description, confidence, supporting_data,
                    recommendation, priority, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                insight.insight_type.value,
                insight.description,
                insight.confidence,
                json.dumps(insight.supporting_data),
                insight.recommendation,
                insight.priority,
                insight.created_at
            ))
        
        conn.commit()
        conn.close()
    
    def get_recent_insights(self, days: int = 7) -> List[ReflectionInsight]:
        """Retrieve recent reflection insights"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT insight_type, description, confidence, supporting_data,
                   recommendation, priority, created_at
            FROM reflection_insights
            WHERE created_at >= datetime('now', '-{} days')
            ORDER BY created_at DESC
        """.format(days))
        
        insights = []
        for row in cursor.fetchall():
            insights.append(ReflectionInsight(
                insight_type=ReflectionInsightType(row[0]),
                description=row[1],
                confidence=row[2],
                supporting_data=json.loads(row[3]),
                recommendation=row[4],
                priority=row[5],
                created_at=row[6]
            ))
        
        conn.close()
        return insights


if __name__ == "__main__":
    # Example usage
    reflector = GuWuReflector()
    
    # Generate comprehensive insights
    insights = reflector.generate_learning_insights()
    
    print("=" * 80)
    print("GU WU REFLECTION INSIGHTS")
    print("=" * 80)
    print()
    
    if not insights:
        print("No insights generated yet. Need more execution history.")
    else:
        for insight in insights:
            print(f"[{insight.priority}] {insight.insight_type.value}")
            print(f"  {insight.description}")
            print(f"  Confidence: {insight.confidence:.1%}")
            print(f"  Recommendation: {insight.recommendation}")
            print()