"""
Unit Tests for Gu Wu Agent (ReAct Pattern)

Tests the autonomous test orchestrator:
- Reasoning engine
- Action executor
- Complete ReAct loop
"""

import pytest
from datetime import datetime
from typing import Dict, List
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from tests.guwu.agent.reasoning import ReasoningEngine, ThoughtProcess, GoalType
from tests.guwu.agent.actions import ActionExecutor, ActionResult
from tests.guwu.agent.orchestrator import GuWuAgent, AgentGoal, Observation


@pytest.mark.unit
@pytest.mark.fast
class TestReasoningEngine:
    """Test reasoning engine decision-making"""
    
    def test_parse_coverage_goal(self):
        """Test parsing coverage goals"""
        # ARRANGE
        engine = ReasoningEngine(db_path='tests/guwu/metrics.db', verbose=False)
        
        # ACT
        goal_type = engine._parse_goal_type("Achieve 90% coverage")
        
        # ASSERT
        assert goal_type == GoalType.COVERAGE
    
    def test_parse_flaky_goal(self):
        """Test parsing flaky test goals"""
        # ARRANGE
        engine = ReasoningEngine(db_path='tests/guwu/metrics.db', verbose=False)
        
        # ACT
        goal_type = engine._parse_goal_type("Fix all flaky tests")
        
        # ASSERT
        assert goal_type == GoalType.FLAKY_TESTS
    
    def test_parse_performance_goal(self):
        """Test parsing performance goals"""
        # ARRANGE
        engine = ReasoningEngine(db_path='tests/guwu/metrics.db', verbose=False)
        
        # ACT
        goal_type = engine._parse_goal_type("Optimize test suite performance")
        
        # ASSERT
        assert goal_type == GoalType.PERFORMANCE
    
    def test_reason_coverage_gap_large(self):
        """Test reasoning when coverage gap is large"""
        # ARRANGE
        engine = ReasoningEngine(db_path='tests/guwu/metrics.db', verbose=False)
        context = {
            'goal': 'Achieve 90% coverage',
            'current_coverage': 0.50,
            'history': []
        }
        
        # ACT
        thought = engine.reason('Achieve 90% coverage', context)
        
        # ASSERT
        assert thought.action == 'analyze_gaps'
        assert thought.confidence > 0.0
        assert 'gap' in thought.reasoning.lower()
    
    def test_reason_coverage_achieved(self):
        """Test reasoning when coverage goal is achieved"""
        # ARRANGE
        engine = ReasoningEngine(db_path='tests/guwu/metrics.db', verbose=False)
        context = {
            'goal': 'Achieve 90% coverage',
            'current_coverage': 0.92,
            'history': []
        }
        
        # ACT
        thought = engine.reason('Achieve 90% coverage', context)
        
        # ASSERT
        assert thought.action == 'complete'
        assert thought.confidence >= 0.7
    
    def test_extract_coverage_target(self):
        """Test extracting coverage percentage from goal"""
        # ARRANGE
        engine = ReasoningEngine(db_path='tests/guwu/metrics.db', verbose=False)
        
        # ACT
        target = engine._extract_coverage_target("Achieve 85% coverage")
        
        # ASSERT
        assert target == 0.85
    
    def test_extract_duration_target(self):
        """Test extracting duration target from goal"""
        # ARRANGE
        engine = ReasoningEngine(db_path='tests/guwu/metrics.db', verbose=False)
        
        # ACT
        target = engine._extract_duration_target("Optimize to <3s per test")
        
        # ASSERT
        assert target == 3.0
    
    def test_reasoning_history_tracking(self):
        """Test that reasoning history is tracked"""
        # ARRANGE
        engine = ReasoningEngine(db_path='tests/guwu/metrics.db', verbose=False)
        context = {'goal': 'Test goal', 'current_coverage': 0.5, 'history': []}
        
        # ACT
        thought1 = engine.reason('Achieve 90% coverage', context)
        thought2 = engine.reason('Achieve 90% coverage', context)
        
        # ASSERT
        assert len(engine.reasoning_history) == 2
        assert engine.reasoning_history[0] == thought1
        assert engine.reasoning_history[1] == thought2


@pytest.mark.unit
@pytest.mark.fast
class TestActionExecutor:
    """Test action executor"""
    
    def test_execute_complete_action(self):
        """Test executing 'complete' action"""
        # ARRANGE
        executor = ActionExecutor(db_path='tests/guwu/metrics.db', verbose=False)
        
        # ACT
        result = executor.execute('complete')
        
        # ASSERT
        assert result.action == 'complete'
        assert result.success is True
        assert 'complete' in result.data['status']
    
    def test_execute_unknown_action(self):
        """Test executing unknown action"""
        # ARRANGE
        executor = ActionExecutor(db_path='tests/guwu/metrics.db', verbose=False)
        
        # ACT
        result = executor.execute('unknown_action')
        
        # ASSERT
        assert result.action == 'unknown_action'
        assert result.success is False
        assert 'error' in result.data
    
    def test_action_history_tracking(self):
        """Test that action history is tracked"""
        # ARRANGE
        executor = ActionExecutor(db_path='tests/guwu/metrics.db', verbose=False)
        
        # ACT
        result1 = executor.execute('complete')
        result2 = executor.execute('complete')
        
        # ASSERT
        assert len(executor.action_history) == 2
        assert executor.action_history[0] == result1
        assert executor.action_history[1] == result2
    
    def test_action_duration_tracking(self):
        """Test that action duration is tracked"""
        # ARRANGE
        executor = ActionExecutor(db_path='tests/guwu/metrics.db', verbose=False)
        
        # ACT
        result = executor.execute('complete')
        
        # ASSERT
        assert result.duration >= 0.0
        assert isinstance(result.duration, float)
    
    def test_get_action_summary(self):
        """Test action summary generation"""
        # ARRANGE
        executor = ActionExecutor(db_path='tests/guwu/metrics.db', verbose=False)
        executor.execute('complete')
        executor.execute('complete')
        
        # ACT
        summary = executor.get_action_summary()
        
        # ASSERT
        assert summary['total_actions'] == 2
        assert summary['success_rate'] == 1.0
        assert summary['success_count'] == 2
        assert summary['failure_count'] == 0


@pytest.mark.unit
class TestGuWuAgent:
    """Test complete agent orchestration"""
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        # ARRANGE & ACT
        agent = GuWuAgent(verbose=False)
        
        # ASSERT
        assert agent.reasoning_engine is not None
        assert agent.action_executor is not None
        assert agent.current_session is None
        assert len(agent.session_history) == 0
    
    def test_parse_goal_type_coverage(self):
        """Test parsing coverage goal type"""
        # ARRANGE
        agent = GuWuAgent(verbose=False)
        
        # ACT
        goal_type = agent._parse_goal_type("Achieve 80% coverage")
        
        # ASSERT
        assert goal_type == GoalType.COVERAGE
    
    def test_extract_target_metrics(self):
        """Test extracting target metrics from goal"""
        # ARRANGE
        agent = GuWuAgent(verbose=False)
        
        # ACT
        metrics = agent._extract_target_metrics("Achieve 85% coverage", {})
        
        # ASSERT
        assert 'target_coverage' in metrics
        assert metrics['target_coverage'] == 0.85
    
    def test_update_context_adds_history(self):
        """Test context updating adds history"""
        # ARRANGE
        agent = GuWuAgent(verbose=False)
        context = {}
        action_result = ActionResult(
            action='test_action',
            success=True,
            data={'key': 'value'},
            duration=1.0,
            timestamp=datetime.now()
        )
        observation = Observation(
            timestamp=datetime.now(),
            action_result=action_result,
            analysis='Test analysis',
            next_needed='next',
            confidence=0.8,
            should_continue=False
        )
        
        # ACT
        updated_context = agent._update_context(context, action_result, observation)
        
        # ASSERT
        assert 'history' in updated_context
        assert len(updated_context['history']) == 1
        assert updated_context['history'][0]['action'] == 'test_action'
        assert updated_context['history'][0]['success'] is True
    
    def test_analyze_gaps_action_with_critical_gaps(self):
        """Test analyzing gap action result with critical gaps"""
        # ARRANGE
        agent = GuWuAgent(verbose=False)
        action_result = ActionResult(
            action='analyze_gaps',
            success=True,
            data={'critical_gaps': 5, 'total_gaps': 20},
            duration=1.0,
            timestamp=datetime.now()
        )
        thought = ThoughtProcess(
            timestamp=datetime.now(),
            situation={},
            reasoning='Test',
            decision='Test',
            action='analyze_gaps',
            confidence=0.8,
            alternatives_considered=[]
        )
        
        # ACT
        analysis, next_needed, should_continue = agent._analyze_action_result(action_result, thought)
        
        # ASSERT
        assert 'critical gaps' in analysis.lower()
        assert next_needed == 'generate_critical_tests'
        assert should_continue is True
    
    def test_analyze_gaps_action_no_critical_gaps(self):
        """Test analyzing gap action result with no critical gaps"""
        # ARRANGE
        agent = GuWuAgent(verbose=False)
        action_result = ActionResult(
            action='analyze_gaps',
            success=True,
            data={'critical_gaps': 0, 'total_gaps': 10},
            duration=1.0,
            timestamp=datetime.now()
        )
        thought = ThoughtProcess(
            timestamp=datetime.now(),
            situation={},
            reasoning='Test',
            decision='Test',
            action='analyze_gaps',
            confidence=0.8,
            alternatives_considered=[]
        )
        
        # ACT
        analysis, next_needed, should_continue = agent._analyze_action_result(action_result, thought)
        
        # ASSERT
        assert 'no critical gaps' in analysis.lower()
        assert next_needed == 'complete'
        assert should_continue is False
    
    def test_session_tracking(self):
        """Test that sessions are tracked in history"""
        # ARRANGE
        agent = GuWuAgent(verbose=False)
        
        # ACT
        session = agent.run_autonomous_session(
            goal_description="Test goal",
            context={'current_coverage': 0.95},
            max_iterations=1
        )
        
        # ASSERT
        assert len(agent.session_history) == 1
        assert agent.session_history[0] == session
    
    def test_session_report_generation(self):
        """Test session report generation"""
        # ARRANGE
        agent = GuWuAgent(verbose=False)
        session = agent.run_autonomous_session(
            goal_description="Achieve 90% coverage",
            context={'current_coverage': 0.95},
            max_iterations=1
        )
        
        # ACT
        report = agent.get_session_report(session)
        
        # ASSERT
        assert 'goal' in report
        assert 'start_time' in report
        assert 'end_time' in report
        assert 'thoughts' in report
        assert 'actions' in report
        assert 'observations' in report
        assert 'final_status' in report
        assert 'success' in report


@pytest.mark.integration
class TestReActLoop:
    """Integration tests for complete ReAct loop"""
    
    def test_coverage_goal_already_achieved(self):
        """Test goal that is already achieved completes immediately"""
        # ARRANGE
        agent = GuWuAgent(verbose=False)
        
        # ACT
        session = agent.run_autonomous_session(
            goal_description="Achieve 90% coverage",
            context={'current_coverage': 0.95},
            max_iterations=5
        )
        
        # ASSERT
        assert session.final_status == 'complete'
        assert session.success is True
        assert session.total_iterations >= 1
    
    def test_max_iterations_timeout(self):
        """Test that agent stops at max iterations"""
        # ARRANGE
        agent = GuWuAgent(verbose=False)
        
        # ACT
        session = agent.run_autonomous_session(
            goal_description="Achieve 100% coverage",  # Unachievable
            context={'current_coverage': 0.50},
            max_iterations=3
        )
        
        # ASSERT
        assert session.total_iterations == 3
        # May timeout or complete depending on actions
        assert session.final_status in ['timeout', 'complete']


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])