"""
Feng Shui ReAct Agent - Autonomous Architecture Improvement

Main orchestrator implementing the ReAct pattern:
REASON → ACT → OBSERVE → REFLECT

Inspired by Gu Wu agent architecture.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field

from .state_analyzer import ArchitectureStateAnalyzer, ArchitectureState
from .strategy_manager import StrategyManager, FixStrategy
from .action_selector import ActionSelector, Action, ActionType
from .reflector import FengShuiReflector


@dataclass
class ReActIteration:
    """Single iteration of ReAct loop"""
    iteration: int
    reasoning: str
    action: Action
    observation: str
    reflection: str
    feng_shui_score_before: float
    feng_shui_score_after: float
    success: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SessionReport:
    """Report for entire ReAct session"""
    goal_description: str
    initial_score: float
    final_score: float
    improvement: float
    iterations: List[ReActIteration]
    total_fixes_attempted: int
    successful_fixes: int
    failed_fixes: int
    strategy_switches: int
    total_time_seconds: float
    completion_status: str  # GOAL_ACHIEVED/MAX_ITERATIONS/STUCK
    insights_generated: List[str]


class FengShuiReActAgent:
    """
    Autonomous architecture improvement agent
    
    Uses ReAct pattern to iteratively improve Feng Shui score:
    1. REASON: Analyze current state, select optimal action
    2. ACT: Execute selected action
    3. OBSERVE: Measure impact of action
    4. REFLECT: Learn from outcome, update strategies
    """
    
    def __init__(
        self,
        modules_dir: Path = None,
        verbose: bool = True,
        enable_reflection: bool = True
    ):
        """
        Initialize ReAct agent
        
        Args:
            modules_dir: Path to modules directory
            verbose: Print detailed progress
            enable_reflection: Enable meta-learning
        """
        self.modules_dir = modules_dir or Path('modules')
        self.verbose = verbose
        self.enable_reflection = enable_reflection
        
        # Initialize components
        self.state_analyzer = ArchitectureStateAnalyzer(self.modules_dir)
        self.strategy_manager = StrategyManager()
        self.action_selector = ActionSelector()
        self.reflector = FengShuiReflector() if enable_reflection else None
        
        # Session state
        self.current_state: Optional[ArchitectureState] = None
        self.iterations: List[ReActIteration] = []
        self.start_time = datetime.now()
    
    def run_autonomous_session(
        self,
        goal_description: str,
        target_score: float = 95.0,
        max_iterations: int = 10,
        target_modules: List[str] = None
    ) -> SessionReport:
        """
        Run autonomous improvement session
        
        Continues until: goal achieved OR max iterations OR stuck
        
        Args:
            goal_description: What to achieve (e.g., "Fix all DI violations")
            target_score: Target Feng Shui score (0-100)
            max_iterations: Maximum iteration limit
            target_modules: Specific modules to improve (None = all)
            
        Returns:
            Session report with all details
        """
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"Feng Shui ReAct Agent - Autonomous Session")
            print(f"{'='*70}")
            print(f"Goal: {goal_description}")
            print(f"Target Score: {target_score}/100")
            print(f"Max Iterations: {max_iterations}")
            print(f"{'='*70}\n")
        
        # Analyze initial state
        self.current_state = self.state_analyzer.analyze_current_state(target_modules)
        initial_score = self.current_state.feng_shui_score
        
        if self.verbose:
            print(f"[INITIAL STATE]")
            print(f"Feng Shui Score: {initial_score:.1f}/100")
            print(f"Critical Violations: {len(self.current_state.get_critical_violations())}")
            print(f"Modules Affected: {len(self.current_state.modules_affected)}")
            print()
        
        # ReAct loop
        completion_status = 'MAX_ITERATIONS'
        consecutive_failures = 0
        
        for iteration in range(1, max_iterations + 1):
            if self.verbose:
                print(f"\n{'─'*70}")
                print(f"[ITERATION {iteration}/{max_iterations}]")
                print(f"{'─'*70}")
            
            # Check goal
            if self.current_state.feng_shui_score >= target_score:
                completion_status = 'GOAL_ACHIEVED'
                if self.verbose:
                    print(f"\n🎉 Goal achieved! Score: {self.current_state.feng_shui_score:.1f}/100")
                break
            
            # Check if stuck (3 consecutive failures)
            if consecutive_failures >= 3:
                completion_status = 'STUCK'
                if self.verbose:
                    print(f"\n⚠️ Stuck after 3 consecutive failures. Stopping.")
                break
            
            # Execute one ReAct iteration
            iteration_result = self._execute_iteration(iteration)
            self.iterations.append(iteration_result)
            
            # Update consecutive failure counter
            if iteration_result.success:
                consecutive_failures = 0
            else:
                consecutive_failures += 1
            
            if self.verbose:
                self._print_iteration_result(iteration_result)
        
        # Generate session report
        session_report = self._generate_session_report(
            goal_description,
            initial_score,
            completion_status
        )
        
        # Generate insights if reflection enabled
        if self.enable_reflection and self.reflector:
            insights = self.reflector.generate_insights()
            session_report.insights_generated = [i.description for i in insights[:5]]
        
        if self.verbose:
            self._print_session_report(session_report)
        
        return session_report
    
    def _execute_iteration(self, iteration_num: int) -> ReActIteration:
        """
        Execute single ReAct iteration
        
        1. REASON: Analyze state, select action
        2. ACT: Execute action
        3. OBSERVE: Measure impact
        4. REFLECT: Learn from outcome
        
        Args:
            iteration_num: Current iteration number
            
        Returns:
            Iteration result with all details
        """
        score_before = self.current_state.feng_shui_score
        
        # 1. REASON: Select optimal action
        reasoning = self._reason()
        
        # Generate available actions
        available_actions = self.action_selector.generate_available_actions(self.current_state)
        
        # Get strategy performance data
        strategy_performance = {}
        if self.reflector:
            for strategy in self.strategy_manager.get_available_strategies():
                strategy_performance[strategy] = self.reflector.get_strategy_success_rate(strategy)
        else:
            # Default rates if no history
            strategy_performance = {s: 0.5 for s in self.strategy_manager.get_available_strategies()}
        
        # Select best action
        selected_action = self.action_selector.select_action(
            self.current_state,
            available_actions,
            strategy_performance
        )
        selected_action.strategy = self.strategy_manager.current_strategy.value
        
        # 2. ACT: Execute action
        execution_start = datetime.now()
        success, observation = self._act(selected_action)
        execution_time_ms = int((datetime.now() - execution_start).total_seconds() * 1000)
        
        # 3. OBSERVE: Measure new state
        self.current_state = self.state_analyzer.analyze_current_state()
        score_after = self.current_state.feng_shui_score
        
        # 4. REFLECT: Learn from outcome
        reflection = self._reflect(selected_action, success, score_before, score_after)
        
        # Record in reflector if enabled
        if self.enable_reflection and self.reflector:
            self.reflector.record_fix_attempt(
                fix_type=selected_action.type.value,
                predicted_success=selected_action.estimated_success_rate,
                actual_success=success,
                module_name=selected_action.target_module,
                strategy_used=selected_action.strategy,
                execution_time_ms=execution_time_ms,
                error_message=observation if not success else None
            )
        
        # Handle failures (strategy switching)
        if not success:
            self.strategy_manager.record_failure()
            if self.strategy_manager.should_switch_strategy():
                old_strategy = self.strategy_manager.current_strategy.value
                self.strategy_manager.switch_strategy()
                new_strategy = self.strategy_manager.current_strategy.value
                reflection += f" Switched strategy: {old_strategy} → {new_strategy}"
        
        return ReActIteration(
            iteration=iteration_num,
            reasoning=reasoning,
            action=selected_action,
            observation=observation,
            reflection=reflection,
            feng_shui_score_before=score_before,
            feng_shui_score_after=score_after,
            success=success
        )
    
    def _reason(self) -> str:
        """
        REASON: Analyze state and explain reasoning
        
        Returns:
            Reasoning description
        """
        critical_count = len(self.current_state.get_critical_violations())
        high_count = len(self.current_state.violations_by_severity.get('HIGH', []))
        
        if critical_count > 0:
            return f"Found {critical_count} CRITICAL violations - must fix immediately"
        elif high_count > 0:
            return f"No critical issues. Addressing {high_count} HIGH priority violations"
        else:
            return "No critical/high issues. Performing preventive maintenance"
    
    def _act(self, action: Action) -> tuple[bool, str]:
        """
        ACT: Execute the selected action
        
        Args:
            action: Action to execute
            
        Returns:
            (success, observation) tuple
        """
        # NOTE: This is a simplified implementation
        # In production, would integrate with automation_engine to execute actual fixes
        
        if action.type == ActionType.SWITCH_STRATEGY:
            return True, f"Switched to {self.strategy_manager.current_strategy.value} strategy"
        
        # Simulate fix execution (placeholder)
        # Real implementation would call automation_engine.apply_fix()
        observation = f"Simulated fix for {action.type.value} in {action.target_module}"
        
        # For now, assume 70% success rate (would be actual result in production)
        import random
        success = random.random() < action.estimated_success_rate
        
        if not success:
            observation = f"Fix failed: {action.description}"
        
        return success, observation
    
    def _reflect(
        self,
        action: Action,
        success: bool,
        score_before: float,
        score_after: float
    ) -> str:
        """
        REFLECT: Learn from the outcome
        
        Args:
            action: Action that was executed
            success: Whether action succeeded
            score_before: Score before action
            score_after: Score after action
            
        Returns:
            Reflection description
        """
        score_delta = score_after - score_before
        
        if success:
            if score_delta > 0:
                return f"✅ Success! Score improved by {score_delta:.1f} points"
            elif score_delta == 0:
                return f"✅ Success, but no score change (may have fixed non-scored issue)"
            else:
                return f"⚠️ Success, but score decreased by {abs(score_delta):.1f} points (unexpected)"
        else:
            return f"❌ Action failed. Score unchanged. Will try alternative approach."
    
    def _generate_session_report(
        self,
        goal_description: str,
        initial_score: float,
        completion_status: str
    ) -> SessionReport:
        """Generate comprehensive session report"""
        final_score = self.current_state.feng_shui_score if self.current_state else initial_score
        improvement = final_score - initial_score
        
        successful_fixes = sum(1 for i in self.iterations if i.success)
        failed_fixes = len(self.iterations) - successful_fixes
        
        # Count strategy switches
        strategy_switches = sum(
            1 for i in self.iterations 
            if 'Switched strategy' in i.reflection
        )
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        return SessionReport(
            goal_description=goal_description,
            initial_score=initial_score,
            final_score=final_score,
            improvement=improvement,
            iterations=self.iterations,
            total_fixes_attempted=len(self.iterations),
            successful_fixes=successful_fixes,
            failed_fixes=failed_fixes,
            strategy_switches=strategy_switches,
            total_time_seconds=total_time,
            completion_status=completion_status,
            insights_generated=[]  # Filled by caller if reflection enabled
        )
    
    def _print_iteration_result(self, iteration: ReActIteration):
        """Print iteration details"""
        status_icon = "✅" if iteration.success else "❌"
        score_delta = iteration.feng_shui_score_after - iteration.feng_shui_score_before
        delta_str = f"+{score_delta:.1f}" if score_delta >= 0 else f"{score_delta:.1f}"
        
        print(f"\n{status_icon} Iteration {iteration.iteration}")
        print(f"   Reasoning: {iteration.reasoning}")
        print(f"   Action: {iteration.action.description}")
        print(f"   Score: {iteration.feng_shui_score_before:.1f} → {iteration.feng_shui_score_after:.1f} ({delta_str})")
        print(f"   Reflection: {iteration.reflection}")
    
    def _print_session_report(self, report: SessionReport):
        """Print comprehensive session report"""
        print(f"\n{'='*70}")
        print(f"SESSION REPORT")
        print(f"{'='*70}")
        print(f"Goal: {report.goal_description}")
        print(f"Status: {report.completion_status}")
        print(f"\n[SCORES]")
        print(f"Initial:  {report.initial_score:.1f}/100")
        print(f"Final:    {report.final_score:.1f}/100")
        print(f"Change:   {'+' if report.improvement >= 0 else ''}{report.improvement:.1f} points")
        print(f"\n[EXECUTION]")
        print(f"Iterations:        {len(report.iterations)}")
        print(f"Successful Fixes:  {report.successful_fixes}")
        print(f"Failed Fixes:      {report.failed_fixes}")
        print(f"Strategy Switches: {report.strategy_switches}")
        print(f"Total Time:        {report.total_time_seconds:.1f}s")
        
        if report.insights_generated:
            print(f"\n[INSIGHTS]")
            for i, insight in enumerate(report.insights_generated, 1):
                print(f"{i}. {insight}")
        
        print(f"{'='*70}\n")


def main():
    """CLI entry point for autonomous improvement"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Feng Shui ReAct Agent')
    parser.add_argument('--goal', type=str, default='Improve Feng Shui score',
                       help='Goal description')
    parser.add_argument('--target-score', type=float, default=95.0,
                       help='Target Feng Shui score (0-100)')
    parser.add_argument('--max-iterations', type=int, default=10,
                       help='Maximum iterations')
    parser.add_argument('--modules', type=str, nargs='*',
                       help='Specific modules to improve')
    parser.add_argument('--no-reflection', action='store_true',
                       help='Disable meta-learning')
    parser.add_argument('--quiet', action='store_true',
                       help='Minimal output')
    
    args = parser.parse_args()
    
    # Run agent
    agent = FengShuiReActAgent(
        verbose=not args.quiet,
        enable_reflection=not args.no_reflection
    )
    
    report = agent.run_autonomous_session(
        goal_description=args.goal,
        target_score=args.target_score,
        max_iterations=args.max_iterations,
        target_modules=args.modules
    )
    
    # Exit code based on completion
    if report.completion_status == 'GOAL_ACHIEVED':
        sys.exit(0)
    elif report.completion_status == 'STUCK':
        sys.exit(2)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()