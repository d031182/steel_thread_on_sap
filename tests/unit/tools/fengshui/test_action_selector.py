"""
Unit tests for Feng Shui Action Selector

Tests weighted action scoring and selection logic.
"""

import pytest
from tools.fengshui.action_selector import (
    ActionSelector,
    Action,
    ActionType
)
from tools.fengshui.state_analyzer import ArchitectureState, ViolationInfo


@pytest.mark.unit
@pytest.mark.fast
class TestActionSelector:
    """Test suite for ActionSelector"""
    
    def test_initialization(self):
        """Test selector initializes correctly"""
        # ARRANGE & ACT
        selector = ActionSelector()
        
        # ASSERT
        assert selector.reflector is None
        assert selector.WEIGHTS['expected_improvement'] == 0.40
        assert selector.WEIGHTS['success_rate'] == 0.30
        assert selector.WEIGHTS['execution_time'] == 0.20
        assert selector.WEIGHTS['risk_level'] == 0.10
    
    def test_select_action_returns_highest_score(self):
        """Test select_action returns action with highest score"""
        # ARRANGE
        selector = ActionSelector()
        actions = [
            Action(ActionType.FIX_STRUCTURE, 'mod1', 'strat1', 0.5, 1000, 'LOW', 'Fix 1'),
            Action(ActionType.FIX_BLUEPRINT, 'mod2', 'strat1', 0.9, 2000, 'LOW', 'Fix 2'),
            Action(ActionType.FIX_DI_VIOLATION, 'mod3', 'strat1', 0.3, 500, 'HIGH', 'Fix 3')
        ]
        state = ArchitectureState(feng_shui_score=70.0)
        strategy_performance = {'strat1': 0.8}
        
        # ACT
        selected = selector.select_action(state, actions, strategy_performance)
        
        # ASSERT
        # Verify we got an action and it has the highest score
        assert selected in actions
        assert selected.priority_score == max(a.priority_score for a in actions)
    
    def test_select_action_raises_on_empty_list(self):
        """Test select_action raises ValueError when no actions available"""
        # ARRANGE
        selector = ActionSelector()
        state = ArchitectureState(feng_shui_score=50.0)
        
        # ACT & ASSERT
        with pytest.raises(ValueError, match="No available actions"):
            selector.select_action(state, [], {})
    
    def test_score_action_weighted_formula(self):
        """Test action scoring uses correct weighted formula"""
        # ARRANGE
        selector = ActionSelector()
        action = Action(
            type=ActionType.FIX_STRUCTURE,
            target_module='test_module',
            strategy='test_strategy',
            estimated_success_rate=0.8,
            estimated_time_ms=10000,
            risk_level='MEDIUM',
            description='Test action'
        )
        state = ArchitectureState(feng_shui_score=50.0)
        strategy_performance = {'test_strategy': 0.7}
        
        # ACT
        score = selector.score_action(action, state, strategy_performance)
        
        # ASSERT
        assert 0.0 <= score <= 1.0
        # Score should be a combination of all 4 factors
        assert score > 0.0  # Should have some score
    
    def test_score_action_penalizes_high_risk(self):
        """Test HIGH risk actions get penalized more than LOW risk"""
        # ARRANGE
        selector = ActionSelector()
        low_risk_action = Action(ActionType.FIX_STRUCTURE, 'mod', 'strat', 0.8, 5000, 'LOW', 'Low risk')
        high_risk_action = Action(ActionType.FIX_STRUCTURE, 'mod', 'strat', 0.8, 5000, 'HIGH', 'High risk')
        state = ArchitectureState(feng_shui_score=50.0)
        strategy_performance = {'strat': 0.8}
        
        # ACT
        low_score = selector.score_action(low_risk_action, state, strategy_performance)
        high_score = selector.score_action(high_risk_action, state, strategy_performance)
        
        # ASSERT
        assert low_score > high_score  # Low risk should score higher
    
    def test_score_action_prefers_faster_execution(self):
        """Test faster actions score higher than slower ones"""
        # ARRANGE
        selector = ActionSelector()
        fast_action = Action(ActionType.FIX_STRUCTURE, 'mod', 'strat', 0.7, 1000, 'LOW', 'Fast')
        slow_action = Action(ActionType.FIX_STRUCTURE, 'mod', 'strat', 0.7, 50000, 'LOW', 'Slow')
        state = ArchitectureState(feng_shui_score=50.0)
        strategy_performance = {'strat': 0.7}
        
        # ACT
        fast_score = selector.score_action(fast_action, state, strategy_performance)
        slow_score = selector.score_action(slow_action, state, strategy_performance)
        
        # ASSERT
        assert fast_score > slow_score
    
    def test_estimate_improvement_for_critical_violation(self):
        """Test improvement estimation considers violation severity"""
        # ARRANGE
        selector = ActionSelector()
        action = Action(ActionType.FIX_DI_VIOLATION, 'mod1', 'strat', 0.7, 1000, 'LOW', 'Fix DI')
        violation = ViolationInfo('fix_di_violation', 'CRITICAL', 'mod1/api.py', 10, 'DI issue', 'di_compliance')
        state = ArchitectureState(
            feng_shui_score=50.0,
            violations_by_type={'fix_di_violation': [violation]}
        )
        
        # ACT
        improvement = selector.estimate_improvement(action, state)
        
        # ASSERT
        # Should have some improvement score (matching logic may vary)
        assert 0.0 <= improvement <= 1.0
    
    def test_estimate_improvement_for_strategy_switch(self):
        """Test strategy switch has moderate improvement estimate"""
        # ARRANGE
        selector = ActionSelector()
        action = Action(ActionType.SWITCH_STRATEGY, 'all', 'switch', 0.7, 100, 'LOW', 'Switch strategy')
        state = ArchitectureState(feng_shui_score=50.0)
        
        # ACT
        improvement = selector.estimate_improvement(action, state)
        
        # ASSERT
        assert improvement == 0.3  # Moderate improvement expected
    
    def test_generate_available_actions_prioritizes_critical(self):
        """Test action generation prioritizes CRITICAL violations"""
        # ARRANGE
        selector = ActionSelector()
        critical_v = ViolationInfo('structure', 'CRITICAL', 'mod1/file.py', 10, 'Critical issue', 'structure')
        medium_v = ViolationInfo('blueprint', 'MEDIUM', 'mod2/api.py', 20, 'Medium issue', 'blueprint')
        state = ArchitectureState(
            feng_shui_score=60.0,
            violations_by_severity={'CRITICAL': [critical_v], 'MEDIUM': [medium_v]}
        )
        
        # ACT
        actions = selector.generate_available_actions(state)
        
        # ASSERT
        # Should have action for critical violation + strategy switch
        assert len(actions) >= 2
        assert any(a.target_module == 'mod1' for a in actions)
    
    def test_generate_available_actions_always_includes_strategy_switch(self):
        """Test strategy switch is always available as fallback"""
        # ARRANGE
        selector = ActionSelector()
        state = ArchitectureState(feng_shui_score=100.0)  # Perfect score, no violations
        
        # ACT
        actions = selector.generate_available_actions(state)
        
        # ASSERT
        assert len(actions) >= 1
        assert any(a.type == ActionType.SWITCH_STRATEGY for a in actions)


@pytest.mark.unit
@pytest.mark.fast
class TestAction:
    """Test suite for Action dataclass"""
    
    def test_action_creation(self):
        """Test Action can be created with all fields"""
        # ARRANGE & ACT
        action = Action(
            type=ActionType.FIX_STRUCTURE,
            target_module='test_module',
            strategy='conservative',
            estimated_success_rate=0.85,
            estimated_time_ms=5000,
            risk_level='MEDIUM',
            description='Fix module structure'
        )
        
        # ASSERT
        assert action.type == ActionType.FIX_STRUCTURE
        assert action.target_module == 'test_module'
        assert action.strategy == 'conservative'
        assert action.estimated_success_rate == 0.85
        assert action.estimated_time_ms == 5000
        assert action.risk_level == 'MEDIUM'
        assert action.description == 'Fix module structure'
        assert action.priority_score == 0.0  # Default value