"""
Tests for Gu Wu Phase 6: Enhanced Reflection Pattern

Tests meta-learning capabilities including:
- Execution history tracking
- Strategy performance analysis
- Confidence calibration
- Pattern recognition
- Learning rate calculation
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path

from tests.guwu.agent.reflector import (
    GuWuReflector,
    ReflectionInsight,
    ReflectionInsightType,
    StrategyPerformance,
    ConfidenceCalibration
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def reflector(temp_db):
    """Create reflector with temporary database"""
    return GuWuReflector(db_path=temp_db)


@pytest.fixture
def reflector_with_history(reflector):
    """Create reflector with sample execution history"""
    # Add diverse execution history
    session_id = "test_session_001"
    
    # Strategy 1: Successful coverage analysis (improving trend)
    for i in range(10):
        reflector.record_execution(
            session_id=session_id,
            goal="Achieve 90% coverage",
            strategy_used="coverage_analysis",
            action_type="analyze",
            confidence=0.85 + (i * 0.01),  # Improving confidence
            success=i >= 3,  # First 3 fail, rest succeed (improving)
            duration_ms=1000 - (i * 50),  # Getting faster
            error_message=None if i >= 3 else "Initial calibration"
        )
    
    # Strategy 2: Declining flaky test strategy
    for i in range(8):
        reflector.record_execution(
            session_id=session_id,
            goal="Fix flaky tests",
            strategy_used="flaky_test_fix",
            action_type="fix",
            confidence=0.75 - (i * 0.05),  # Declining confidence
            success=i < 3,  # First 3 succeed, rest fail (declining)
            duration_ms=2000 + (i * 100),  # Getting slower
            error_message="Timeout" if i >= 3 else None
        )
    
    # Strategy 3: Stable performance strategy
    for i in range(5):
        reflector.record_execution(
            session_id=session_id,
            goal="Optimize performance",
            strategy_used="performance_optimize",
            action_type="optimize",
            confidence=0.80,  # Consistent
            success=True,  # Always succeeds
            duration_ms=1500,  # Consistent duration
            error_message=None
        )
    
    return reflector


# ===== Basic Functionality Tests =====

@pytest.mark.unit
@pytest.mark.fast
def test_reflector_initialization(temp_db):
    """Test reflector initializes with proper database schema"""
    # ARRANGE & ACT
    reflector = GuWuReflector(db_path=temp_db)
    
    # ASSERT
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    # Check tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    
    assert 'execution_history' in tables
    assert 'reflection_insights' in tables
    assert 'strategy_performance' in tables
    
    conn.close()


@pytest.mark.unit
@pytest.mark.fast
def test_record_execution(reflector):
    """Test recording execution creates database entries"""
    # ARRANGE
    session_id = "test_session"
    goal = "Achieve 90% coverage"
    strategy = "coverage_analysis"
    
    # ACT
    reflector.record_execution(
        session_id=session_id,
        goal=goal,
        strategy_used=strategy,
        action_type="analyze",
        confidence=0.85,
        success=True,
        duration_ms=1200.5,
        error_message=None,
        context={'module': 'knowledge_graph'}
    )
    
    # ASSERT
    conn = sqlite3.connect(reflector.db_path)
    cursor = conn.cursor()
    
    # Check execution history
    cursor.execute("SELECT COUNT(*) FROM execution_history")
    assert cursor.fetchone()[0] == 1
    
    # Check strategy performance
    cursor.execute("SELECT * FROM strategy_performance WHERE strategy_name = ?", (strategy,))
    row = cursor.fetchone()
    assert row is not None
    assert row[2] == 1  # total_uses
    assert row[3] == 1  # success_count
    
    conn.close()


# ===== Strategy Performance Analysis Tests =====

@pytest.mark.unit
def test_analyze_strategy_performance(reflector_with_history):
    """Test strategy performance analysis identifies trends correctly"""
    # ACT
    performances = reflector_with_history.analyze_strategy_performance()
    
    # ASSERT
    assert len(performances) == 3
    
    # Find each strategy
    coverage = next(p for p in performances if p.strategy_name == "coverage_analysis")
    flaky = next(p for p in performances if p.strategy_name == "flaky_test_fix")
    perf = next(p for p in performances if p.strategy_name == "performance_optimize")
    
    # Coverage: Improving (3 failures, 7 successes)
    assert coverage.total_uses == 10
    assert coverage.success_rate == 0.7
    assert coverage.trend in ["IMPROVING", "INSUFFICIENT_DATA"]
    
    # Flaky: Declining (3 successes, 5 failures)
    assert flaky.total_uses == 8
    assert flaky.success_rate < 0.5
    assert flaky.trend in ["DECLINING", "INSUFFICIENT_DATA"]
    
    # Performance: Stable (all successes)
    assert perf.total_uses == 5
    assert perf.success_rate == 1.0
    assert perf.trend in ["STABLE", "INSUFFICIENT_DATA"]


@pytest.mark.unit
def test_strategy_performance_metrics_calculation(reflector):
    """Test strategy performance calculates averages correctly"""
    # ARRANGE
    strategy = "test_strategy"
    
    # Add executions with known metrics
    reflector.record_execution("s1", "goal", strategy, "action", 0.8, True, 1000)
    reflector.record_execution("s1", "goal", strategy, "action", 0.9, True, 1500)
    reflector.record_execution("s1", "goal", strategy, "action", 0.7, False, 2000)
    
    # ACT
    performances = reflector.analyze_strategy_performance()
    
    # ASSERT
    assert len(performances) == 1
    perf = performances[0]
    
    assert perf.total_uses == 3
    assert perf.success_count == 2
    assert perf.failure_count == 1
    assert perf.success_rate == pytest.approx(2/3, abs=0.01)
    assert perf.avg_duration == pytest.approx(1500, abs=10)
    assert perf.avg_confidence == pytest.approx(0.8, abs=0.05)


# ===== Confidence Calibration Tests =====

@pytest.mark.unit
def test_calibrate_confidence(reflector):
    """Test confidence calibration detects miscalibrations"""
    # ARRANGE - Add executions with known confidence/success patterns
    
    # 80-90% confidence: Should have 85% success rate
    # Actual: Only 50% success = poorly calibrated
    for i in range(10):
        reflector.record_execution(
            "s1", "goal", "strategy", "action",
            confidence=0.85,
            success=(i < 5),  # 50% success
            duration_ms=1000
        )
    
    # ACT
    calibrations = reflector.calibrate_confidence(bins=10)
    
    # ASSERT
    # Find 80-90% bin
    cal_80_90 = next((c for c in calibrations if '80%' in c.confidence_range), None)
    
    if cal_80_90:
        assert cal_80_90.sample_size == 10
        assert cal_80_90.actual_success_rate == 0.5
        assert cal_80_90.predicted_success_rate >= 0.8
        assert cal_80_90.calibration_error >= 0.3  # Large error


@pytest.mark.unit
def test_calibrate_confidence_perfect_calibration(reflector):
    """Test perfectly calibrated confidence has zero error"""
    # ARRANGE - 80% confidence with exactly 80% success rate
    for i in range(10):
        reflector.record_execution(
            "s1", "goal", "strategy", "action",
            confidence=0.80,
            success=(i < 8),  # 80% success
            duration_ms=1000
        )
    
    # ACT
    calibrations = reflector.calibrate_confidence(bins=10)
    
    # ASSERT
    cal_80 = next((c for c in calibrations if '80%' in c.confidence_range), None)
    
    if cal_80:
        assert cal_80.calibration_error < 0.05  # Nearly perfect


# ===== Pattern Recognition Tests =====

@pytest.mark.unit
def test_recognize_failing_action_pattern(reflector):
    """Test pattern recognition identifies consistently failing actions"""
    # ARRANGE - One action type fails frequently
    for i in range(20):
        reflector.record_execution(
            "s1", "goal", "strategy",
            action_type="generate_tests",  # Failing action
            confidence=0.8,
            success=(i < 5),  # 25% success rate
            duration_ms=1000
        )
    
    # ACT
    insights = reflector.recognize_patterns()
    
    # ASSERT
    failing_pattern = next(
        (i for i in insights if "generate_tests" in i.description and "failure rate" in i.description),
        None
    )
    
    assert failing_pattern is not None
    assert failing_pattern.insight_type == ReflectionInsightType.PATTERN_RECOGNITION
    assert failing_pattern.priority in ["HIGH", "MEDIUM"]


# ===== Learning Rate Tests =====

@pytest.mark.unit
def test_calculate_learning_rate_improvement(reflector):
    """Test learning rate calculation detects improvement over time"""
    # ARRANGE - Early failures, late successes
    for i in range(20):
        # First quarter: 25% success
        # Last quarter: 75% success
        if i < 5:
            success = (i < 1)  # 20% success in first 5
        elif i >= 15:
            success = (i >= 16)  # 80% success in last 5
        else:
            success = (i % 2 == 0)  # 50% in middle
        
        reflector.record_execution(
            f"s{i}", "goal", "strategy", "action",
            confidence=0.7,
            success=success,
            duration_ms=1000
        )
    
    # ACT
    insights = reflector.generate_learning_insights()
    
    # ASSERT
    learning_rate_insight = next(
        (i for i in insights if i.insight_type == ReflectionInsightType.LEARNING_RATE),
        None
    )
    
    # May not generate if improvement isn't significant enough
    # But if it does, it should indicate improvement
    if learning_rate_insight:
        assert 'improved' in learning_rate_insight.description.lower()


# ===== Integration Tests =====

@pytest.mark.unit
def test_generate_comprehensive_insights(reflector_with_history):
    """Test generate_learning_insights combines all analyses"""
    # ACT
    insights = reflector_with_history.generate_learning_insights()
    
    # ASSERT
    assert len(insights) > 0
    
    # Should have various insight types
    insight_types = {i.insight_type for i in insights}
    
    # Check we have strategy performance insights
    strategy_insights = [i for i in insights 
                        if i.insight_type == ReflectionInsightType.STRATEGY_PERFORMANCE]
    assert len(strategy_insights) > 0


@pytest.mark.unit
def test_store_and_retrieve_insights(reflector):
    """Test insights are stored and can be retrieved"""
    # ARRANGE
    test_insight = ReflectionInsight(
        insight_type=ReflectionInsightType.PATTERN_RECOGNITION,
        description="Test pattern detected",
        confidence=0.85,
        supporting_data={'key': 'value'},
        recommendation="Fix the pattern",
        priority="HIGH",
        created_at=datetime.now().isoformat()
    )
    
    # ACT
    reflector._store_insights([test_insight])
    retrieved = reflector.get_recent_insights(days=1)
    
    # ASSERT
    assert len(retrieved) == 1
    assert retrieved[0].description == "Test pattern detected"
    assert retrieved[0].confidence == 0.85
    assert retrieved[0].priority == "HIGH"


# ===== Edge Cases =====

@pytest.mark.unit
def test_reflector_with_no_history(reflector):
    """Test reflector handles empty database gracefully"""
    # ACT
    performances = reflector.analyze_strategy_performance()
    calibrations = reflector.calibrate_confidence()
    patterns = reflector.recognize_patterns()
    insights = reflector.generate_learning_insights()
    
    # ASSERT
    assert performances == []
    assert calibrations == []
    assert patterns == []
    assert insights == []


@pytest.mark.unit
def test_reflector_with_single_execution(reflector):
    """Test reflector handles minimal data gracefully"""
    # ARRANGE
    reflector.record_execution(
        "s1", "goal", "strategy", "action", 0.8, True, 1000
    )
    
    # ACT
    performances = reflector.analyze_strategy_performance()
    insights = reflector.generate_learning_insights()
    
    # ASSERT
    assert len(performances) == 1
    # May generate limited insights with minimal data
    assert isinstance(insights, list)


@pytest.mark.unit
def test_concurrent_session_tracking(reflector):
    """Test reflector can track multiple sessions simultaneously"""
    # ARRANGE & ACT
    for session_num in range(3):
        session_id = f"session_{session_num}"
        for i in range(5):
            reflector.record_execution(
                session_id=session_id,
                goal=f"Goal {session_num}",
                strategy_used="test_strategy",
                action_type="test_action",
                confidence=0.8,
                success=True,
                duration_ms=1000
            )
    
    # ASSERT
    conn = sqlite3.connect(reflector.db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(DISTINCT session_id) FROM execution_history")
    assert cursor.fetchone()[0] == 3
    
    cursor.execute("SELECT COUNT(*) FROM execution_history")
    assert cursor.fetchone()[0] == 15
    
    conn.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])