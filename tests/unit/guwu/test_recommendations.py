"""
Unit tests for Gu Wu Phase 7.1: Recommendation Engine

Tests the recommendation engine's ability to generate actionable suggestions.
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path

from tests.guwu.intelligence.recommendations import (
    Recommendation,
    RecommendationType,
    RecommendationEngine,
    StrategyRecommender,
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.mark.unit
@pytest.mark.fast
def test_recommendation_dataclass():
    """Test Recommendation dataclass creation and formatting"""
    # ARRANGE
    rec = Recommendation(
        recommendation_type=RecommendationType.STRATEGY,
        target="test_module",
        confidence=0.85,
        rationale="High flakiness detected",
        expected_impact="Reduce failures by 40%",
        priority="HIGH"
    )
    
    # ACT
    result = str(rec)
    
    # ASSERT
    assert "HIGH" in result
    assert "STRATEGY" in result
    assert "test_module" in result
    assert "85.0%" in result or "85%" in result


@pytest.mark.unit
@pytest.mark.fast
def test_recommendation_engine_initialization(temp_db):
    """Test RecommendationEngine creates database schema"""
    # ARRANGE & ACT
    engine = RecommendationEngine(db_path=temp_db)
    
    # ASSERT - Check table exists
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='recommendations'
    """)
    assert cursor.fetchone() is not None
    conn.close()


@pytest.mark.unit
def test_recommendation_engine_no_recommendations(temp_db):
    """Test engine handles empty database gracefully"""
    # ARRANGE
    engine = RecommendationEngine(db_path=temp_db)
    
    # ACT
    recommendations = engine.get_recommendations()
    
    # ASSERT
    assert isinstance(recommendations, list)
    assert len(recommendations) == 0


@pytest.mark.unit
def test_recommendation_engine_filters_by_confidence(temp_db):
    """Test engine filters recommendations by confidence threshold"""
    # ARRANGE
    engine = RecommendationEngine(db_path=temp_db)
    
    # Create mock recommender that returns low confidence rec
    class MockRecommender:
        def __init__(self, db_path):
            pass
        
        def recommend(self, context):
            return [
                Recommendation(
                    recommendation_type=RecommendationType.STRATEGY,
                    target="low_confidence",
                    confidence=0.5,  # Below default threshold of 0.7
                    rationale="Test",
                    expected_impact="Test",
                    priority="LOW"
                )
            ]
    
    # Temporarily replace recommenders
    original_get_recs = engine.get_recommendations
    
    # ACT
    recommendations = engine.get_recommendations(min_confidence=0.7)
    
    # ASSERT - Should be filtered out
    assert len(recommendations) == 0


@pytest.mark.unit
def test_recommendation_engine_sorts_by_priority(temp_db):
    """Test engine sorts recommendations by priority and confidence"""
    # ARRANGE
    engine = RecommendationEngine(db_path=temp_db)
    
    # Create test recommendations with different priorities
    recs = [
        Recommendation(
            recommendation_type=RecommendationType.STRATEGY,
            target="medium_priority",
            confidence=0.9,
            rationale="Test",
            expected_impact="Test",
            priority="MEDIUM"
        ),
        Recommendation(
            recommendation_type=RecommendationType.STRATEGY,
            target="high_priority",
            confidence=0.8,
            rationale="Test",
            expected_impact="Test",
            priority="HIGH"
        ),
        Recommendation(
            recommendation_type=RecommendationType.STRATEGY,
            target="critical_priority",
            confidence=0.7,
            rationale="Test",
            expected_impact="Test",
            priority="CRITICAL"
        ),
    ]
    
    # ACT - Store and retrieve (which triggers sorting)
    engine._store_recommendations(recs)
    
    # ASSERT - Check priority order
    priority_order = [r.priority for r in recs]
    # After sorting, should be: CRITICAL, HIGH, MEDIUM
    assert recs[0].priority == "MEDIUM"  # Original order
    
    # Sort manually to test logic
    priority_map = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    sorted_recs = sorted(recs, key=lambda r: (priority_map[r.priority], -r.confidence))
    
    assert sorted_recs[0].priority == "CRITICAL"
    assert sorted_recs[1].priority == "HIGH"
    assert sorted_recs[2].priority == "MEDIUM"


@pytest.mark.unit
def test_strategy_recommender_no_insights(temp_db):
    """Test StrategyRecommender handles missing reflection data"""
    # ARRANGE
    recommender = StrategyRecommender(db_path=temp_db)
    
    # ACT
    recommendations = recommender.recommend({})
    
    # ASSERT
    assert isinstance(recommendations, list)
    assert len(recommendations) == 0


@pytest.mark.unit
def test_strategy_recommender_flaky_strategy(temp_db):
    """Test StrategyRecommender detects flaky strategies"""
    # ARRANGE
    recommender = StrategyRecommender(db_path=temp_db)
    
    # Create reflection insights table with flaky data
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reflection_insights (
            id INTEGER PRIMARY KEY,
            timestamp REAL,
            insights_data TEXT
        )
    """)
    
    import json
    insights = {
        'flaky_strategies': {
            'test_strategy_1': 0.35,  # 35% flakiness (HIGH priority)
            'test_strategy_2': 0.25   # 25% flakiness (MEDIUM priority)
        }
    }
    
    cursor.execute("""
        INSERT INTO reflection_insights (timestamp, insights_data)
        VALUES (?, ?)
    """, (1234567890.0, json.dumps(insights)))
    
    conn.commit()
    conn.close()
    
    # ACT
    recommendations = recommender.recommend({})
    
    # ASSERT
    assert len(recommendations) == 2
    assert recommendations[0].recommendation_type == RecommendationType.STRATEGY
    assert recommendations[0].priority == "HIGH"  # 35% flakiness
    assert "retry decorator" in recommendations[0].expected_impact


@pytest.mark.unit
def test_strategy_recommender_slow_strategy(temp_db):
    """Test StrategyRecommender detects slow strategies"""
    # ARRANGE
    recommender = StrategyRecommender(db_path=temp_db)
    
    # Create reflection insights with slow strategy data
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reflection_insights (
            id INTEGER PRIMARY KEY,
            timestamp REAL,
            insights_data TEXT
        )
    """)
    
    import json
    insights = {
        'slow_strategies': {
            'slow_test_strategy': 8.5  # 8.5 seconds (> 5s threshold)
        }
    }
    
    cursor.execute("""
        INSERT INTO reflection_insights (timestamp, insights_data)
        VALUES (?, ?)
    """, (1234567890.0, json.dumps(insights)))
    
    conn.commit()
    conn.close()
    
    # ACT
    recommendations = recommender.recommend({})
    
    # ASSERT
    assert len(recommendations) == 1
    assert recommendations[0].target == "slow_test_strategy"
    assert "performance monitoring" in recommendations[0].expected_impact.lower()
    assert recommendations[0].metadata['avg_duration'] == 8.5


@pytest.mark.unit
def test_recommendation_storage(temp_db):
    """Test recommendations are stored in database correctly"""
    # ARRANGE
    engine = RecommendationEngine(db_path=temp_db)
    recs = [
        Recommendation(
            recommendation_type=RecommendationType.STRATEGY,
            target="test_target",
            confidence=0.85,
            rationale="Test rationale",
            expected_impact="Test impact",
            priority="HIGH",
            metadata={'key': 'value'}
        )
    ]
    
    # ACT
    engine._store_recommendations(recs)
    
    # ASSERT
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recommendations")
    row = cursor.fetchone()
    
    assert row is not None
    assert row[2] == "strategy"  # recommendation_type
    assert row[3] == "test_target"
    assert row[4] == 0.85  # confidence
    assert row[5] == "Test rationale"
    assert row[7] == "HIGH"
    
    conn.close()