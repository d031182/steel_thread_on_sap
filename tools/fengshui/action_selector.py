"""
Action Selector for Feng Shui ReAct Agent

Selects optimal action based on state and historical performance.
Uses weighted scoring to choose best action from available options.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class ActionType(Enum):
    """Types of actions the agent can take"""
    FIX_DI_VIOLATION = "fix_di_violation"
    FIX_BLUEPRINT = "fix_blueprint"
    FIX_STRUCTURE = "fix_structure"
    FIX_COUPLING = "fix_coupling"
    SWITCH_STRATEGY = "switch_strategy"
    ROLLBACK = "rollback"


@dataclass
class Action:
    """An action the agent can take"""
    type: ActionType
    target_module: str
    strategy: str
    estimated_success_rate: float  # 0.0-1.0
    estimated_time_ms: int
    risk_level: str  # LOW/MEDIUM/HIGH
    description: str
    priority_score: float = 0.0  # Calculated by selector


class ActionSelector:
    """Select best action based on state and history"""
    
    # Scoring weights (sum to 1.0)
    WEIGHTS = {
        'expected_improvement': 0.40,  # How much will this improve score?
        'success_rate': 0.30,          # How likely is this to succeed?
        'execution_time': 0.20,        # How fast can we do this?
        'risk_level': 0.10             # How risky is this action?
    }
    
    # Risk level penalties
    RISK_PENALTIES = {
        'LOW': 1.0,      # No penalty
        'MEDIUM': 0.8,   # 20% penalty
        'HIGH': 0.5      # 50% penalty
    }
    
    def __init__(self, reflector=None):
        """
        Initialize action selector
        
        Args:
            reflector: FengShuiReflector for historical performance data
        """
        self.reflector = reflector
        
    def select_action(
        self,
        state: 'ArchitectureState',
        available_actions: List[Action],
        strategy_performance: Dict[str, float]
    ) -> Action:
        """
        Choose optimal action using weighted scoring
        
        Selection criteria (weighted):
        1. Expected improvement: 40%
        2. Success rate: 30%
        3. Execution time: 20%
        4. Risk level: 10%
        
        Args:
            state: Current architecture state
            available_actions: List of possible actions
            strategy_performance: Historical success rates by strategy
            
        Returns:
            Highest-scoring action
        """
        if not available_actions:
            raise ValueError("No available actions to select from")
        
        # Score all actions
        for action in available_actions:
            action.priority_score = self.score_action(action, state, strategy_performance)
        
        # Return highest scoring action
        best_action = max(available_actions, key=lambda a: a.priority_score)
        return best_action
    
    def score_action(
        self,
        action: Action,
        state: 'ArchitectureState',
        strategy_performance: Dict[str, float]
    ) -> float:
        """
        Score an action (0.0-1.0) based on weighted criteria
        
        Args:
            action: Action to score
            state: Current architecture state
            strategy_performance: Historical success rates
            
        Returns:
            Composite score (0.0-1.0)
        """
        # 1. Expected improvement (40%)
        improvement_score = self.estimate_improvement(action, state)
        improvement_contribution = improvement_score * self.WEIGHTS['expected_improvement']
        
        # 2. Success rate (30%)
        success_rate = strategy_performance.get(action.strategy, 0.5)  # Default 50%
        success_contribution = success_rate * self.WEIGHTS['success_rate']
        
        # 3. Execution time (20%) - normalize and invert (faster = better)
        # Assume max time is 60000ms (1 minute)
        time_score = 1.0 - min(1.0, action.estimated_time_ms / 60000.0)
        time_contribution = time_score * self.WEIGHTS['execution_time']
        
        # 4. Risk level (10%) - penalize risky actions
        risk_penalty = self.RISK_PENALTIES.get(action.risk_level, 0.5)
        risk_contribution = risk_penalty * self.WEIGHTS['risk_level']
        
        # Combine all scores
        total_score = (
            improvement_contribution +
            success_contribution +
            time_contribution +
            risk_contribution
        )
        
        return min(1.0, max(0.0, total_score))  # Clamp to [0.0, 1.0]
    
    def generate_available_actions(self, state: 'ArchitectureState') -> List[Action]:
        """
        Generate list of possible actions given current state
        
        Prioritizes critical violations first, then high, then medium.
        
        Args:
            state: Current architecture state
            
        Returns:
            List of available actions
        """
        actions = []
        
        # Get critical violations first
        critical_violations = state.get_critical_violations()
        
        for violation in critical_violations:
            action = self._create_action_for_violation(violation, state)
            if action:
                actions.append(action)
        
        # If no critical violations, look at high severity
        if not actions:
            high_violations = state.violations_by_severity.get('HIGH', [])
            for violation in high_violations[:3]:  # Limit to top 3
                action = self._create_action_for_violation(violation, state)
                if action:
                    actions.append(action)
        
        # Always include strategy switch as fallback option
        actions.append(Action(
            type=ActionType.SWITCH_STRATEGY,
            target_module='all',
            strategy='switch',
            estimated_success_rate=0.7,
            estimated_time_ms=100,
            risk_level='LOW',
            description='Switch to alternative strategy'
        ))
        
        return actions
    
    def estimate_improvement(self, action: Action, state: 'ArchitectureState') -> float:
        """
        Estimate how much this action will improve Feng Shui score
        
        Uses violation severity to estimate improvement:
        - CRITICAL fix: +20 points
        - HIGH fix: +10 points
        - MEDIUM fix: +5 points
        - LOW fix: +2 points
        
        Args:
            action: Action to estimate
            state: Current architecture state
            
        Returns:
            Estimated improvement (0.0-1.0 normalized)
        """
        if action.type == ActionType.SWITCH_STRATEGY:
            return 0.3  # Moderate improvement expected from strategy switch
        
        # Find violations related to this action
        target_violations = state.get_violations_for_module(action.target_module)
        
        if not target_violations:
            return 0.1  # Minimal improvement if no violations found
        
        # Calculate potential improvement based on severity
        improvement_points = 0.0
        for v in target_violations:
            if action.type.value in v.category or action.type.value in v.type:
                if v.severity == 'CRITICAL':
                    improvement_points += 20.0
                elif v.severity == 'HIGH':
                    improvement_points += 10.0
                elif v.severity == 'MEDIUM':
                    improvement_points += 5.0
                elif v.severity == 'LOW':
                    improvement_points += 2.0
        
        # Normalize to 0.0-1.0 (assume max improvement is 40 points)
        return min(1.0, improvement_points / 40.0)
    
    def _create_action_for_violation(
        self,
        violation: 'ViolationInfo',
        state: 'ArchitectureState'
    ) -> Optional[Action]:
        """
        Create action to fix a specific violation
        
        Args:
            violation: Violation to fix
            state: Current architecture state
            
        Returns:
            Action to fix violation, or None if no fix available
        """
        # Map violation category to action type
        action_type_map = {
            'di_compliance': ActionType.FIX_DI_VIOLATION,
            'blueprint': ActionType.FIX_BLUEPRINT,
            'structure': ActionType.FIX_STRUCTURE,
            'coupling': ActionType.FIX_COUPLING
        }
        
        action_type = action_type_map.get(violation.category)
        if not action_type:
            return None
        
        # Extract module name from file path
        module_name = violation.file_path.split('/')[0] if '/' in violation.file_path else 'unknown'
        
        # Estimate success rate based on violation type (historical data if available)
        estimated_success = 0.7  # Default 70%
        if self.reflector:
            # TODO: Query reflector for historical success rate of this fix type
            pass
        
        # Estimate execution time based on action type
        time_estimates = {
            ActionType.FIX_DI_VIOLATION: 5000,   # 5 seconds
            ActionType.FIX_BLUEPRINT: 2000,      # 2 seconds
            ActionType.FIX_STRUCTURE: 3000,      # 3 seconds
            ActionType.FIX_COUPLING: 4000        # 4 seconds
        }
        estimated_time = time_estimates.get(action_type, 3000)
        
        # Map severity to risk level
        risk_map = {
            'CRITICAL': 'HIGH',   # Critical fixes are risky
            'HIGH': 'MEDIUM',
            'MEDIUM': 'LOW',
            'LOW': 'LOW'
        }
        risk_level = risk_map.get(violation.severity, 'MEDIUM')
        
        return Action(
            type=action_type,
            target_module=module_name,
            strategy='current',  # Will be set by agent
            estimated_success_rate=estimated_success,
            estimated_time_ms=estimated_time,
            risk_level=risk_level,
            description=f"Fix {violation.category} in {module_name}: {violation.description[:50]}"
        )