"""
Gu Wu Agent Orchestrator

Main ReAct loop implementation for autonomous test orchestration.
Combines reasoning (what to do) + acting (doing it) + observing (results).
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
import json

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from tools.guwu.agent.reasoning import ReasoningEngine, ThoughtProcess, GoalType
from tools.guwu.agent.actions import ActionExecutor, ActionResult
from tools.guwu.agent.reflector import GuWuReflector


@dataclass
class AgentGoal:
    """Represents a testing goal for the agent"""
    description: str
    goal_type: GoalType
    target_metrics: Dict[str, Any]
    max_iterations: int = 10
    timeout_seconds: int = 300
    
    def to_dict(self) -> Dict:
        return {
            'description': self.description,
            'goal_type': self.goal_type.value,
            'target_metrics': self.target_metrics,
            'max_iterations': self.max_iterations,
            'timeout_seconds': self.timeout_seconds
        }


@dataclass
class Observation:
    """
    Observation after action execution
    
    Contains:
    - What we observed from action result
    - What we learned
    - What should happen next
    """
    timestamp: datetime
    action_result: ActionResult
    analysis: str
    next_needed: str
    confidence: float
    should_continue: bool
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'action_result': self.action_result.to_dict(),
            'analysis': self.analysis,
            'next_needed': self.next_needed,
            'confidence': confidence,
            'should_continue': self.should_continue
        }


@dataclass
class AgentSession:
    """Complete agent session record"""
    goal: AgentGoal
    start_time: datetime
    end_time: Optional[datetime]
    thoughts: List[ThoughtProcess]
    actions: List[ActionResult]
    observations: List[Observation]
    final_status: str
    success: bool
    total_iterations: int
    
    def to_dict(self) -> Dict:
        return {
            'goal': self.goal.to_dict(),
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'thoughts': [t.to_dict() for t in self.thoughts],
            'actions': [a.to_dict() for a in self.actions],
            'observations': [o.to_dict() for o in self.observations],
            'final_status': self.final_status,
            'success': self.success,
            'total_iterations': self.total_iterations,
            'duration': (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        }


class GuWuAgent:
    """
    Autonomous test orchestrator with ReAct pattern
    
    ReAct Loop:
    1. REASON: Think about what to do next
    2. ACT: Execute chosen action
    3. OBSERVE: Analyze results
    4. REFLECT: Decide if done or continue
    
    Example goals:
    - "Achieve 90% coverage on knowledge_graph module"
    - "Fix all flaky tests"
    - "Optimize test suite to <5s per test"
    """
    
    def __init__(self, db_path: str = 'tools/guwu/metrics.db', verbose: bool = True, enable_reflection: bool = True):
        """
        Initialize Gu Wu Agent
        
        Args:
            db_path: Path to Gu Wu metrics database
            verbose: Enable detailed logging
            enable_reflection: Enable Phase 6 meta-learning (default: True)
        """
        self.db_path = db_path
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.reasoning_engine = ReasoningEngine(db_path, verbose)
        self.action_executor = ActionExecutor(db_path, verbose)
        self.reflector = GuWuReflector() if enable_reflection else None
        
        # Session tracking
        self.current_session: Optional[AgentSession] = None
        self.session_history: List[AgentSession] = []
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def run_autonomous_session(self, goal_description: str, 
                               context: Optional[Dict] = None,
                               max_iterations: int = 10) -> AgentSession:
        """
        Run autonomous testing session with ReAct loop
        
        Args:
            goal_description: What to achieve (e.g., "Achieve 90% coverage")
            context: Optional initial context
            max_iterations: Maximum reasoning loops before timeout
        
        Returns:
            AgentSession with complete execution record
        """
        # Initialize session
        context = context or {}
        context['goal'] = goal_description
        
        goal = AgentGoal(
            description=goal_description,
            goal_type=self._parse_goal_type(goal_description),
            target_metrics=self._extract_target_metrics(goal_description, context),
            max_iterations=max_iterations
        )
        
        self.current_session = AgentSession(
            goal=goal,
            start_time=datetime.now(),
            end_time=None,
            thoughts=[],
            actions=[],
            observations=[],
            final_status='in_progress',
            success=False,
            total_iterations=0
        )
        
        self.logger.info("=" * 80)
        self.logger.info(f"[Gu Wu Agent] STARTING AUTONOMOUS SESSION")
        self.logger.info("=" * 80)
        self.logger.info(f"Goal: {goal_description}")
        self.logger.info(f"Max Iterations: {max_iterations}")
        self.logger.info("=" * 80)
        
        # ReAct Loop
        iteration = 0
        done = False
        
        while not done and iteration < max_iterations:
            iteration += 1
            self.logger.info(f"\n[Gu Wu Agent] === ITERATION {iteration}/{max_iterations} ===")
            
            try:
                # 1. REASON: What should I do next?
                thought = self._reason(goal_description, context)
                self.current_session.thoughts.append(thought)
                
                # Check if reasoning says we're done
                if thought.action == 'complete':
                    self.logger.info("[Gu Wu Agent] Reasoning decided goal is achieved")
                    done = True
                    self.current_session.final_status = 'complete'
                    self.current_session.success = True
                    break
                
                # 2. ACT: Execute the chosen action
                action_start_time = datetime.now()
                action_result = self._act(thought.action, context)
                action_duration = (datetime.now() - action_start_time).total_seconds() * 1000  # ms
                self.current_session.actions.append(action_result)
                
                # Record execution for Phase 6 reflection
                if self.reflector:
                    self.reflector.record_execution(
                        session_id=self.session_id,
                        goal=goal_description,
                        strategy_used=thought.action,
                        action_type=action_result.action.split('_')[0],  # e.g., 'analyze' from 'analyze_gaps'
                        confidence=thought.confidence,
                        success=action_result.success,
                        duration_ms=action_duration,
                        error_message=action_result.error if not action_result.success else None,
                        context=context
                    )
                
                # 3. OBSERVE: Analyze what happened
                observation = self._observe(action_result, thought)
                self.current_session.observations.append(observation)
                
                # Update context with new information
                context = self._update_context(context, action_result, observation)
                
                # 4. REFLECT: Should we continue?
                done = not observation.should_continue
                
                if done:
                    self.logger.info("[Gu Wu Agent] Observation decided to complete")
                    self.current_session.final_status = 'complete'
                    self.current_session.success = observation.confidence > 0.7
                
            except Exception as e:
                self.logger.error(f"[Gu Wu Agent] Error in iteration {iteration}: {e}")
                self.current_session.final_status = 'error'
                self.current_session.success = False
                done = True
        
        # Check if we timed out
        if iteration >= max_iterations and not done:
            self.logger.warning(f"[Gu Wu Agent] Reached max iterations ({max_iterations})")
            self.current_session.final_status = 'timeout'
            self.current_session.success = False
        
        # Finalize session
        self.current_session.end_time = datetime.now()
        self.current_session.total_iterations = iteration
        
        # Generate Phase 6 reflection insights
        if self.reflector:
            self.logger.info("\n" + "=" * 80)
            self.logger.info("[Gu Wu Agent] PHASE 6: META-LEARNING REFLECTION")
            self.logger.info("=" * 80)
            
            insights = self.reflector.generate_learning_insights()
            
            if insights:
                self.logger.info(f"Generated {len(insights)} meta-learning insights:")
                for insight in insights:
                    self.logger.info(f"\n[{insight.priority}] {insight.insight_type.value}")
                    self.logger.info(f"  {insight.description}")
                    self.logger.info(f"  Confidence: {insight.confidence:.1%}")
                    self.logger.info(f"  Recommendation: {insight.recommendation}")
            else:
                self.logger.info("No insights yet. Need more execution history.")
            
            self.logger.info("=" * 80)
        
        # Log summary
        self._log_session_summary(self.current_session)
        
        # Store in history
        self.session_history.append(self.current_session)
        
        return self.current_session
    
    def _reason(self, goal: str, context: Dict) -> ThoughtProcess:
        """
        REASONING phase: Decide what to do next
        
        Uses ReasoningEngine to analyze situation and choose action
        """
        if self.verbose:
            self.logger.info("\n[REASON] Analyzing situation...")
        
        thought = self.reasoning_engine.reason(goal, context)
        
        if self.verbose:
            self.logger.info(f"[REASON] Reasoning: {thought.reasoning}")
            self.logger.info(f"[REASON] Decision: {thought.action}")
            self.logger.info(f"[REASON] Confidence: {thought.confidence:.1%}")
        
        return thought
    
    def _act(self, action: str, context: Dict) -> ActionResult:
        """
        ACTION phase: Execute the chosen action
        
        Uses ActionExecutor to perform testing action
        """
        if self.verbose:
            self.logger.info(f"\n[ACT] Executing: {action}")
        
        # Extract parameters from context if needed
        params = self._prepare_action_params(action, context)
        
        action_result = self.action_executor.execute(action, params)
        
        if self.verbose:
            self.logger.info(f"[ACT] Success: {action_result.success}")
            self.logger.info(f"[ACT] Duration: {action_result.duration:.2f}s")
        
        return action_result
    
    def _observe(self, action_result: ActionResult, thought: ThoughtProcess) -> Observation:
        """
        OBSERVATION phase: Analyze action results
        
        Determines:
        - What did we learn?
        - What should happen next?
        - Should we continue or complete?
        """
        if self.verbose:
            self.logger.info("\n[OBSERVE] Analyzing results...")
        
        # Analyze based on action type
        analysis, next_needed, should_continue = self._analyze_action_result(
            action_result, 
            thought
        )
        
        # Calculate confidence in observation
        confidence = self._calculate_observation_confidence(action_result, thought)
        
        observation = Observation(
            timestamp=datetime.now(),
            action_result=action_result,
            analysis=analysis,
            next_needed=next_needed,
            confidence=confidence,
            should_continue=should_continue
        )
        
        if self.verbose:
            self.logger.info(f"[OBSERVE] Analysis: {analysis}")
            self.logger.info(f"[OBSERVE] Next Needed: {next_needed}")
            self.logger.info(f"[OBSERVE] Should Continue: {should_continue}")
        
        return observation
    
    def _analyze_action_result(self, action_result: ActionResult, 
                               thought: ThoughtProcess) -> tuple[str, str, bool]:
        """
        Analyze action result to determine next step
        
        Returns:
            (analysis, next_needed, should_continue)
        """
        action = action_result.action
        data = action_result.data
        
        # Coverage gap analysis
        if action == 'analyze_gaps':
            critical_gaps = data.get('critical_gaps', 0)
            total_gaps = data.get('total_gaps', 0)
            
            if critical_gaps == 0:
                return (
                    f"No critical gaps found ({total_gaps} total gaps are lower priority)",
                    'complete',
                    False
                )
            else:
                return (
                    f"Found {critical_gaps} critical gaps requiring tests",
                    'generate_critical_tests',
                    True
                )
        
        # Test generation
        elif action in ['generate_targeted_tests', 'generate_critical_tests']:
            tests_generated = data.get('tests_generated', 0) or data.get('critical_tests_generated', 0)
            
            if tests_generated > 0:
                return (
                    f"Generated {tests_generated} test templates",
                    'verify_coverage',
                    True
                )
            else:
                return (
                    "No tests generated, may need manual intervention",
                    'complete',
                    False
                )
        
        # Flaky test analysis
        elif action == 'analyze_flaky_patterns':
            patterns_found = data.get('patterns_identified', 0)
            
            if patterns_found > 0:
                return (
                    f"Identified {patterns_found} flaky patterns",
                    'generate_flaky_fixes',
                    True
                )
            else:
                return (
                    "No clear patterns, tests may need manual review",
                    'complete',
                    False
                )
        
        # Fix generation
        elif action == 'generate_flaky_fixes':
            fixes_generated = data.get('fixes_generated', 0)
            
            if fixes_generated > 0:
                return (
                    f"Generated {fixes_generated} fix suggestions",
                    'complete',
                    False
                )
            else:
                return (
                    "Could not generate automatic fixes",
                    'complete',
                    False
                )
        
        # Performance analysis
        elif action == 'analyze_performance_bottlenecks':
            bottlenecks = data.get('bottlenecks_identified', 0)
            
            if bottlenecks > 0:
                return (
                    f"Identified {bottlenecks} performance bottlenecks",
                    'generate_optimizations',
                    True
                )
            else:
                return (
                    "No major bottlenecks found",
                    'complete',
                    False
                )
        
        # Optimization generation
        elif action == 'generate_optimizations':
            optimizations = data.get('optimizations_generated', 0)
            
            if optimizations > 0:
                return (
                    f"Generated {optimizations} optimization suggestions",
                    'complete',
                    False
                )
            else:
                return (
                    "No optimizations could be generated",
                    'complete',
                    False
                )
        
        # Prediction
        elif action == 'predict_failures':
            high_risk = data.get('high_risk_tests', 0)
            
            return (
                f"Predicted {high_risk} high-risk tests",
                'complete',
                False
            )
        
        # Coverage verification
        elif action == 'verify_coverage':
            coverage_pct = data.get('coverage_percentage', 0)
            
            return (
                f"Current coverage: {coverage_pct:.1%}",
                'complete',
                False
            )
        
        # Complete action
        elif action == 'complete':
            return (
                "Goal achieved",
                'none',
                False
            )
        
        # Unknown action
        else:
            return (
                f"Unknown action result for: {action}",
                'complete',
                False
            )
    
    def _calculate_observation_confidence(self, action_result: ActionResult, 
                                         thought: ThoughtProcess) -> float:
        """Calculate confidence in observation"""
        # Start with action success
        confidence = 0.8 if action_result.success else 0.3
        
        # Factor in reasoning confidence
        confidence = (confidence + thought.confidence) / 2
        
        return confidence
    
    def _update_context(self, context: Dict, action_result: ActionResult, 
                       observation: Observation) -> Dict:
        """Update context with new information from action"""
        # Add action result data to context
        if action_result.success:
            context.update(action_result.data)
        
        # Track history
        if 'history' not in context:
            context['history'] = []
        
        context['history'].append({
            'action': action_result.action,
            'timestamp': action_result.timestamp.isoformat(),
            'success': action_result.success
        })
        
        return context
    
    def _prepare_action_params(self, action: str, context: Dict) -> Dict:
        """Prepare parameters for action from context"""
        params = {}
        
        # Add relevant context based on action
        if action == 'run_tests':
            params['tests'] = context.get('tests_to_run', [])
        
        return params
    
    def _parse_goal_type(self, goal_description: str) -> GoalType:
        """Parse goal string to determine type"""
        goal_lower = goal_description.lower()
        
        if 'coverage' in goal_lower:
            return GoalType.COVERAGE
        elif 'flaky' in goal_lower:
            return GoalType.FLAKY_TESTS
        elif 'performance' in goal_lower or 'optimize' in goal_lower:
            return GoalType.PERFORMANCE
        elif 'gap' in goal_lower:
            return GoalType.GAP_ANALYSIS
        else:
            return GoalType.CUSTOM
    
    def _extract_target_metrics(self, goal: str, context: Dict) -> Dict:
        """Extract target metrics from goal string"""
        import re
        
        metrics = {}
        
        # Coverage percentage
        match = re.search(r'(\d+)%', goal)
        if match:
            metrics['target_coverage'] = float(match.group(1)) / 100.0
        
        # Duration threshold
        match = re.search(r'<\s*(\d+\.?\d*)\s*s', goal)
        if match:
            metrics['target_duration'] = float(match.group(1))
        
        return metrics
    
    def _log_session_summary(self, session: AgentSession):
        """Log summary of completed session"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("[Gu Wu Agent] SESSION COMPLETE")
        self.logger.info("=" * 80)
        self.logger.info(f"Goal: {session.goal.description}")
        self.logger.info(f"Status: {session.final_status}")
        self.logger.info(f"Success: {session.success}")
        self.logger.info(f"Iterations: {session.total_iterations}")
        self.logger.info(f"Duration: {(session.end_time - session.start_time).total_seconds():.2f}s")
        self.logger.info(f"Thoughts: {len(session.thoughts)}")
        self.logger.info(f"Actions: {len(session.actions)}")
        self.logger.info(f"Observations: {len(session.observations)}")
        self.logger.info("=" * 80)
    
    def get_session_report(self, session: Optional[AgentSession] = None) -> Dict:
        """Get detailed report of session"""
        session = session or self.current_session
        
        if not session:
            return {'error': 'No session available'}
        
        return session.to_dict()
    
    def save_session_report(self, filepath: str, session: Optional[AgentSession] = None):
        """Save session report to JSON file"""
        session = session or self.current_session
        
        if not session:
            raise ValueError("No session to save")
        
        with open(filepath, 'w') as f:
            json.dump(session.to_dict(), f, indent=2)
        
        self.logger.info(f"[Gu Wu Agent] Session report saved to: {filepath}")


if __name__ == '__main__':
    # Example usage
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    agent = GuWuAgent(verbose=True)
    
    # Example 1: Coverage goal
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Coverage Goal")
    print("=" * 80)
    session = agent.run_autonomous_session(
        goal_description="Achieve 90% coverage on knowledge_graph module",
        context={'current_coverage': 0.65},
        max_iterations=5
    )
    print(f"\nResult: {session.final_status}")
    print(f"Success: {session.success}")
    
    # Example 2: Flaky test goal
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Flaky Test Goal")
    print("=" * 80)
    session = agent.run_autonomous_session(
        goal_description="Fix all flaky tests",
        context={'flaky_tests_count': 3, 'total_tests': 100},
        max_iterations=5
    )
    print(f"\nResult: {session.final_status}")
    print(f"Success: {session.success}")