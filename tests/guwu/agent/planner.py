"""
Gu Wu Agent Planner - Hierarchical Goal Decomposition

Implements planning pattern for breaking down complex testing goals
into manageable sub-goals with dependency tracking.

Philosophy: Complex goals need structured breakdown before execution.
Like a general planning a campaign before battle.
"""

import sys
import os
from datetime import datetime
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


class GoalStatus(Enum):
    """Status of a goal in the plan"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class GoalPriority(Enum):
    """Priority levels for goals"""
    CRITICAL = 1  # Must complete for success
    HIGH = 2      # Important but not blocking
    MEDIUM = 3    # Nice to have
    LOW = 4       # Optional optimization


@dataclass
class SubGoal:
    """
    Individual sub-goal in a plan
    
    Represents an atomic, achievable step toward the main goal
    """
    id: str
    description: str
    priority: GoalPriority
    estimated_duration: float  # seconds
    dependencies: List[str] = field(default_factory=list)  # IDs of prerequisite sub-goals
    status: GoalStatus = GoalStatus.PENDING
    action: str = ""  # Action to execute for this sub-goal
    result: Optional[Dict] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'description': self.description,
            'priority': self.priority.value,
            'estimated_duration': self.estimated_duration,
            'dependencies': self.dependencies,
            'status': self.status.value,
            'action': self.action,
            'result': self.result,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }


@dataclass
class ExecutionPlan:
    """
    Complete execution plan for a complex goal
    
    Contains:
    - Hierarchical sub-goals
    - Dependency graph
    - Execution order
    - Progress tracking
    """
    goal: str
    sub_goals: List[SubGoal]
    created_at: datetime
    total_estimated_duration: float
    
    def to_dict(self) -> Dict:
        return {
            'goal': self.goal,
            'sub_goals': [sg.to_dict() for sg in self.sub_goals],
            'created_at': self.created_at.isoformat(),
            'total_estimated_duration': self.total_estimated_duration,
            'progress_percentage': self.get_progress_percentage()
        }
    
    def get_progress_percentage(self) -> float:
        """Calculate completion percentage"""
        if not self.sub_goals:
            return 0.0
        
        completed = sum(1 for sg in self.sub_goals if sg.status == GoalStatus.COMPLETED)
        return (completed / len(self.sub_goals)) * 100.0
    
    def get_next_goals(self) -> List[SubGoal]:
        """
        Get next sub-goals that can be executed
        
        Returns goals that:
        - Are PENDING
        - Have all dependencies COMPLETED
        """
        completed_ids = {sg.id for sg in self.sub_goals if sg.status == GoalStatus.COMPLETED}
        
        ready_goals = []
        for sg in self.sub_goals:
            if sg.status == GoalStatus.PENDING:
                # Check if all dependencies are completed
                if all(dep_id in completed_ids for dep_id in sg.dependencies):
                    ready_goals.append(sg)
        
        # Sort by priority
        ready_goals.sort(key=lambda g: g.priority.value)
        return ready_goals
    
    def is_blocked(self) -> bool:
        """Check if plan is blocked (circular dependencies or failed critical goals)"""
        # Check for failed critical goals
        for sg in self.sub_goals:
            if sg.status == GoalStatus.FAILED and sg.priority == GoalPriority.CRITICAL:
                return True
        
        # Check if any pending goals with no ready dependencies
        pending = [sg for sg in self.sub_goals if sg.status == GoalStatus.PENDING]
        if pending and not self.get_next_goals():
            return True
        
        return False


class GoalPlanner:
    """
    Hierarchical goal planner for complex testing objectives
    
    Decomposes high-level goals into executable sub-goals with:
    - Dependency tracking
    - Priority assignment
    - Duration estimation
    - Parallel execution opportunities
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        self.plan_history: List[ExecutionPlan] = []
    
    def create_plan(self, goal: str, context: Optional[Dict] = None) -> ExecutionPlan:
        """
        Create execution plan for a goal
        
        Args:
            goal: High-level testing objective
            context: Current state information
        
        Returns:
            ExecutionPlan with sub-goals and dependencies
        """
        context = context or {}
        
        if self.verbose:
            self.logger.info(f"\n[Planner] Creating plan for: {goal}")
        
        # Analyze goal type and create appropriate plan
        sub_goals = self._decompose_goal(goal, context)
        
        # Calculate total estimated duration
        total_duration = sum(sg.estimated_duration for sg in sub_goals)
        
        plan = ExecutionPlan(
            goal=goal,
            sub_goals=sub_goals,
            created_at=datetime.now(),
            total_estimated_duration=total_duration
        )
        
        self.plan_history.append(plan)
        
        if self.verbose:
            self.logger.info(f"[Planner] Plan created: {len(sub_goals)} sub-goals, ~{total_duration:.1f}s estimated")
        
        return plan
    
    def _decompose_goal(self, goal: str, context: Dict) -> List[SubGoal]:
        """
        Decompose goal into sub-goals
        
        Strategies:
        - Coverage goals → analyze gaps → generate tests → verify
        - Flaky test goals → identify patterns → generate fixes → validate
        - Performance goals → profile → identify bottlenecks → optimize
        """
        goal_lower = goal.lower()
        
        if 'coverage' in goal_lower:
            return self._plan_coverage_goal(goal, context)
        elif 'flaky' in goal_lower:
            return self._plan_flaky_goal(goal, context)
        elif 'performance' in goal_lower or 'optimize' in goal_lower:
            return self._plan_performance_goal(goal, context)
        else:
            return self._plan_generic_goal(goal, context)
    
    def _plan_coverage_goal(self, goal: str, context: Dict) -> List[SubGoal]:
        """Plan for coverage improvement goals"""
        current_coverage = context.get('current_coverage', 0.0)
        target_coverage = self._extract_target_coverage(goal)
        
        sub_goals = []
        
        # Sub-goal 1: Analyze gaps (always first)
        sub_goals.append(SubGoal(
            id='cov_1_analyze',
            description='Analyze coverage gaps to identify untested code',
            priority=GoalPriority.CRITICAL,
            estimated_duration=5.0,
            dependencies=[],
            action='analyze_gaps'
        ))
        
        # Sub-goal 2: Generate tests for critical gaps
        sub_goals.append(SubGoal(
            id='cov_2_generate',
            description='Generate tests for critical coverage gaps',
            priority=GoalPriority.CRITICAL,
            estimated_duration=15.0,
            dependencies=['cov_1_analyze'],
            action='generate_critical_tests'
        ))
        
        # Sub-goal 3: Verify coverage improvement
        sub_goals.append(SubGoal(
            id='cov_3_verify',
            description=f'Verify coverage reached {target_coverage:.0%}',
            priority=GoalPriority.CRITICAL,
            estimated_duration=10.0,
            dependencies=['cov_2_generate'],
            action='verify_coverage'
        ))
        
        # Optional: Generate remaining tests (if gap is large)
        if target_coverage - current_coverage > 0.2:
            sub_goals.append(SubGoal(
                id='cov_4_complete',
                description='Generate tests for remaining gaps',
                priority=GoalPriority.HIGH,
                estimated_duration=20.0,
                dependencies=['cov_3_verify'],
                action='generate_targeted_tests'
            ))
        
        return sub_goals
    
    def _plan_flaky_goal(self, goal: str, context: Dict) -> List[SubGoal]:
        """Plan for flaky test remediation"""
        flaky_count = context.get('flaky_tests_count', 0)
        
        sub_goals = []
        
        # Sub-goal 1: Analyze flaky patterns
        sub_goals.append(SubGoal(
            id='flaky_1_analyze',
            description=f'Analyze patterns in {flaky_count} flaky tests',
            priority=GoalPriority.CRITICAL,
            estimated_duration=10.0,
            dependencies=[],
            action='analyze_flaky_patterns'
        ))
        
        # Sub-goal 2: Generate fixes
        sub_goals.append(SubGoal(
            id='flaky_2_fix',
            description='Generate fix suggestions for flaky tests',
            priority=GoalPriority.CRITICAL,
            estimated_duration=15.0,
            dependencies=['flaky_1_analyze'],
            action='generate_flaky_fixes'
        ))
        
        # Sub-goal 3: Validate fixes
        sub_goals.append(SubGoal(
            id='flaky_3_validate',
            description='Validate fixes reduce flakiness',
            priority=GoalPriority.HIGH,
            estimated_duration=20.0,
            dependencies=['flaky_2_fix'],
            action='validate_fixes'
        ))
        
        return sub_goals
    
    def _plan_performance_goal(self, goal: str, context: Dict) -> List[SubGoal]:
        """Plan for performance optimization"""
        sub_goals = []
        
        # Sub-goal 1: Identify bottlenecks
        sub_goals.append(SubGoal(
            id='perf_1_analyze',
            description='Analyze test suite performance bottlenecks',
            priority=GoalPriority.CRITICAL,
            estimated_duration=10.0,
            dependencies=[],
            action='analyze_performance_bottlenecks'
        ))
        
        # Sub-goal 2: Generate optimizations
        sub_goals.append(SubGoal(
            id='perf_2_optimize',
            description='Generate optimization suggestions',
            priority=GoalPriority.CRITICAL,
            estimated_duration=15.0,
            dependencies=['perf_1_analyze'],
            action='generate_optimizations'
        ))
        
        # Sub-goal 3: Verify improvements
        sub_goals.append(SubGoal(
            id='perf_3_verify',
            description='Verify performance improvements',
            priority=GoalPriority.HIGH,
            estimated_duration=20.0,
            dependencies=['perf_2_optimize'],
            action='verify_performance'
        ))
        
        return sub_goals
    
    def _plan_generic_goal(self, goal: str, context: Dict) -> List[SubGoal]:
        """Plan for generic/custom goals"""
        # Simple 3-step plan for unknown goals
        return [
            SubGoal(
                id='gen_1_analyze',
                description='Analyze current state',
                priority=GoalPriority.CRITICAL,
                estimated_duration=5.0,
                dependencies=[],
                action='analyze_situation'
            ),
            SubGoal(
                id='gen_2_execute',
                description='Execute main action',
                priority=GoalPriority.CRITICAL,
                estimated_duration=10.0,
                dependencies=['gen_1_analyze'],
                action='execute_action'
            ),
            SubGoal(
                id='gen_3_verify',
                description='Verify goal achieved',
                priority=GoalPriority.HIGH,
                estimated_duration=5.0,
                dependencies=['gen_2_execute'],
                action='verify_completion'
            )
        ]
    
    def _extract_target_coverage(self, goal: str) -> float:
        """Extract target coverage from goal string"""
        import re
        match = re.search(r'(\d+)%', goal)
        if match:
            return float(match.group(1)) / 100.0
        return 0.9  # Default 90%
    
    def visualize_plan(self, plan: ExecutionPlan) -> str:
        """
        Create ASCII visualization of plan
        
        Shows:
        - Sub-goals with status
        - Dependencies (arrows)
        - Critical path
        """
        lines = []
        lines.append("=" * 80)
        lines.append(f"EXECUTION PLAN: {plan.goal}")
        lines.append("=" * 80)
        lines.append(f"Created: {plan.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Total Estimated Duration: {plan.total_estimated_duration:.1f}s")
        lines.append(f"Progress: {plan.get_progress_percentage():.1f}%")
        lines.append("=" * 80)
        lines.append("")
        
        # Group by priority
        by_priority = {}
        for sg in plan.sub_goals:
            priority = sg.priority.name
            if priority not in by_priority:
                by_priority[priority] = []
            by_priority[priority].append(sg)
        
        # Display by priority
        for priority in [GoalPriority.CRITICAL, GoalPriority.HIGH, GoalPriority.MEDIUM, GoalPriority.LOW]:
            priority_name = priority.name
            if priority_name in by_priority:
                lines.append(f"\n[{priority_name} PRIORITY]")
                for sg in by_priority[priority_name]:
                    status_symbol = {
                        GoalStatus.PENDING: "[PENDING]",
                        GoalStatus.IN_PROGRESS: "[IN PROGRESS]",
                        GoalStatus.COMPLETED: "[DONE]",
                        GoalStatus.BLOCKED: "[BLOCKED]",
                        GoalStatus.FAILED: "[FAILED]"
                    }.get(sg.status, "[?]")
                    
                    lines.append(f"  {status_symbol} {sg.id}: {sg.description}")
                    if sg.dependencies:
                        lines.append(f"     Depends on: {', '.join(sg.dependencies)}")
                    lines.append(f"     Estimated: {sg.estimated_duration:.1f}s | Action: {sg.action}")
        
        lines.append("\n" + "=" * 80)
        return "\n".join(lines)


if __name__ == '__main__':
    # Example usage
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    planner = GoalPlanner(verbose=True)
    
    # Example 1: Coverage goal
    print("\nEXAMPLE 1: Coverage Goal")
    print("=" * 80)
    plan = planner.create_plan(
        goal="Achieve 90% coverage on knowledge_graph module",
        context={'current_coverage': 0.65}
    )
    print(planner.visualize_plan(plan))
    
    # Example 2: Flaky test goal
    print("\n\nEXAMPLE 2: Flaky Test Goal")
    print("=" * 80)
    plan = planner.create_plan(
        goal="Fix all flaky tests",
        context={'flaky_tests_count': 5}
    )
    print(planner.visualize_plan(plan))
    
    # Example 3: Get next executable goals
    print("\n\nEXAMPLE 3: Next Executable Goals")
    print("=" * 80)
    next_goals = plan.get_next_goals()
    print(f"Ready to execute: {len(next_goals)} goals")
    for sg in next_goals:
        print(f"  - {sg.id}: {sg.description}")