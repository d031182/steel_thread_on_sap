"""
Shi Fu Phase 5: Growth Tracker - The Master Observes Progress
==============================================================

"The Master sees not just the present, but the journey.
 Growth is celebrated. Stagnation is addressed. The path forward is illuminated."

Phase 5 Components:
1. Historical Trend Analysis - Tracks quality improvement over time
2. Celebration System - Recognizes wins when scores improve
3. Growth Advisor - Suggests new capabilities for disciples
4. Predictive Insights - Forecasts quality trajectory
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from statistics import mean, stdev


logger = logging.getLogger(__name__)


@dataclass
class HistoricalSnapshot:
    """A point-in-time quality measurement"""
    timestamp: str
    fengshui_score: float
    guwu_score: float
    ecosystem_score: float
    pattern_count: int
    urgent_count: int


@dataclass
class TrendAnalysis:
    """Quality trend over time"""
    period_days: int
    snapshots: List[HistoricalSnapshot]
    fengshui_trend: str  # "improving", "stable", "declining"
    guwu_trend: str
    ecosystem_trend: str
    avg_improvement_rate: float  # Points per week
    volatility: float  # Standard deviation


@dataclass
class Celebration:
    """Recognition of quality improvements"""
    achievement: str
    description: str
    impact: str
    timestamp: str
    emoji: str  # For fun! 🎉


@dataclass
class GrowthSuggestion:
    """Advice for disciple evolution"""
    disciple: str  # "Feng Shui", "Gu Wu", or "Both"
    suggestion_type: str  # "new_agent", "enhanced_capability", "process_change"
    title: str
    rationale: str
    expected_benefit: str
    effort_estimate: str  # "2-3 hours", "1-2 days", etc.
    priority: int  # 1-10


@dataclass
class Prediction:
    """Forecasted quality trajectory"""
    target_date: str
    predicted_fengshui: float
    predicted_guwu: float
    predicted_ecosystem: float
    confidence: float  # 0.0-1.0
    assumptions: List[str]


class GrowthTracker:
    """
    Shi Fu's Growth Tracker - Observes progress, celebrates wins, guides evolution
    
    Tracks historical quality metrics, analyzes trends, suggests improvements,
    and forecasts future quality based on current trajectory.
    """
    
    def __init__(
        self,
        state_file: Path = Path(".shifu_state.json"),
        verbose: bool = False
    ):
        """
        Initialize Growth Tracker
        
        Args:
            state_file: Path to state file (contains historical snapshots)
            verbose: Enable detailed logging
        """
        self.state_file = state_file
        self.verbose = verbose
        
        if self.verbose:
            logger.info("[Growth Tracker] Shi Fu observes the journey...")
    
    def _load_history(self) -> List[HistoricalSnapshot]:
        """Load historical snapshots from state file"""
        if not self.state_file.exists():
            return []
        
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            
            history = []
            for snapshot_data in state.get('history', []):
                history.append(HistoricalSnapshot(
                    timestamp=snapshot_data['timestamp'],
                    fengshui_score=snapshot_data['fengshui_score'],
                    guwu_score=snapshot_data['guwu_score'],
                    ecosystem_score=snapshot_data['ecosystem_score'],
                    pattern_count=snapshot_data.get('pattern_count', 0),
                    urgent_count=snapshot_data.get('urgent_count', 0)
                ))
            
            return history
        except Exception as e:
            logger.error(f"[Growth Tracker] Error loading history: {e}")
            return []
    
    def _save_snapshot(
        self,
        fengshui_score: float,
        guwu_score: float,
        ecosystem_score: float,
        pattern_count: int = 0,
        urgent_count: int = 0
    ):
        """Save a new snapshot to state file"""
        snapshot = HistoricalSnapshot(
            timestamp=datetime.now().isoformat(),
            fengshui_score=fengshui_score,
            guwu_score=guwu_score,
            ecosystem_score=ecosystem_score,
            pattern_count=pattern_count,
            urgent_count=urgent_count
        )
        
        # Load existing state
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                state = json.load(f)
        else:
            state = {'history': []}
        
        # Add new snapshot
        state['history'].append({
            'timestamp': snapshot.timestamp,
            'fengshui_score': snapshot.fengshui_score,
            'guwu_score': snapshot.guwu_score,
            'ecosystem_score': snapshot.ecosystem_score,
            'pattern_count': snapshot.pattern_count,
            'urgent_count': snapshot.urgent_count
        })
        
        # Keep last 90 days only (prevent infinite growth)
        cutoff = (datetime.now() - timedelta(days=90)).isoformat()
        state['history'] = [
            s for s in state['history']
            if s['timestamp'] >= cutoff
        ]
        
        # Save
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def analyze_trends(self, period_days: int = 30) -> Optional[TrendAnalysis]:
        """
        Analyze quality trends over specified period
        
        Args:
            period_days: Number of days to analyze (default 30)
        
        Returns:
            TrendAnalysis or None if insufficient data
        """
        history = self._load_history()
        
        if len(history) < 2:
            if self.verbose:
                logger.info("[Growth Tracker] Insufficient data for trend analysis")
            return None
        
        # Filter to period
        cutoff = (datetime.now() - timedelta(days=period_days)).isoformat()
        period_snapshots = [s for s in history if s.timestamp >= cutoff]
        
        if len(period_snapshots) < 2:
            if self.verbose:
                logger.info(f"[Growth Tracker] Only {len(period_snapshots)} snapshots in period")
            return None
        
        # Calculate trends
        fengshui_trend = self._calculate_trend([s.fengshui_score for s in period_snapshots])
        guwu_trend = self._calculate_trend([s.guwu_score for s in period_snapshots])
        ecosystem_trend = self._calculate_trend([s.ecosystem_score for s in period_snapshots])
        
        # Calculate improvement rate (points per week)
        days_elapsed = (
            datetime.fromisoformat(period_snapshots[-1].timestamp) -
            datetime.fromisoformat(period_snapshots[0].timestamp)
        ).days
        
        if days_elapsed > 0:
            weeks = days_elapsed / 7.0
            ecosystem_change = period_snapshots[-1].ecosystem_score - period_snapshots[0].ecosystem_score
            avg_improvement_rate = ecosystem_change / weeks
        else:
            avg_improvement_rate = 0.0
        
        # Calculate volatility
        ecosystem_scores = [s.ecosystem_score for s in period_snapshots]
        volatility = stdev(ecosystem_scores) if len(ecosystem_scores) > 1 else 0.0
        
        return TrendAnalysis(
            period_days=period_days,
            snapshots=period_snapshots,
            fengshui_trend=fengshui_trend,
            guwu_trend=guwu_trend,
            ecosystem_trend=ecosystem_trend,
            avg_improvement_rate=avg_improvement_rate,
            volatility=volatility
        )
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear regression slope
        n = len(values)
        x = list(range(n))
        x_mean = mean(x)
        y_mean = mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        # Classify
        if slope > 0.5:
            return "improving"
        elif slope < -0.5:
            return "declining"
        else:
            return "stable"
    
    def identify_celebrations(
        self,
        trend: TrendAnalysis
    ) -> List[Celebration]:
        """
        Identify achievements worth celebrating
        
        Args:
            trend: Trend analysis with historical data
        
        Returns:
            List of celebrations
        """
        celebrations = []
        
        if len(trend.snapshots) < 2:
            return celebrations
        
        # Get first and last snapshot
        first = trend.snapshots[0]
        last = trend.snapshots[-1]
        
        # Celebration 1: Ecosystem Score Improvement
        ecosystem_improvement = last.ecosystem_score - first.ecosystem_score
        if ecosystem_improvement >= 5.0:
            celebrations.append(Celebration(
                achievement="Major Ecosystem Improvement",
                description=f"Ecosystem score improved by {ecosystem_improvement:.1f} points!",
                impact=f"From {first.ecosystem_score:.1f} to {last.ecosystem_score:.1f}",
                timestamp=datetime.now().isoformat(),
                emoji="🎉"
            ))
        elif ecosystem_improvement >= 2.0:
            celebrations.append(Celebration(
                achievement="Ecosystem Improvement",
                description=f"Ecosystem score improved by {ecosystem_improvement:.1f} points",
                impact=f"From {first.ecosystem_score:.1f} to {last.ecosystem_score:.1f}",
                timestamp=datetime.now().isoformat(),
                emoji="✨"
            ))
        
        # Celebration 2: Pattern Reduction
        pattern_reduction = first.pattern_count - last.pattern_count
        if pattern_reduction >= 5:
            celebrations.append(Celebration(
                achievement="Significant Pattern Reduction",
                description=f"Reduced quality patterns by {pattern_reduction}!",
                impact=f"From {first.pattern_count} to {last.pattern_count} patterns",
                timestamp=datetime.now().isoformat(),
                emoji="🏆"
            ))
        
        # Celebration 3: Urgent Pattern Elimination
        if first.urgent_count > 0 and last.urgent_count == 0:
            celebrations.append(Celebration(
                achievement="All Urgent Issues Resolved",
                description=f"Eliminated all {first.urgent_count} URGENT patterns!",
                impact="Zero critical quality issues",
                timestamp=datetime.now().isoformat(),
                emoji="🎯"
            ))
        
        # Celebration 4: Consistent Improvement
        if trend.ecosystem_trend == "improving" and trend.avg_improvement_rate > 1.0:
            celebrations.append(Celebration(
                achievement="Sustained Quality Growth",
                description=f"Improving at {trend.avg_improvement_rate:.1f} points/week",
                impact="Consistent upward trajectory",
                timestamp=datetime.now().isoformat(),
                emoji="📈"
            ))
        
        # Celebration 5: Low Volatility (Stability)
        if trend.volatility < 3.0 and len(trend.snapshots) >= 4:
            celebrations.append(Celebration(
                achievement="Quality Stability Achieved",
                description=f"Low volatility ({trend.volatility:.1f}) indicates stable quality",
                impact="Predictable, consistent quality",
                timestamp=datetime.now().isoformat(),
                emoji="🎵"
            ))
        
        return celebrations
    
    def suggest_growth_opportunities(
        self,
        trend: TrendAnalysis,
        current_patterns: List[Dict]
    ) -> List[GrowthSuggestion]:
        """
        Suggest growth opportunities for disciples
        
        Args:
            trend: Historical trend analysis
            current_patterns: Currently detected patterns
        
        Returns:
            List of growth suggestions
        """
        suggestions = []
        
        # Analyze recurring pattern types
        pattern_types = {}
        for pattern in current_patterns:
            ptype = pattern.get('pattern_name', 'unknown')
            pattern_types[ptype] = pattern_types.get(ptype, 0) + 1
        
        # Suggestion 1: Feng Shui needs new agent?
        if pattern_types.get('SECURITY_ISSUES_CAUSE_TEST_GAPS', 0) >= 3:
            suggestions.append(GrowthSuggestion(
                disciple="Feng Shui",
                suggestion_type="new_agent",
                title="Add SecurityArchitectAgent",
                rationale="Security patterns recurring frequently (3+ instances)",
                expected_benefit="Reduce security violations by 70%, improve test coverage gaps",
                effort_estimate="4-6 hours",
                priority=9
            ))
        
        if pattern_types.get('PERFORMANCE_ISSUES_SLOW_TESTS', 0) >= 3:
            suggestions.append(GrowthSuggestion(
                disciple="Feng Shui",
                suggestion_type="new_agent",
                title="Enhance PerformanceAgent",
                rationale="Performance issues causing slow tests (3+ instances)",
                expected_benefit="Reduce N+1 queries, improve test execution speed by 40%",
                effort_estimate="3-4 hours",
                priority=7
            ))
        
        # Suggestion 2: Gu Wu needs enhancement?
        if trend.guwu_trend == "declining":
            suggestions.append(GrowthSuggestion(
                disciple="Gu Wu",
                suggestion_type="enhanced_capability",
                title="Enhance Flaky Test Detection",
                rationale="Gu Wu score declining - may indicate test quality degradation",
                expected_benefit="Improved flaky test detection, faster test suite",
                effort_estimate="2-3 hours",
                priority=8
            ))
        
        # Suggestion 3: Both disciples need coordination?
        if len(current_patterns) > 5:
            suggestions.append(GrowthSuggestion(
                disciple="Both",
                suggestion_type="process_change",
                title="Implement Pre-Commit Quality Gate",
                rationale="High pattern count suggests issues entering codebase frequently",
                expected_benefit="Prevent 60% of quality issues before commit",
                effort_estimate="3-4 hours",
                priority=10
            ))
        
        # Suggestion 4: Growth based on improvement rate
        if trend.avg_improvement_rate < 0.5 and len(trend.snapshots) >= 4:
            suggestions.append(GrowthSuggestion(
                disciple="Both",
                suggestion_type="process_change",
                title="Increase Analysis Frequency",
                rationale="Slow improvement rate - more frequent feedback may help",
                expected_benefit="Faster quality improvement cycle",
                effort_estimate="1 hour (config change)",
                priority=6
            ))
        
        # Sort by priority
        suggestions.sort(key=lambda s: s.priority, reverse=True)
        
        return suggestions
    
    def predict_trajectory(
        self,
        trend: TrendAnalysis,
        weeks_ahead: int = 4
    ) -> Optional[Prediction]:
        """
        Predict future quality based on current trajectory
        
        Args:
            trend: Historical trend analysis
            weeks_ahead: How many weeks to forecast
        
        Returns:
            Prediction or None if insufficient data
        """
        if len(trend.snapshots) < 3:
            return None
        
        # Simple linear extrapolation
        target_date = (datetime.now() + timedelta(weeks=weeks_ahead)).isoformat()
        
        # Calculate current velocity (points per week)
        fengshui_velocity = self._calculate_velocity(
            [s.fengshui_score for s in trend.snapshots],
            trend.period_days
        )
        guwu_velocity = self._calculate_velocity(
            [s.guwu_score for s in trend.snapshots],
            trend.period_days
        )
        ecosystem_velocity = self._calculate_velocity(
            [s.ecosystem_score for s in trend.snapshots],
            trend.period_days
        )
        
        # Project forward
        current = trend.snapshots[-1]
        predicted_fengshui = min(100, max(0, current.fengshui_score + (fengshui_velocity * weeks_ahead)))
        predicted_guwu = min(100, max(0, current.guwu_score + (guwu_velocity * weeks_ahead)))
        predicted_ecosystem = min(100, max(0, current.ecosystem_score + (ecosystem_velocity * weeks_ahead)))
        
        # Calculate confidence (lower volatility = higher confidence)
        confidence = max(0.3, min(1.0, 1.0 - (trend.volatility / 20.0)))
        
        # Generate assumptions
        assumptions = [
            "Current improvement rate continues",
            "No major architectural changes",
            "Team capacity remains stable",
            f"Based on {len(trend.snapshots)} historical snapshots"
        ]
        
        if trend.volatility > 5.0:
            assumptions.append("⚠️ High volatility - prediction less reliable")
        
        return Prediction(
            target_date=target_date,
            predicted_fengshui=predicted_fengshui,
            predicted_guwu=predicted_guwu,
            predicted_ecosystem=predicted_ecosystem,
            confidence=confidence,
            assumptions=assumptions
        )
    
    def _calculate_velocity(self, values: List[float], period_days: int) -> float:
        """Calculate velocity (change per week)"""
        if len(values) < 2 or period_days == 0:
            return 0.0
        
        change = values[-1] - values[0]
        weeks = period_days / 7.0
        
        return change / weeks if weeks > 0 else 0.0
    
    def record_snapshot(
        self,
        fengshui_score: float,
        guwu_score: float,
        ecosystem_score: float,
        pattern_count: int = 0,
        urgent_count: int = 0
    ):
        """
        Record a new quality snapshot
        
        Args:
            fengshui_score: Current Feng Shui score
            guwu_score: Current Gu Wu score
            ecosystem_score: Current ecosystem score
            pattern_count: Number of patterns detected
            urgent_count: Number of URGENT patterns
        """
        self._save_snapshot(
            fengshui_score,
            guwu_score,
            ecosystem_score,
            pattern_count,
            urgent_count
        )
        
        if self.verbose:
            logger.info(f"[Growth Tracker] Snapshot recorded: ecosystem={ecosystem_score:.1f}")


def main():
    """CLI entry point for Growth Tracker"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Shi Fu Growth Tracker - Observe progress, celebrate wins"
    )
    parser.add_argument(
        '--analyze-trends',
        action='store_true',
        help='Analyze quality trends over time'
    )
    parser.add_argument(
        '--period',
        type=int,
        default=30,
        help='Analysis period in days (default: 30)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable detailed logging'
    )
    
    args = parser.parse_args()
    
    tracker = GrowthTracker(verbose=args.verbose)
    
    if args.analyze_trends:
        trend = tracker.analyze_trends(period_days=args.period)
        
        if not trend:
            print("Insufficient data for trend analysis.")
            print("Run weekly analyses to build historical data.")
            return
        
        print("\n" + "="*70)
        print("Shi Fu's Growth Analysis")
        print("="*70)
        
        print(f"\nPeriod: {trend.period_days} days ({len(trend.snapshots)} snapshots)")
        print(f"\nTrends:")
        print(f"  Feng Shui: {trend.fengshui_trend.upper()}")
        print(f"  Gu Wu: {trend.guwu_trend.upper()}")
        print(f"  Ecosystem: {trend.ecosystem_trend.upper()}")
        
        print(f"\nImprovement Rate: {trend.avg_improvement_rate:+.2f} points/week")
        print(f"Volatility: {trend.volatility:.2f} (lower is more stable)")
        
        # Celebrations
        celebrations = tracker.identify_celebrations(trend)
        if celebrations:
            print("\n" + "="*70)
            print("Celebrations! 🎉")
            print("="*70)
            for cel in celebrations:
                print(f"\n{cel.emoji} {cel.achievement}")
                print(f"   {cel.description}")
                print(f"   Impact: {cel.impact}")
        
        # Growth suggestions
        suggestions = tracker.suggest_growth_opportunities(trend, [])
        if suggestions:
            print("\n" + "="*70)
            print("Growth Opportunities")
            print("="*70)
            for sug in suggestions[:3]:  # Top 3
                print(f"\n{sug.title} (Priority: {sug.priority}/10)")
                print(f"   Disciple: {sug.disciple}")
                print(f"   Rationale: {sug.rationale}")
                print(f"   Benefit: {sug.expected_benefit}")
                print(f"   Effort: {sug.effort_estimate}")
        
        # Prediction
        prediction = tracker.predict_trajectory(trend, weeks_ahead=4)
        if prediction:
            print("\n" + "="*70)
            print("4-Week Forecast")
            print("="*70)
            print(f"\nPredicted Scores (Confidence: {prediction.confidence:.0%}):")
            print(f"  Feng Shui: {prediction.predicted_fengshui:.1f}")
            print(f"  Gu Wu: {prediction.predicted_guwu:.1f}")
            print(f"  Ecosystem: {prediction.predicted_ecosystem:.1f}")
            print(f"\nAssumptions:")
            for assumption in prediction.assumptions:
                print(f"  • {assumption}")


if __name__ == '__main__':
    main()