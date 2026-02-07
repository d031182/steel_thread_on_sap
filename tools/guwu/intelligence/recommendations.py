"""
Gu Wu Phase 7.1: Recommendation Engine Core

Provides intelligent recommendations for test improvement based on reflection insights.
"""

import sqlite3
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class RecommendationType(Enum):
    """Types of recommendations the engine can generate"""
    STRATEGY = "strategy"           # Which testing strategy to use
    COVERAGE = "coverage"           # Where to add tests
    REFACTORING = "refactoring"     # Code that needs improvement


@dataclass
class Recommendation:
    """A single recommendation with context and confidence"""
    recommendation_type: RecommendationType
    target: str                     # What to improve (module, function, etc.)
    confidence: float               # 0.0-1.0 confidence score
    rationale: str                  # WHY this recommendation
    expected_impact: str            # What will improve
    priority: str                   # CRITICAL, HIGH, MEDIUM, LOW
    metadata: Optional[Dict] = None # Additional context
    
    def __str__(self) -> str:
        """Format recommendation for display"""
        return (
            f"[{self.priority}] {self.recommendation_type.value.upper()} "
            f"recommendation for {self.target}\n"
            f"  Confidence: {self.confidence:.1%}\n"
            f"  Rationale: {self.rationale}\n"
            f"  Impact: {self.expected_impact}"
        )


class RecommendationEngine:
    """
    Core recommendation engine that generates actionable suggestions.
    
    Uses reflection insights to identify improvement opportunities.
    """
    
    def __init__(self, db_path: str = "tools/guwu/guwu_metrics.db"):
        self.db_path = db_path
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Create recommendations table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                recommendation_type TEXT NOT NULL,
                target TEXT NOT NULL,
                confidence REAL NOT NULL,
                rationale TEXT NOT NULL,
                expected_impact TEXT,
                priority TEXT DEFAULT 'MEDIUM',
                status TEXT DEFAULT 'pending',
                metadata TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_recommendations(
        self, 
        context: Optional[Dict] = None,
        min_confidence: float = 0.7
    ) -> List[Recommendation]:
        """
        Generate recommendations based on current context.
        
        Args:
            context: Optional context (module name, recent changes, etc.)
            min_confidence: Minimum confidence threshold (0.0-1.0)
        
        Returns:
            List of recommendations sorted by priority and confidence
        """
        recommendations = []
        
        # Get all available recommenders
        recommenders = [
            StrategyRecommender(self.db_path),
            # Future: CoverageAdvisor, RefactoringSuggester
        ]
        
        # Generate recommendations from each recommender
        for recommender in recommenders:
            recs = recommender.recommend(context or {})
            recommendations.extend(recs)
        
        # Filter by confidence
        recommendations = [r for r in recommendations if r.confidence >= min_confidence]
        
        # Sort by priority (CRITICAL > HIGH > MEDIUM > LOW) and confidence
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        recommendations.sort(
            key=lambda r: (priority_order.get(r.priority, 999), -r.confidence)
        )
        
        # Store in database
        self._store_recommendations(recommendations)
        
        return recommendations
    
    def _store_recommendations(self, recommendations: List[Recommendation]):
        """Store recommendations in database for tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for rec in recommendations:
            cursor.execute("""
                INSERT INTO recommendations 
                (timestamp, recommendation_type, target, confidence, rationale, 
                 expected_impact, priority, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                time.time(),
                rec.recommendation_type.value,
                rec.target,
                rec.confidence,
                rec.rationale,
                rec.expected_impact,
                rec.priority,
                str(rec.metadata) if rec.metadata else None
            ))
        
        conn.commit()
        conn.close()


class StrategyRecommender:
    """
    Recommends optimal testing strategies based on historical patterns.
    
    Analyzes reflection insights to determine which strategies work best.
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def recommend(self, context: Dict) -> List[Recommendation]:
        """Generate strategy recommendations"""
        recommendations = []
        
        # Get reflection insights
        insights = self._get_reflection_insights()
        
        if not insights:
            return recommendations
        
        # Analyze flakiness patterns
        if insights.get('flaky_strategies'):
            for strategy, score in insights['flaky_strategies'].items():
                if score > 0.2:  # More than 20% flakiness
                    recommendations.append(Recommendation(
                        recommendation_type=RecommendationType.STRATEGY,
                        target=strategy,
                        confidence=min(score, 0.95),
                        rationale=f"Strategy has {score:.1%} flakiness rate (threshold: 20%)",
                        expected_impact=f"Enable retry decorator to reduce failures by ~40%",
                        priority="HIGH" if score > 0.3 else "MEDIUM",
                        metadata={'flakiness_score': score}
                    ))
        
        # Analyze performance trends
        if insights.get('slow_strategies'):
            for strategy, avg_duration in insights['slow_strategies'].items():
                if avg_duration > 5.0:  # Slower than 5 seconds
                    recommendations.append(Recommendation(
                        recommendation_type=RecommendationType.STRATEGY,
                        target=strategy,
                        confidence=0.85,
                        rationale=f"Strategy averages {avg_duration:.1f}s (threshold: 5s)",
                        expected_impact="Add performance monitoring to identify bottlenecks",
                        priority="MEDIUM",
                        metadata={'avg_duration': avg_duration}
                    ))
        
        return recommendations
    
    def _get_reflection_insights(self) -> Dict:
        """Query reflection database for insights"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if reflection tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='reflection_insights'
            """)
            
            if not cursor.fetchone():
                conn.close()
                return {}
            
            # Get latest insights
            cursor.execute("""
                SELECT insights_data FROM reflection_insights
                ORDER BY timestamp DESC LIMIT 1
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                import json
                return json.loads(row[0])
            
            return {}
            
        except Exception:
            return {}


def main():
    """CLI entry point for recommendation engine"""
    import sys
    import io
    
    # Windows encoding fix
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    engine = RecommendationEngine()
    recommendations = engine.get_recommendations()
    
    if not recommendations:
        print("[OK] No recommendations at this time. Keep up the good work!")
        return
    
    print("[RECOMMENDATIONS] GU WU RECOMMENDATIONS")
    print("=" * 60)
    print(f"Generated {len(recommendations)} recommendation(s)\n")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}\n")
    
    print("=" * 60)
    print("[TIP] Address HIGH priority items first for maximum impact")


if __name__ == "__main__":
    main()