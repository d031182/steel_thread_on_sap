"""
Reasoning Engine for Gu Wu Agent

Implements the "Reason" part of ReAct pattern.
Analyzes current state and decides what action to take next.
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


class GoalType(Enum):
    """Types of testing goals"""
    COVERAGE = "coverage"           # Achieve X% coverage
    FLAKY_TESTS = "flaky_tests"     # Fix flaky tests
    PERFORMANCE = "performance"      # Optimize test speed
    GAP_ANALYSIS = "gap_analysis"   # Find missing tests
    REGRESSION = "regression"        # Prevent regressions
    CUSTOM = "custom"                # Custom goal


@dataclass
class ThoughtProcess:
    """
    Represents a reasoning step in ReAct loop
    
    Contains:
    - Current situation analysis
    - Decision logic
    - Chosen action with justification
    """
    timestamp: datetime
    situation: Dict[str, Any]
    reasoning: str
    decision: str
    action: str
    confidence: float  # 0.0 to 1.0
    alternatives_considered: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for logging"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'situation': self.situation,
            'reasoning': self.reasoning,
            'decision': self.decision,
            'action': self.action,
            'confidence': self.confidence,
            'alternatives': self.alternatives_considered
        }


class ReasoningEngine:
    """
    Reasoning engine for autonomous test orchestration
    
    Analyzes current state and decides next action using:
    1. Goal analysis (what are we trying to achieve?)
    2. State assessment (where are we now?)
    3. Action selection (what should we do next?)
    4. Confidence scoring (how sure are we?)
    """
    
    def __init__(self, db_path: str, verbose: bool = False):
        """
        Initialize reasoning engine
        
        Args:
            db_path: Path to Gu Wu metrics database
            verbose: Enable detailed logging
        """
        self.db_path = db_path
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        
        # Reasoning history for learning
        self.reasoning_history: List[ThoughtProcess] = []
    
    def reason(self, goal: str, context: Dict[str, Any]) -> ThoughtProcess:
        """
        Main reasoning method - analyzes situation and decides action
        
        Args:
            goal: What we're trying to achieve
            context: Current state and history
        
        Returns:
            ThoughtProcess with decision and action
        """
        # Parse goal type
        goal_type = self._parse_goal_type(goal)
        
        # Analyze current situation
        situation = self._assess_situation(goal_type, context)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(goal_type, situation, context)
        
        # Select best action
        action, alternatives = self._select_action(goal_type, situation, reasoning)
        
        # Calculate confidence
        confidence = self._calculate_confidence(situation, action, context)
        
        # Create thought process
        thought = ThoughtProcess(
            timestamp=datetime.now(),
            situation=situation,
            reasoning=reasoning,
            decision=f"Selected '{action}' based on {reasoning}",
            action=action,
            confidence=confidence,
            alternatives_considered=alternatives
        )
        
        # Store for learning
        self.reasoning_history.append(thought)
        
        if self.verbose:
            self._log_thought_process(thought)
        
        return thought
    
    def _parse_goal_type(self, goal: str) -> GoalType:
        """Parse goal string to determine type"""
        goal_lower = goal.lower()
        
        if 'coverage' in goal_lower or '%' in goal_lower:
            return GoalType.COVERAGE
        elif 'flaky' in goal_lower or 'unstable' in goal_lower:
            return GoalType.FLAKY_TESTS
        elif 'performance' in goal_lower or 'speed' in goal_lower or 'optimize' in goal_lower:
            return GoalType.PERFORMANCE
        elif 'gap' in goal_lower or 'missing' in goal_lower:
            return GoalType.GAP_ANALYSIS
        elif 'regression' in goal_lower or 'prevent' in goal_lower:
            return GoalType.REGRESSION
        else:
            return GoalType.CUSTOM
    
    def _assess_situation(self, goal_type: GoalType, context: Dict) -> Dict[str, Any]:
        """
        Assess current testing situation
        
        Returns:
            Dictionary with situation metrics
        """
        situation = {
            'goal_type': goal_type.value,
            'timestamp': datetime.now().isoformat()
        }
        
        # Coverage-specific assessment
        if goal_type == GoalType.COVERAGE:
            current_coverage = context.get('current_coverage', 0.0)
            target_coverage = self._extract_coverage_target(context.get('goal', ''))
            
            situation.update({
                'current_coverage': current_coverage,
                'target_coverage': target_coverage,
                'coverage_gap': target_coverage - current_coverage,
                'status': 'achieved' if current_coverage >= target_coverage else 'in_progress'
            })
        
        # Flaky tests assessment
        elif goal_type == GoalType.FLAKY_TESTS:
            flaky_count = context.get('flaky_tests_count', 0)
            total_tests = context.get('total_tests', 0)
            
            situation.update({
                'flaky_tests_count': flaky_count,
                'total_tests': total_tests,
                'flaky_percentage': (flaky_count / total_tests * 100) if total_tests > 0 else 0,
                'status': 'achieved' if flaky_count == 0 else 'in_progress'
            })
        
        # Performance assessment
        elif goal_type == GoalType.PERFORMANCE:
            slow_tests = context.get('slow_tests', [])
            avg_duration = context.get('avg_test_duration', 0.0)
            target_duration = self._extract_duration_target(context.get('goal', ''))
            
            situation.update({
                'slow_tests_count': len(slow_tests),
                'avg_test_duration': avg_duration,
                'target_duration': target_duration,
                'performance_gap': avg_duration - target_duration,
                'status': 'achieved' if avg_duration <= target_duration else 'in_progress'
            })
        
        # Gap analysis assessment
        elif goal_type == GoalType.GAP_ANALYSIS:
            critical_gaps = context.get('critical_gaps', 0)
            total_gaps = context.get('total_gaps', 0)
            
            situation.update({
                'critical_gaps': critical_gaps,
                'total_gaps': total_gaps,
                'status': 'achieved' if critical_gaps == 0 else 'in_progress'
            })
        
        return situation
    
    def _generate_reasoning(self, goal_type: GoalType, situation: Dict, context: Dict) -> str:
        """
        Generate reasoning explanation for decision
        
        Returns:
            Human-readable reasoning string
        """
        # Coverage reasoning
        if goal_type == GoalType.COVERAGE:
            current = situation['current_coverage']
            target = situation['target_coverage']
            gap = situation['coverage_gap']
            
            if gap <= 0:
                return f"Coverage goal achieved ({current:.1%} >= {target:.1%})"
            elif gap > 0.2:
                return f"Large coverage gap ({gap:.1%}), need gap analysis to find untested code"
            else:
                return f"Small coverage gap ({gap:.1%}), can target specific areas"
        
        # Flaky tests reasoning
        elif goal_type == GoalType.FLAKY_TESTS:
            flaky_count = situation['flaky_tests_count']
            
            if flaky_count == 0:
                return "No flaky tests detected, goal achieved"
            elif flaky_count > 5:
                return f"High flaky test count ({flaky_count}), need systematic analysis"
            else:
                return f"Found {flaky_count} flaky tests, can address individually"
        
        # Performance reasoning
        elif goal_type == GoalType.PERFORMANCE:
            slow_count = situation['slow_tests_count']
            avg = situation['avg_test_duration']
            target = situation['target_duration']
            
            if avg <= target:
                return f"Performance goal achieved (avg {avg:.2f}s <= target {target:.2f}s)"
            elif slow_count > 10:
                return f"Many slow tests ({slow_count}), need systematic optimization"
            else:
                return f"Few slow tests ({slow_count}), can optimize individually"
        
        # Gap analysis reasoning
        elif goal_type == GoalType.GAP_ANALYSIS:
            critical = situation['critical_gaps']
            total = situation['total_gaps']
            
            if critical == 0:
                return f"No critical gaps, {total} total gaps are lower priority"
            else:
                return f"Found {critical} critical gaps (complex untested code), must address"
        
        return "Analyzing situation to determine best action"
    
    def _select_action(self, goal_type: GoalType, situation: Dict, reasoning: str) -> tuple[str, List[str]]:
        """
        Select best action based on goal and situation
        
        Returns:
            (selected_action, alternative_actions)
        """
        alternatives = []
        
        # Coverage goal actions
        if goal_type == GoalType.COVERAGE:
            if situation['status'] == 'achieved':
                return ('complete', ['verify_coverage', 'generate_report'])
            
            gap = situation['coverage_gap']
            if gap > 0.2:
                alternatives = ['run_partial_analysis', 'manual_review']
                return ('analyze_gaps', alternatives)
            else:
                alternatives = ['analyze_gaps', 'manual_targeted_tests']
                return ('generate_targeted_tests', alternatives)
        
        # Flaky tests goal actions
        elif goal_type == GoalType.FLAKY_TESTS:
            if situation['status'] == 'achieved':
                return ('complete', ['verify_stability', 'generate_report'])
            
            flaky_count = situation['flaky_tests_count']
            if flaky_count > 5:
                alternatives = ['fix_individually', 'analyze_patterns']
                return ('analyze_flaky_patterns', alternatives)
            else:
                alternatives = ['analyze_patterns', 'defer_to_later']
                return ('generate_flaky_fixes', alternatives)
        
        # Performance goal actions
        elif goal_type == GoalType.PERFORMANCE:
            if situation['status'] == 'achieved':
                return ('complete', ['verify_performance', 'generate_report'])
            
            slow_count = situation['slow_tests_count']
            if slow_count > 10:
                alternatives = ['optimize_individually', 'profile_all']
                return ('analyze_performance_bottlenecks', alternatives)
            else:
                alternatives = ['analyze_bottlenecks', 'add_parallelization']
                return ('generate_optimizations', alternatives)
        
        # Gap analysis goal actions
        elif goal_type == GoalType.GAP_ANALYSIS:
            critical = situation['critical_gaps']
            if critical == 0:
                return ('complete', ['address_medium_gaps', 'generate_report'])
            else:
                alternatives = ['generate_all_tests', 'prioritize_by_complexity']
                return ('generate_critical_tests', alternatives)
        
        # Fallback
        return ('analyze_situation', ['complete', 'retry'])
    
    def _calculate_confidence(self, situation: Dict, action: str, context: Dict) -> float:
        """
        Calculate confidence in chosen action
        
        Returns:
            Confidence score 0.0 to 1.0
        """
        # Start with base confidence
        confidence = 0.7
        
        # Increase confidence if situation is clear
        if situation.get('status') == 'achieved':
            confidence += 0.2  # High confidence in completion
        
        # Increase confidence based on data quality
        history_length = len(context.get('history', []))
        if history_length > 5:
            confidence += 0.1  # More history = better decisions
        
        # Decrease confidence if uncertain
        if action == 'analyze_situation':
            confidence -= 0.2  # Fallback action = less confident
        
        # Clamp to valid range
        return max(0.0, min(1.0, confidence))
    
    def _extract_coverage_target(self, goal: str) -> float:
        """Extract coverage percentage from goal string"""
        # Look for patterns like "90%", "0.9", "90"
        import re
        
        # Pattern 1: "90%"
        match = re.search(r'(\d+)%', goal)
        if match:
            return float(match.group(1)) / 100.0
        
        # Pattern 2: "0.9"
        match = re.search(r'0\.(\d+)', goal)
        if match:
            return float('0.' + match.group(1))
        
        # Default: 70% (minimum threshold)
        return 0.7
    
    def _extract_duration_target(self, goal: str) -> float:
        """Extract duration target from goal string"""
        # Look for patterns like "5s", "5 seconds", "<5s"
        import re
        
        match = re.search(r'[<≤]?\s*(\d+\.?\d*)\s*s', goal)
        if match:
            return float(match.group(1))
        
        # Default: 5 seconds
        return 5.0
    
    def _log_thought_process(self, thought: ThoughtProcess):
        """Log thought process for transparency"""
        self.logger.info("=" * 60)
        self.logger.info("[Gu Wu Agent] REASONING")
        self.logger.info("=" * 60)
        self.logger.info(f"Situation: {thought.situation}")
        self.logger.info(f"Reasoning: {thought.reasoning}")
        self.logger.info(f"Decision: {thought.decision}")
        self.logger.info(f"Action: {thought.action}")
        self.logger.info(f"Confidence: {thought.confidence:.1%}")
        self.logger.info(f"Alternatives: {', '.join(thought.alternatives_considered)}")
        self.logger.info("=" * 60)
    
    def get_reasoning_summary(self) -> Dict:
        """Get summary of reasoning history"""
        if not self.reasoning_history:
            return {'total_thoughts': 0, 'avg_confidence': 0.0}
        
        return {
            'total_thoughts': len(self.reasoning_history),
            'avg_confidence': sum(t.confidence for t in self.reasoning_history) / len(self.reasoning_history),
            'actions_taken': [t.action for t in self.reasoning_history],
            'confidence_trend': [t.confidence for t in self.reasoning_history]
        }


if __name__ == '__main__':
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    engine = ReasoningEngine(db_path='tools/guwu/metrics.db', verbose=True)
    
    # Example 1: Coverage goal
    context = {
        'goal': 'Achieve 90% coverage on knowledge_graph module',
        'current_coverage': 0.65,
        'history': []
    }
    thought = engine.reason('Achieve 90% coverage', context)
    print(f"\nAction: {thought.action}")
    print(f"Confidence: {thought.confidence:.1%}")
    
    # Example 2: Flaky test goal
    context = {
        'goal': 'Fix all flaky tests',
        'flaky_tests_count': 3,
        'total_tests': 100,
        'history': []
    }
    thought = engine.reason('Fix all flaky tests', context)
    print(f"\nAction: {thought.action}")
    print(f"Confidence: {thought.confidence:.1%}")