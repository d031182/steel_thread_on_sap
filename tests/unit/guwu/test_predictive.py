"""
Unit tests for Gu Wu Predictive Analytics (Phase 7.3)
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta
from tests.guwu.intelligence.predictive import (
    PredictiveEngine,
    PreflightChecker,
    Prediction
)


@pytest.fixture
def temp_db():
    """Create temporary database with test data"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Create tables
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE test_executions (
            test_name TEXT,
            outcome TEXT,
            duration REAL,
            timestamp REAL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE test_metrics (
            test_name TEXT PRIMARY KEY,
            flakiness_score REAL,
            avg_duration REAL
        )
    """)
    
    conn.commit()
    conn.close()
    
    yield path
    
    # Cleanup
    os.unlink(path)


@pytest.mark.unit
@pytest.mark.fast
def test_prediction_dataclass():
    """Test Prediction dataclass creation"""
    # ARRANGE & ACT
    pred = Prediction(
        test_name="test_example",
        prediction_type="FAILURE",
        confidence=0.85,
        reasoning="High failure rate",
        expected_duration=3.5
    )
    
    # ASSERT
    assert pred.test_name == "test_example"
    assert pred.prediction_type == "FAILURE"
    assert pred.confidence == 0.85
    assert pred.expected_duration == 3.5


@pytest.mark.unit
@pytest.mark.fast
def test_predictive_engine_init(temp_db):
    """Test PredictiveEngine initialization"""
    # ARRANGE & ACT
    engine = PredictiveEngine(db_path=temp_db)
    
    # ASSERT
    assert engine.db_path == temp_db


@pytest.mark.unit
def test_predict_failures_empty_db(temp_db):
    """Test failure prediction with empty database"""
    # ARRANGE
    engine = PredictiveEngine(db_path=temp_db)
    
    # ACT
    predictions = engine.predict_failures()
    
    # ASSERT
    assert predictions == []


@pytest.mark.unit
def test_predict_failures_with_flaky_test(temp_db):
    """Test failure prediction for flaky test"""
    # ARRANGE
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    now = datetime.now().timestamp()
    
    # Create a flaky test (alternating pass/fail)
    for i in range(10):
        outcome = 'passed' if i % 2 == 0 else 'failed'
        cursor.execute("""
            INSERT INTO test_executions (test_name, outcome, duration, timestamp)
            VALUES (?, ?, ?, ?)
        """, ('test_flaky', outcome, 2.0, now - (i * 3600)))
    
    # Add metrics
    cursor.execute("""
        INSERT INTO test_metrics (test_name, flakiness_score, avg_duration)
        VALUES ('test_flaky', 0.45, 2.0)
    """)
    
    conn.commit()
    conn.close()
    
    engine = PredictiveEngine(db_path=temp_db)
    
    # ACT
    predictions = engine.predict_failures()
    
    # ASSERT
    assert len(predictions) >= 1
    assert predictions[0].test_name == 'test_flaky'
    assert predictions[0].prediction_type == "FAILURE"
    assert predictions[0].confidence > 0.5


@pytest.mark.unit
def test_predict_failures_with_stable_test(temp_db):
    """Test failure prediction for stable test"""
    # ARRANGE
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    now = datetime.now().timestamp()
    
    # Create a stable test (all passed)
    for i in range(10):
        cursor.execute("""
            INSERT INTO test_executions (test_name, outcome, duration, timestamp)
            VALUES (?, ?, ?, ?)
        """, ('test_stable', 'passed', 2.0, now - (i * 3600)))
    
    # Add metrics
    cursor.execute("""
        INSERT INTO test_metrics (test_name, flakiness_score, avg_duration)
        VALUES ('test_stable', 0.05, 2.0)
    """)
    
    conn.commit()
    conn.close()
    
    engine = PredictiveEngine(db_path=temp_db)
    
    # ACT
    predictions = engine.predict_failures()
    
    # ASSERT
    # Stable test should not be predicted to fail
    assert not any(p.test_name == 'test_stable' for p in predictions)


@pytest.mark.unit
def test_predict_execution_time_empty_db(temp_db):
    """Test execution time prediction with empty database"""
    # ARRANGE
    engine = PredictiveEngine(db_path=temp_db)
    
    # ACT
    predictions = engine.predict_execution_time()
    
    # ASSERT
    assert predictions == {}


@pytest.mark.unit
def test_predict_execution_time_with_data(temp_db):
    """Test execution time prediction with historical data"""
    # ARRANGE
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    now = datetime.now().timestamp()
    
    # Insert execution data with consistent timing
    durations = [2.0, 2.1, 2.2, 2.0, 2.1]
    for i, duration in enumerate(durations):
        cursor.execute("""
            INSERT INTO test_executions (test_name, outcome, duration, timestamp)
            VALUES (?, ?, ?, ?)
        """, ('test_consistent', 'passed', duration, now - (i * 3600)))
    
    conn.commit()
    conn.close()
    
    engine = PredictiveEngine(db_path=temp_db)
    
    # ACT
    predictions = engine.predict_execution_time(['test_consistent'])
    
    # ASSERT
    assert 'test_consistent' in predictions
    assert 1.8 <= predictions['test_consistent'] <= 2.5  # Reasonable range


@pytest.mark.unit
def test_predict_execution_time_weighted_average(temp_db):
    """Test execution time uses weighted average (recent > old)"""
    # ARRANGE
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    now = datetime.now().timestamp()
    
    # Recent executions are faster
    for i in range(5):
        duration = 1.0 if i < 3 else 5.0  # Recent: 1.0s, Old: 5.0s
        cursor.execute("""
            INSERT INTO test_executions (test_name, outcome, duration, timestamp)
            VALUES (?, ?, ?, ?)
        """, ('test_improving', 'passed', duration, now - (i * 3600)))
    
    conn.commit()
    conn.close()
    
    engine = PredictiveEngine(db_path=temp_db)
    
    # ACT
    predictions = engine.predict_execution_time(['test_improving'])
    
    # ASSERT
    # Should be closer to recent (1.0s) than old (5.0s)
    assert predictions['test_improving'] < 3.0


@pytest.mark.unit
def test_get_preflight_report_empty_db(temp_db):
    """Test pre-flight report with empty database"""
    # ARRANGE
    engine = PredictiveEngine(db_path=temp_db)
    
    # ACT
    report = engine.get_preflight_report()
    
    # ASSERT
    assert report['likely_failures'] == []
    assert report['slow_tests'] == []
    assert report['total_tests'] == 0
    assert report['estimated_time'] == 0.0
    assert report['risk_level'] == 'UNKNOWN'


@pytest.mark.unit
def test_get_preflight_report_with_data(temp_db):
    """Test pre-flight report with realistic data"""
    # ARRANGE
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    now = datetime.now().timestamp()
    
    # Fast stable test
    for i in range(5):
        cursor.execute("""
            INSERT INTO test_executions (test_name, outcome, duration, timestamp)
            VALUES (?, ?, ?, ?)
        """, ('test_fast', 'passed', 1.0, now - (i * 3600)))
    
    # Slow test
    for i in range(5):
        cursor.execute("""
            INSERT INTO test_executions (test_name, outcome, duration, timestamp)
            VALUES (?, ?, ?, ?)
        """, ('test_slow', 'passed', 8.0, now - (i * 3600)))
    
    # Flaky test
    for i in range(10):
        outcome = 'passed' if i % 2 == 0 else 'failed'
        cursor.execute("""
            INSERT INTO test_executions (test_name, outcome, duration, timestamp)
            VALUES (?, ?, ?, ?)
        """, ('test_flaky', outcome, 2.0, now - (i * 3600)))
    
    cursor.execute("""
        INSERT INTO test_metrics (test_name, flakiness_score, avg_duration)
        VALUES ('test_flaky', 0.45, 2.0)
    """)
    
    conn.commit()
    conn.close()
    
    engine = PredictiveEngine(db_path=temp_db)
    
    # ACT
    report = engine.get_preflight_report()
    
    # ASSERT
    assert report['total_tests'] == 3
    assert report['estimated_time'] > 0
    assert len(report['slow_tests']) >= 1
    assert report['risk_level'] in ['LOW', 'MEDIUM', 'HIGH']


@pytest.mark.unit
def test_calculate_risk_level_high(temp_db):
    """Test risk level calculation for high risk"""
    # ARRANGE
    engine = PredictiveEngine(db_path=temp_db)
    predictions = [
        Prediction("test1", "FAILURE", 0.9, "reason"),
        Prediction("test2", "FAILURE", 0.85, "reason"),
        Prediction("test3", "FAILURE", 0.82, "reason"),
    ]
    
    # ACT
    risk = engine._calculate_risk_level(predictions)
    
    # ASSERT
    assert risk == "HIGH"


@pytest.mark.unit
def test_calculate_risk_level_low(temp_db):
    """Test risk level calculation for low risk"""
    # ARRANGE
    engine = PredictiveEngine(db_path=temp_db)
    predictions = []
    
    # ACT
    risk = engine._calculate_risk_level(predictions)
    
    # ASSERT
    assert risk == "LOW"


@pytest.mark.unit
@pytest.mark.fast
def test_preflight_checker_init(temp_db):
    """Test PreflightChecker initialization"""
    # ARRANGE & ACT
    checker = PreflightChecker(db_path=temp_db)
    
    # ASSERT
    assert checker.engine is not None
    assert checker.engine.db_path == temp_db


@pytest.mark.unit
def test_preflight_checker_run(temp_db):
    """Test pre-flight checker report generation"""
    # ARRANGE
    checker = PreflightChecker(db_path=temp_db)
    
    # ACT
    report = checker.run_preflight()
    
    # ASSERT
    assert "GU WU PRE-FLIGHT CHECK" in report
    assert "SUMMARY" in report
    assert "Risk Level:" in report


@pytest.mark.unit
def test_preflight_format_with_failures(temp_db):
    """Test pre-flight report formatting with failures"""
    # ARRANGE
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    now = datetime.now().timestamp()
    
    # Create flaky test
    for i in range(10):
        outcome = 'passed' if i % 3 == 0 else 'failed'
        cursor.execute("""
            INSERT INTO test_executions (test_name, outcome, duration, timestamp)
            VALUES (?, ?, ?, ?)
        """, ('test_risky', outcome, 2.0, now - (i * 3600)))
    
    cursor.execute("""
        INSERT INTO test_metrics (test_name, flakiness_score, avg_duration)
        VALUES ('test_risky', 0.55, 2.0)
    """)
    
    conn.commit()
    conn.close()
    
    checker = PreflightChecker(db_path=temp_db)
    
    # ACT
    report = checker.run_preflight()
    
    # ASSERT
    assert "[LIKELY FAILURES]" in report
    assert "Confidence:" in report


@pytest.mark.unit
def test_preflight_format_with_slow_tests(temp_db):
    """Test pre-flight report formatting with slow tests"""
    # ARRANGE
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    now = datetime.now().timestamp()
    
    # Create slow test
    for i in range(5):
        cursor.execute("""
            INSERT INTO test_executions (test_name, outcome, duration, timestamp)
            VALUES (?, ?, ?, ?)
        """, ('test_slow', 'passed', 12.0, now - (i * 3600)))
    
    conn.commit()
    conn.close()
    
    checker = PreflightChecker(db_path=temp_db)
    
    # ACT
    report = checker.run_preflight()
    
    # ASSERT
    assert "[SLOW TESTS]" in report or "Est. Time:" in report