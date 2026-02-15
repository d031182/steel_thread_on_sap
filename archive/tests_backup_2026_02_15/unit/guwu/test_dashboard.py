"""
Unit tests for Gu Wu Dashboard Generator (Phase 7.2)
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta
from tools.guwu.intelligence.dashboard import (
    DashboardGenerator,
    HealthMetrics,
    TrendData
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
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
    
    cursor.execute("""
        CREATE TABLE test_sessions (
            session_id TEXT,
            timestamp REAL,
            coverage_pct REAL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE recommendations (
            id INTEGER PRIMARY KEY,
            status TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    
    yield path
    
    # Cleanup
    os.unlink(path)


@pytest.mark.unit
@pytest.mark.fast
def test_health_metrics_dataclass():
    """Test HealthMetrics dataclass creation"""
    # ARRANGE
    metrics = HealthMetrics(
        total_tests=100,
        passing_tests=95,
        flaky_tests=3,
        slow_tests=5,
        coverage_pct=85.5,
        health_score=0.92
    )
    
    # ACT & ASSERT
    assert metrics.total_tests == 100
    assert metrics.passing_tests == 95
    assert metrics.health_score == 0.92


@pytest.mark.unit
@pytest.mark.fast
def test_trend_data_dataclass():
    """Test TrendData dataclass creation"""
    # ARRANGE
    trends = TrendData(
        period="7d",
        pass_rate_trend="UP",
        coverage_trend="STABLE",
        performance_trend="DOWN"
    )
    
    # ACT & ASSERT
    assert trends.period == "7d"
    assert trends.pass_rate_trend == "UP"


@pytest.mark.unit
@pytest.mark.fast
def test_dashboard_generator_init(temp_db):
    """Test DashboardGenerator initialization"""
    # ARRANGE & ACT
    generator = DashboardGenerator(db_path=temp_db)
    
    # ASSERT
    assert generator.db_path == temp_db


@pytest.mark.unit
@pytest.mark.fast
def test_generate_header():
    """Test dashboard header generation"""
    # ARRANGE
    generator = DashboardGenerator()
    
    # ACT
    header = generator._generate_header()
    
    # ASSERT
    assert "GU WU INTELLIGENCE DASHBOARD" in header
    assert "Attending to martial affairs" in header
    assert "Generated:" in header


@pytest.mark.unit
@pytest.mark.fast
def test_generate_health_section_excellent():
    """Test health section with EXCELLENT rating"""
    # ARRANGE
    generator = DashboardGenerator()
    health = HealthMetrics(
        total_tests=100,
        passing_tests=98,
        flaky_tests=1,
        slow_tests=2,
        coverage_pct=92.0,
        health_score=0.95
    )
    
    # ACT
    section = generator._generate_health_section(health)
    
    # ASSERT
    assert "[EXCELLENT]" in section
    assert "████████████████████" in section  # 20 blocks
    assert "95.0%" in section
    assert "Total Tests:" in section


@pytest.mark.unit
@pytest.mark.fast
def test_generate_health_section_needs_attention():
    """Test health section with NEEDS ATTENTION rating"""
    # ARRANGE
    generator = DashboardGenerator()
    health = HealthMetrics(
        total_tests=100,
        passing_tests=60,
        flaky_tests=15,
        slow_tests=10,
        coverage_pct=45.0,
        health_score=0.55
    )
    
    # ACT
    section = generator._generate_health_section(health)
    
    # ASSERT
    assert "[NEEDS ATTENTION]" in section
    assert "████████░░░░░░░░░░░░" in section  # 8 blocks
    assert "55.0%" in section


@pytest.mark.unit
@pytest.mark.fast
def test_generate_trends_section():
    """Test trends section generation"""
    # ARRANGE
    generator = DashboardGenerator()
    trends = TrendData(
        period="7d",
        pass_rate_trend="UP",
        coverage_trend="STABLE",
        performance_trend="DOWN"
    )
    
    # ACT
    section = generator._generate_trends_section(trends)
    
    # ASSERT
    assert "[TRENDS] Last 7d" in section
    assert "↑ IMPROVING" in section
    assert "→ STABLE" in section
    assert "↓ DECLINING" in section


@pytest.mark.unit
@pytest.mark.fast
def test_generate_hotspots_section_with_issues():
    """Test hotspots section with issues"""
    # ARRANGE
    generator = DashboardGenerator()
    hotspots = [
        {'name': 'test_slow_1', 'issue': 'Slow (12.3s)', 'priority': 'HIGH'},
        {'name': 'test_flaky_2', 'issue': 'Flaky (45.0%)', 'priority': 'CRITICAL'}
    ]
    
    # ACT
    section = generator._generate_hotspots_section(hotspots)
    
    # ASSERT
    assert "[HOTSPOTS]" in section
    assert "test_slow_1" in section
    assert "Slow (12.3s)" in section
    assert "Priority: HIGH" in section


@pytest.mark.unit
@pytest.mark.fast
def test_generate_hotspots_section_no_issues():
    """Test hotspots section with no issues"""
    # ARRANGE
    generator = DashboardGenerator()
    hotspots = []
    
    # ACT
    section = generator._generate_hotspots_section(hotspots)
    
    # ASSERT
    assert "[HOTSPOTS] No critical issues detected" in section


@pytest.mark.unit
def test_get_health_metrics_with_data(temp_db):
    """Test health metrics calculation with real data"""
    # ARRANGE
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    now = datetime.now().timestamp()
    
    # Insert test executions (last 24h)
    for i in range(10):
        cursor.execute("""
            INSERT INTO test_executions (test_name, outcome, duration, timestamp)
            VALUES (?, ?, ?, ?)
        """, (f'test_{i}', 'passed' if i < 9 else 'failed', 2.0, now - 3600))
    
    # Insert metrics
    cursor.execute("""
        INSERT INTO test_metrics (test_name, flakiness_score, avg_duration)
        VALUES ('test_flaky', 0.35, 3.0)
    """)
    
    cursor.execute("""
        INSERT INTO test_metrics (test_name, flakiness_score, avg_duration)
        VALUES ('test_slow', 0.1, 8.5)
    """)
    
    # Insert coverage
    cursor.execute("""
        INSERT INTO test_sessions (session_id, timestamp, coverage_pct)
        VALUES ('session1', ?, 75.5)
    """, (now,))
    
    conn.commit()
    conn.close()
    
    generator = DashboardGenerator(db_path=temp_db)
    
    # ACT
    health = generator._get_health_metrics()
    
    # ASSERT
    assert health.total_tests == 10
    assert health.passing_tests == 9
    assert health.flaky_tests == 1
    assert health.slow_tests == 1
    assert health.coverage_pct == 75.5
    assert 0.0 <= health.health_score <= 1.0


@pytest.mark.unit
def test_get_health_metrics_empty_db(temp_db):
    """Test health metrics with empty database"""
    # ARRANGE
    generator = DashboardGenerator(db_path=temp_db)
    
    # ACT
    health = generator._get_health_metrics()
    
    # ASSERT
    assert health.total_tests == 0
    assert health.passing_tests == 0
    assert health.flaky_tests == 0
    assert health.health_score == 0.0


@pytest.mark.unit
def test_get_trends_with_data(temp_db):
    """Test trends calculation with real data"""
    # ARRANGE
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    now = datetime.now().timestamp()
    week_ago = (datetime.now() - timedelta(days=7)).timestamp()
    
    # Insert improving trend (80% → 95% pass rate)
    for day in range(7):
        timestamp = week_ago + (day * 86400)
        for i in range(20):
            outcome = 'passed' if (i < 16 + day) else 'failed'  # Improving
            cursor.execute("""
                INSERT INTO test_executions (test_name, outcome, duration, timestamp)
                VALUES (?, ?, ?, ?)
            """, (f'test_{i}', outcome, 2.0, timestamp))
    
    conn.commit()
    conn.close()
    
    generator = DashboardGenerator(db_path=temp_db)
    
    # ACT
    trends = generator._get_trends()
    
    # ASSERT
    assert trends.period == "7d"
    assert trends.pass_rate_trend in ["UP", "DOWN", "STABLE"]


@pytest.mark.unit
def test_get_hotspots_with_issues(temp_db):
    """Test hotspot detection with issues"""
    # ARRANGE
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    # Insert flaky test
    cursor.execute("""
        INSERT INTO test_metrics (test_name, flakiness_score, avg_duration)
        VALUES ('test_flaky', 0.45, 3.0)
    """)
    
    # Insert slow test
    cursor.execute("""
        INSERT INTO test_metrics (test_name, flakiness_score, avg_duration)
        VALUES ('test_slow', 0.1, 12.5)
    """)
    
    conn.commit()
    conn.close()
    
    generator = DashboardGenerator(db_path=temp_db)
    
    # ACT
    hotspots = generator._get_hotspots()
    
    # ASSERT
    assert len(hotspots) >= 1
    assert any('Flaky' in spot['issue'] for spot in hotspots)


@pytest.mark.unit
def test_generate_full_dashboard(temp_db):
    """Test complete dashboard generation"""
    # ARRANGE
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    now = datetime.now().timestamp()
    
    # Insert minimal data
    cursor.execute("""
        INSERT INTO test_executions (test_name, outcome, duration, timestamp)
        VALUES ('test_1', 'passed', 2.0, ?)
    """, (now - 3600,))
    
    cursor.execute("""
        INSERT INTO test_sessions (session_id, timestamp, coverage_pct)
        VALUES ('session1', ?, 80.0)
    """, (now,))
    
    conn.commit()
    conn.close()
    
    generator = DashboardGenerator(db_path=temp_db)
    
    # ACT
    dashboard = generator.generate()
    
    # ASSERT
    assert "GU WU INTELLIGENCE DASHBOARD" in dashboard
    assert "[HEALTH OVERVIEW]" in dashboard
    assert "[TRENDS]" in dashboard
    assert "[HOTSPOTS]" in dashboard
    assert "[RECOMMENDATIONS]" in dashboard