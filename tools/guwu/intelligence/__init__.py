"""
Gu Wu Phase 7: Intelligent Recommendations & Visualization

This module provides intelligent recommendations, predictive analytics,
and adaptive strategies for test execution.

Components:
- recommendations: Core recommendation engine and recommenders
- dashboard: Visual intelligence dashboard (ASCII + future web)
- predictions: Failure and performance predictors
- adapters: Context-aware strategy selection

Philosophy: "Intelligence without action is meaningless; action without intelligence is dangerous"
"""

from .recommendations import (
    Recommendation,
    RecommendationType,
    RecommendationEngine,
    StrategyRecommender,
)

__all__ = [
    'Recommendation',
    'RecommendationType',
    'RecommendationEngine',
    'StrategyRecommender',
]