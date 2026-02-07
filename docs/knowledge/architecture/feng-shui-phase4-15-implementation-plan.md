# Feng Shui Phase 4.15: ReAct + Reflection Implementation Plan

**Status**: 📋 READY FOR IMPLEMENTATION  
**Created**: 2026-02-06  
**Estimated Effort**: 8-12 hours  
**Prerequisites**: All tests passing ✅ (19/19 for module_quality_gate.py)

---

## 🎯 Objective

Transform Feng Shui from sequential automation into an **autonomous architecture agent** with:
- **Goal-driven execution**: Iterates until target score achieved
- **Self-correction**: Switches strategies on failures
- **Meta-learning**: Learns from fix success rates over time
- **Reflection**: Improves decision-making continuously

---

## 📦 Deliverables

### Phase 4.15 Core Components (8 files)

**New Files**:
1. `tools/fengshui/react_agent.py` - ReAct Pattern agent (250-300 LOC)
2. `tools/fengshui/reflector.py` - Reflection meta-learning (200-250 LOC)
3. `tools/fengshui/state_analyzer.py` - Architecture state analysis (100-150 LOC)
4. `tools/fengshui/action_selector.py` - Action selection logic (80-100 LOC)
5. `tools/fengshui/strategy_manager.py` - Strategy switching (60-80 LOC)
6. `tests/unit/tools/test_react_agent.py` - Unit tests (200-250 LOC)
7. `tests/unit/tools/test_reflector.py` - Unit tests (150-200 LOC)
8. `tests/integration/test_fengshui_react_integration.py` - Integration tests (100-150 LOC)

**Modified Files**:
1. `tools/fengshui/automation_engine.py` - Add ReAct integration
2. `docs/knowledge/INDEX.md` - Add Phase 4.15 reference

**Documentation**:
1. `docs/knowledge/architecture/feng-shui-phase4-15-react-reflection.md` - Complete guide

---

## 🏗️ Implementation Steps

### Step 1: Database Schema for Reflection (30 min)

**File**: `tools/fengshui/reflection_schema.sql`

```sql
-- Reflection database for meta-learning
-- Location: tools/fengshui/reflection.db

CREATE TABLE IF NOT EXISTS fix_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    fix_type TEXT NOT NULL,
    module_name TEXT NOT NULL,
    strategy_used TEXT NOT NULL,
    predicted_success REAL NOT NULL,  -- 0.0-1.0
    actual_success INTEGER NOT NULL,   -- 0 or 1
    execution_time_ms INTEGER NOT NULL,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS strategy_performance (
    strategy_name TEXT PRIMARY KEY,
    total_attempts INTEGER NOT NULL DEFAULT 0,
    success_count INTEGER NOT NULL DEFAULT 0,
    avg_execution_time_ms REAL NOT NULL DEFAULT 0.0,
    trend TEXT NOT NULL DEFAULT 'STABLE',  -- IMPROVING/STABLE/DECLINING
    last_updated TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reflection_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    insight_type TEXT NOT NULL,
    priority TEXT NOT NULL,  -- CRITICAL/HIGH/MEDIUM/LOW
    description TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'OPEN'  -- OPEN/ACKNOWLEDGED/RESOLVED
);

CREATE INDEX idx_fix_attempts_timestamp ON fix_attempts(timestamp);
CREATE INDEX idx_fix_attempts_module ON fix_attempts(module_name);
CREATE INDEX idx_fix_attempts_strategy ON fix_attempts(strategy_used);
CREATE INDEX idx_insights_priority ON reflection_insights(priority);
```

### Step 2: Architecture State Analyzer (1 hour)

**File**: `tools/fengshui/state_analyzer.py`

```python
"""
Architecture State Analyzer for Feng Shui ReAct Agent

Analyzes current architecture state to inform agent decision-making.
"""

from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path
import json

@dataclass
class ViolationInfo:
    """Information about a specific violation"""
    type: str
    severity: str  # CRITICAL/HIGH/MEDIUM/LOW
    file_path: str
    line_number: int
    description: str

@dataclass
class ArchitectureState:
    """Current state of architecture"""
    feng_shui_score: float  # 0-100
    violations_by_type: Dict[str, List[ViolationInfo]]
    modules_affected: List[str]
    recent_fix_history: List[Dict]
    available_strategies: List[str]
    timestamp: str

class ArchitectureStateAnalyzer:
    """Analyze current architecture state for decision-making"""
    
    def __init__(self):
        self.quality_gate = None  # Will be injected
        
    def analyze_current_state(self, target_modules: List[str] = None) -> ArchitectureState:
        """
        Comprehensive state analysis
        
        Args:
            target_modules: Specific modules to analyze (None = all modules)
            
        Returns:
            ArchitectureState with complete analysis
        """
        # Implementation:
        # 1. Run quality gate on all/target modules
        # 2. Collect violations by type/severity
        # 3. Calculate overall Feng Shui score
        # 4. Load recent fix history from reflector
        # 5. Enumerate available strategies
        pass
    
    def calculate_feng_shui_score(self, violations: Dict) -> float:
        """
        Calculate overall Feng Shui score (0-100)
        
        Weighting:
        - CRITICAL violations: -20 points each
        - HIGH violations: -10 points each
        - MEDIUM violations: -5 points each
        - LOW violations: -2 points each
        
        Start from 100, deduct points, floor at 0
        """
        pass
    
    def categorize_violations(self, raw_violations: List) -> Dict[str, List[ViolationInfo]]:
        """Group violations by type for targeted fixing"""
        pass
    
    def identify_critical_path(self, violations: Dict) -> List[str]:
        """Identify which violations to fix first (critical path)"""
        pass
```

### Step 3: Action Selector (1 hour)

**File**: `tools/fengshui/action_selector.py`

```python
"""
Action Selector for Feng Shui ReAct Agent

Selects optimal action based on state and historical performance.
"""

from dataclasses import dataclass
from typing import List, Dict
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

class ActionSelector:
    """Select best action based on state and history"""
    
    def __init__(self, reflector=None):
        self.reflector = reflector
        
    def select_action(
        self,
        state: 'ArchitectureState',
        available_actions: List[Action],
        strategy_performance: Dict[str, float]
    ) -> Action:
        """
        Choose optimal action
        
        Selection criteria (weighted):
        1. Expected improvement: 40%
        2. Success rate: 30%
        3. Execution time: 20%
        4. Risk level: 10%
        
        Returns:
            Highest-scoring action
        """
        pass
    
    def score_action(self, action: Action, state: 'ArchitectureState') -> float:
        """Score an action (0.0-1.0) based on criteria"""
        pass
    
    def generate_available_actions(self, state: 'ArchitectureState') -> List[Action]:
        """Generate list of possible actions given current state"""
        pass
    
    def estimate_improvement(self, action: Action, state: 'ArchitectureState') -> float:
        """Estimate how much this action will improve Feng Shui score"""
        pass
```

### Step 4: Strategy Manager (45 min)

**File**: `tools/fengshui/strategy_manager.py`

```python
"""
Strategy Manager for Feng Shui ReAct Agent

Manages strategy selection and switching.
"""

from enum import Enum
from typing import Dict, List

class Strategy(Enum):
    """Available improvement strategies"""
    AGGRESSIVE = "aggressive"  # Fix all issues immediately
    CONSERVATIVE = "conservative"  # Fix one at a time, verify each
    TARGETED = "targeted"  # Fix only critical issues
    EXPERIMENTAL = "experimental"  # Try new approaches

class StrategyManager:
    """Manage and switch between improvement strategies"""
    
    def __init__(self):
        self.current_strategy = Strategy.CONSERVATIVE
        self.consecutive_failures = 0
        self.strategy_history = []
        
    def get_current_strategy(self) -> Strategy:
        """Get currently active strategy"""
        return self.current_strategy
    
    def should_switch_strategy(self, consecutive_failures: int) -> bool:
        """
        Determine if strategy should change
        
        Switch after 3 consecutive failures
        """
        return consecutive_failures >= 3
    
    def select_alternative_strategy(self) -> Strategy:
        """
        Choose alternative strategy
        
        Rotation: CONSERVATIVE → AGGRESSIVE → TARGETED → EXPERIMENTAL → CONSERVATIVE
        """
        pass
    
    def record_result(self, success: bool):
        """Record fix result and update failure counter"""
        if success:
            self.consecutive_failures = 0
        else:
            self.consecutive_failures += 1
            
    def get_strategy_config(self, strategy: Strategy) -> Dict:
        """Get configuration for specific strategy"""
        configs = {
            Strategy.CONSERVATIVE: {
                'batch_size': 1,
                'verify_each': True,
                'risk_tolerance': 'LOW'
            },
            Strategy.AGGRESSIVE: {
                'batch_size': 10,
                'verify_each': False,
                'risk_tolerance': 'HIGH'
            },
            # ... etc
        }
        return configs[strategy]
```

### Step 5: FengShuiReflector (2-3 hours)

**File**: `tools/fengshui/reflector.py`

```python
"""
Feng Shui Reflector - Meta-Learning Engine

Tracks fix attempts, analyzes patterns, generates insights.
Inspired by Gu Wu Phase 6 reflection capabilities.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class SuccessRateAnalysis:
    """Analysis of fix success rates"""
    fix_type: str
    total_attempts: int
    success_count: int
    success_rate: float
    predicted_rate: float
    calibration_error: float  # Difference between predicted and actual

@dataclass
class StrategyAnalysis:
    """Analysis of strategy performance over time"""
    strategy_name: str
    total_attempts: int
    success_rate: float
    avg_time_ms: float
    trend: str  # IMPROVING/STABLE/DECLINING

@dataclass
class CalibrationIssue:
    """Confidence calibration issue"""
    fix_type: str
    predicted_success: float
    actual_success: float
    error: float  # abs(predicted - actual)
    severity: str  # CRITICAL if error > 0.3, HIGH if > 0.15

@dataclass
class RecurringPattern:
    """Recurring violation pattern"""
    violation_type: str
    modules_affected: List[str]
    frequency: int
    recommendation: str

@dataclass
class ReflectionInsight:
    """Actionable insight from reflection"""
    priority: str  # CRITICAL/HIGH/MEDIUM/LOW
    category: str  # STRATEGY/CALIBRATION/PATTERN/PERFORMANCE
    description: str
    recommendation: str
    impact: str  # Expected impact if followed

class FengShuiReflector:
    """Meta-learning engine for Feng Shui self-improvement"""
    
    def __init__(self, db_path: Path = None):
        if db_path is None:
            db_path = Path(__file__).parent / 'reflection.db'
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with schema"""
        # Execute reflection_schema.sql
        pass
    
    def record_fix_attempt(
        self,
        fix_type: str,
        predicted_success: float,
        actual_success: bool,
        module_name: str,
        strategy_used: str,
        execution_time_ms: int = 0,
        error_message: str = None
    ):
        """
        Track each fix attempt for learning
        
        This is the core data collection mechanism
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO fix_attempts 
            (timestamp, fix_type, module_name, strategy_used, 
             predicted_success, actual_success, execution_time_ms, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            fix_type,
            module_name,
            strategy_used,
            predicted_success,
            1 if actual_success else 0,
            execution_time_ms,
            error_message
        ))
        
        conn.commit()
        conn.close()
        
        # Update strategy performance
        self._update_strategy_performance(strategy_used, actual_success, execution_time_ms)
    
    def analyze_fix_success_rates(self) -> Dict[str, SuccessRateAnalysis]:
        """
        Calculate actual vs predicted success rates
        
        Returns:
            Analysis showing calibration accuracy per fix type
        """
        # Query fix_attempts, group by fix_type
        # Calculate avg(predicted_success) vs avg(actual_success)
        # Identify calibration errors > 15%
        pass
    
    def analyze_strategy_performance(self) -> List[StrategyAnalysis]:
        """
        Track which strategies work best over time
        
        Returns:
            Strategies with IMPROVING/STABLE/DECLINING trends
        """
        # Query strategy_performance table
        # Calculate trend based on recent attempts
        # Compare current vs historical success rates
        pass
    
    def calibrate_confidence(self) -> List[CalibrationIssue]:
        """
        Detect confidence miscalibrations (>15% error)
        
        Returns:
            Issues requiring confidence adjustment
        """
        success_rates = self.analyze_fix_success_rates()
        issues = []
        
        for fix_type, analysis in success_rates.items():
            if analysis.calibration_error > 0.15:
                severity = 'CRITICAL' if analysis.calibration_error > 0.3 else 'HIGH'
                issues.append(CalibrationIssue(
                    fix_type=fix_type,
                    predicted_success=analysis.predicted_rate,
                    actual_success=analysis.success_rate,
                    error=analysis.calibration_error,
                    severity=severity
                ))
        
        return issues
    
    def recognize_patterns(self) -> List[RecurringPattern]:
        """
        Identify recurring violations across modules
        
        Returns:
            Patterns suggesting systemic issues
        """
        # Query fix_attempts for same violation_type across multiple modules
        # Identify patterns (e.g., DI violations in 5+ modules = systemic)
        pass
    
    def generate_insights(self) -> List[ReflectionInsight]:
        """
        Synthesize all analyses into actionable recommendations
        
        Returns:
            Prioritized insights (CRITICAL/HIGH/MEDIUM/LOW)
        """
        insights = []
        
        # 1. Check calibration issues
        calibration_issues = self.calibrate_confidence()
        for issue in calibration_issues:
            insights.append(ReflectionInsight(
                priority=issue.severity,
                category='CALIBRATION',
                description=f"Confidence miscalibration for {issue.fix_type}",
                recommendation=f"Adjust predicted success from {issue.predicted_success:.2f} to {issue.actual_success:.2f}",
                impact="Improved action selection accuracy"
            ))
        
        # 2. Check strategy performance
        strategies = self.analyze_strategy_performance()
        for strategy in strategies:
            if strategy.trend == 'DECLINING':
                insights.append(ReflectionInsight(
                    priority='HIGH',
                    category='STRATEGY',
                    description=f"Strategy '{strategy.strategy_name}' performance declining",
                    recommendation=f"Consider switching to alternative strategy",
                    impact="Improved fix success rate"
                ))
        
        # 3. Check recurring patterns
        patterns = self.recognize_patterns()
        for pattern in patterns:
            insights.append(ReflectionInsight(
                priority='MEDIUM',
                category='PATTERN',
                description=f"Recurring {pattern.violation_type} across {len(pattern.modules_affected)} modules",
                recommendation=pattern.recommendation,
                impact="Address systemic architectural issue"
            ))
        
        # Sort by priority
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        insights.sort(key=lambda x: priority_order[x.priority])
        
        return insights
    
    def _update_strategy_performance(self, strategy: str, success: bool, time_ms: int):
        """Update strategy performance metrics"""
        pass
```

### Step 6: FengShuiReActAgent (3-4 hours)

**File**: `tools/fengshui/react_agent.py`

```python
"""
Feng Shui ReAct Agent - Autonomous Architecture Improvement

Implements ReAct Pattern: Reason → Act → Observe → Reflect
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time
import logging

from .reflector import FengShuiReflector
from .state_analyzer import ArchitectureStateAnalyzer, ArchitectureState
from .action_selector import ActionSelector, Action
from .strategy_manager import StrategyManager, Strategy
from .automation_engine import FengShuiAutomationEngine

@dataclass
class SessionReport:
    """Report from autonomous session"""
    goal_achieved: bool
    initial_score: float
    final_score: float
    iterations: int
    actions_taken: List[Dict]
    strategy_switches: int
    total_time_seconds: float
    insights: List[str]

class FengShuiReActAgent:
    """
    Autonomous reasoning agent for architecture improvement
    
    Implements ReAct Pattern:
    - REASON: Analyze current state, select best action
    - ACT: Execute selected action (via existing automation_engine)
    - OBSERVE: Measure improvement, detect failures
    - REFLECT: Learn from results, adjust strategy
    """
    
    def __init__(self, automation_engine: FengShuiAutomationEngine = None):
        self.engine = automation_engine or FengShuiAutomationEngine()
        self.reflector = FengShuiReflector()
        self.state_analyzer = ArchitectureStateAnalyzer()
        self.action_selector = ActionSelector(self.reflector)
        self.strategy_manager = StrategyManager()
        self.logger = logging.getLogger(__name__)
        
    def run_autonomous_session(
        self, 
        goal: str,              # e.g., "Achieve score 95+"
        max_iterations: int = 10,
        timeout_minutes: int = 30,
        verbose: bool = True
    ) -> SessionReport:
        """
        Execute autonomous improvement loop
        
        Args:
            goal: Target to achieve (parsed for score threshold)
            max_iterations: Max iterations before stopping
            timeout_minutes: Max time before stopping
            verbose: Log detailed progress
            
        Returns:
            SessionReport with iterations, actions taken, final score
        """
        start_time = datetime.now()
        timeout = timedelta(minutes=timeout_minutes)
        
        # Parse goal
        target_score = self._parse_goal(goal)
        
        # Initial state
        state = self.state_analyzer.analyze_current_state()
        initial_score = state.feng_shui_score
        
        if verbose:
            self.logger.info(f"Starting autonomous session: goal={goal}, initial_score={initial_score:.1f}")
        
        actions_taken = []
        iterations = 0
        strategy_switches = 0
        
        # Main ReAct loop
        while iterations < max_iterations:
            # Check timeout
            if datetime.now() - start_time > timeout:
                self.logger.warning(f"Timeout reached after {iterations} iterations")
                break
            
            # Check goal achievement
            if state.feng_shui_score >= target_score:
                self.logger.info(f"Goal achieved! Score: {state.feng_shui_score:.1f} >= {target_score:.1f}")
                break
            
            iterations += 1
            if verbose:
                self.logger.info(f"\n=== Iteration {iterations}/{max_iterations} ===")
                self.logger.info(f"Current score: {state.feng_shui_score:.1f}")
            
            # REASON: Select next action
            action = self._reason_about_next_action(state)
            if verbose:
                self.logger.info(f"Selected action: {action.description}")
            
            # ACT: Execute action
            result = self._execute_action(action)
            actions_taken.append({
                'iteration': iterations,
                'action': action.description,
                'strategy': action.strategy,
                'success': result.success,
                'time_ms': result.execution_time_ms
            })
            
            # OBSERVE: Measure improvement
            new_state = self.state_analyzer.analyze_current_state()
            improvement = self._observe_improvement(state, new_state)
            if verbose:
                self.logger.info(f"Improvement: {improvement.score_delta:+.1f} points")
            
            # REFLECT: Learn from result
            self._reflect_and_adjust(improvement)
            
            # Check if strategy should switch
            if self.strategy_manager.should_switch_strategy(self.strategy_manager.consecutive_failures):
                old_strategy = self.strategy_manager.current_strategy
                self.strategy_manager.select_alternative_strategy()
                strategy_switches += 1
                if verbose:
                    self.logger.info(f"Strategy switched: {old_strategy.value} → {self.strategy_manager.current_strategy.value}")
            
            # Update state for next iteration
            state = new_state
            
            # Check for no improvement
            if improvement.score_delta <= 0 and self.strategy_manager.consecutive_failures >= 3:
                self.logger.warning("No improvement after 3 attempts, stopping")
                break
        
        # Generate final report
        final_score = state.feng_shui_score
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Get insights from reflector
        insights = self.reflector.generate_insights()
        
        return SessionReport(
            goal_achieved=(final_score >= target_score),
            initial_score=initial_score,
            final_score=final_score,
            iterations=iterations,
            actions_taken=actions_taken,
            strategy_switches=strategy_switches,
            total_time_seconds=total_time,
            insights=[f"{i.priority}: {i.description}" for i in insights[:5]]
        )
    
    def _parse_goal(self, goal: str) -> float:
        """Parse goal string to extract target score"""
        # Extract number from strings like "Achieve score 95+" or "score >= 90"
        import re
        match = re.search(r'(\d+)', goal)
        if match:
            return float(match.group(1))
        return 70.0  # Default threshold
    
    def _reason_about_next_action(self, state: ArchitectureState) -> Action:
        """
        Select best action based on current state
        
        Uses action selector with strategy performance data
        """
        # Get strategy performance from reflector
        strategy_performance = self._get_strategy_performance()
        
        # Generate available actions
        available_actions = self.action_selector.generate_available_actions(state)
        
        # Select best action
        action = self.action_selector.select_action(
            state,
            available_actions,
            strategy_performance
        )
        
        return action
    
    def _execute_action(self, action: Action) -> 'ActionResult':
        """Execute action via automation engine"""
        start_time = time.time()
        
        try:
            # Use existing automation_engine to apply fix
            success = self.engine.apply_fix(
                module=action.target_module,
                fix_type=action.type.value,
                strategy=action.strategy
            )
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            return ActionResult(
                success=success,
                execution_time_ms=execution_time_ms,
                error_message=None
            )
        
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            return ActionResult(
                success=False,
                execution_time_ms=execution_time_ms,
                error_message=str(e)
            )
    
    def _observe_improvement(self, before: ArchitectureState, after: ArchitectureState) -> 'Improvement':
        """Measure impact of action"""
        return Improvement(
            score_delta=after.feng_shui_score - before.feng_shui_score,
            violations_fixed=self._count_violations_fixed(before, after),
            new_violations=self._count_new_violations(before, after)
        )
    
    def _reflect_and_adjust(self, improvement: 'Improvement'):
        """Learn from result, update strategy if needed"""
        # Record result in reflector
        self.reflector.record_fix_attempt(
            fix_type=improvement.fix_type,
            predicted_success=improvement.predicted_success,
            actual_success=improvement.was_successful,
            module_name=improvement.module,
            strategy_used=self.strategy_manager.current_strategy.value,
            execution_time_ms=improvement.execution_time_ms
        )
        
        # Update strategy manager
        self.strategy_manager.record_result(improvement.was_successful)
    
    def _get_strategy_performance(self) -> Dict[str, float]:
        """Get strategy success rates from reflector"""
        strategies = self.reflector.analyze_strategy_performance()
        return {s.strategy_name: s.success_rate for s in strategies}
    
    def _count_violations_fixed(self, before: ArchitectureState, after: ArchitectureState) -> int:
        """Count violations that were fixed"""
        pass
    
    def _count_new_violations(self, before: ArchitectureState, after: ArchitectureState) -> int:
        """Count new violations introduced"""
        pass

@dataclass
class ActionResult:
    """Result of executing an action"""
    success: bool
    execution_time_ms: int
    error_message: Optional[str]

@dataclass
class Improvement:
    """Measured improvement from an action"""
    score_delta: float
    violations_fixed: int
    new_violations: int
    fix_type: str = ""
    predicted_success: float = 0.0
    was_successful: bool = False
    module: str = ""
    execution_time_ms: int = 0
```

### Step 7: Integration with Automation Engine (30 min)

**File**: `tools/fengshui/automation_engine.py` (modify existing)

```python
# Add ReAct integration

class FengShuiAutomationEngine:
    """Existing automation engine"""
    
    # ADD THIS METHOD:
    def run_with_react_agent(
        self,
        goal: str = "score >= 90",
        max_iterations: int = 10,
        timeout_minutes: int = 30
    ) -> 'SessionReport':
        """
        Run automation with ReAct agent (autonomous mode)
        
        This is the new entry point for autonomous operation
        """
        from .react_agent import FengShuiReActAgent
        
        agent = FengShuiReActAgent(automation_engine=self)
        report = agent.run_autonomous_session(
            goal=goal,
            max_iterations=max_iterations,
            timeout_minutes=timeout_minutes,
            verbose=True
        )
        
        return report
    
    # EXISTING METHODS REMAIN UNCHANGED
    def run_full_automation(self, auto_fix=False):
        """Existing sequential automation (backward compatible)"""
        pass
```

### Step 8: Unit Tests (2-3 hours)

**File**: `tests/unit/tools/test_react_agent.py`

```python
"""
Unit tests for FengShuiReActAgent
"""

import pytest
from unittest.mock import Mock, patch
from tools.fengshui.react_agent import FengShuiReActAgent
from tools.fengshui.state_analyzer import ArchitectureState

@pytest.mark.unit
def test_react_agent_goal_driven_execution():
    """Test agent stops when goal achieved"""
    # ARRANGE
    agent = FengShuiReActAgent()
    goal = "Achieve score 90+"
    
    # Mock state analyzer to show improvement
    with patch.object(agent.state_analyzer, 'analyze_current_state') as mock_analyze:
        mock_analyze.side_effect = [
            # Initial state
            ArchitectureState(feng_shui_score=85.0, ...),
            # After first action
            ArchitectureState(feng_shui_score=92.0, ...)
        ]
        
        # ACT
        report = agent.run_autonomous_session(goal, max_iterations=5)
        
        # ASSERT
        assert report.goal_achieved is True
        assert report.final_score >= 90.0
        assert report.iterations <= 2  # Should stop after reaching goal

@pytest.mark.unit
def test_react_agent_strategy_switching():
    """Test agent switches strategies on repeated failures"""
    # ARRANGE
    agent = FengShuiReActAgent()
    
    # Mock action results to fail 3 times
    with patch.object(agent, '_execute_action') as mock_execute:
        mock_execute.return_value = ActionResult(success=False, execution_time_ms=100, error_message="test")
        
        # ACT
        agent.strategy_manager.record_result(False)
        agent.strategy_manager.record_result(False)
        agent.strategy_manager.record_result(False)
        
        # ASSERT
        assert agent.strategy_manager.should_switch_strategy(3) is True

@pytest.mark.unit
def test_react_agent_timeout():
    """Test agent respects timeout"""
    # ARRANGE
    agent = FengShuiReActAgent()
    goal = "score >= 100"  # Unreachable goal
    
    # ACT
    report = agent.run_autonomous_session(goal, max_iterations=100, timeout_minutes=0.01)
    
    # ASSERT
    assert report.goal_achieved is False
    assert report.total_time_seconds < 5  # Should timeout quickly

# Add 10-15 more unit tests covering:
# - Action selection
# - Improvement measurement
# - Reflection integration
# - Edge cases (no violations, all fixes fail, etc.)
```

**File**: `tests/unit/tools/test_reflector.py`

```python
"""
Unit tests for FengShuiReflector
"""

import pytest
from tools.fengshui.reflector import FengShuiReflector

@pytest.mark.unit
def test_reflector_records_fix_attempt():
    """Test reflector stores fix attempts"""
    # ARRANGE
    reflector = FengShuiReflector()
    
    # ACT
    reflector.record_fix_attempt(
        fix_type="DI_VIOLATION",
        predicted_success=0.8,
        actual_success=True,
        module_name="test_module",
        strategy_used="conservative"
    )
    
    # ASSERT
    # Query database to verify record was created
    pass

@pytest.mark.unit
def test_reflector_detects_calibration_issues():
    """Test reflector identifies miscalibrations"""
    # ARRANGE
    reflector = FengShuiReflector()
    
    # Record several attempts with prediction errors
    for _ in range(10):
        reflector.record_fix_attempt(
            fix_type="BLUEPRINT",
            predicted_success=0.9,  # Over-confident
            actual_success=False,   # But failing
            module_name="test",
            strategy_used="aggressive"
        )
    
    # ACT
    issues = reflector.calibrate_confidence()
    
    # ASSERT
    assert len(issues) > 0
    assert issues[0].severity in ['CRITICAL', 'HIGH']
    assert issues[0].error > 0.15

# Add 10-12 more unit tests
```

### Step 9: Integration Tests (1 hour)

**File**: `tests/integration/test_fengshui_react_integration.py`

```python
"""
Integration tests for ReAct agent with real modules
"""

import pytest
from tools.fengshui.react_agent import FengShuiReActAgent

@pytest.mark.integration
def test_react_agent_full_session():
    """Test complete autonomous session on test module"""
    # ARRANGE
    agent = FengShuiReActAgent()
    
    # ACT
    report = agent.run_autonomous_session(
        goal="score >= 80",
        max_iterations=5
    )
    
    # ASSERT
    assert report.iterations > 0
    assert len(report.actions_taken) > 0
    assert report.final_score >= report.initial_score  # Should not regress

@pytest.mark.integration
def test_reflector_learning_over_time():
    """Test reflection improves over multiple sessions"""
    # ARRANGE
    agent = FengShuiReActAgent()
    
    # ACT - Run multiple sessions
    report1 = agent.run_autonomous_session(goal="score >= 75", max_iterations=3)
    report2 = agent.run_autonomous_session(goal="score >= 75", max_iterations=3)
    
    # ASSERT
    # Second session should be more efficient (fewer iterations or better success rate)
    pass
```

### Step 10: Documentation (1-2 hours)

**File**: `docs/knowledge/architecture/feng-shui-phase4-15-react-reflection.md`

Complete guide with:
- Architecture overview
- ReAct Pattern explanation
- Reflection Pattern explanation
- Usage examples
- API reference
- Troubleshooting
- Integration guide

---

## 🧪 Testing Strategy

### Unit Tests (Expected: 25+ tests)
- ReAct agent: 12-15 tests
- Reflector: 10-12 tests
- State analyzer: 3-4 tests
- Action selector: 3-4 tests
- Strategy manager: 2-3 tests

### Integration Tests (Expected: 3-5 tests)
- Full autonomous session
- Multi-iteration learning
- Strategy switching
- Real module improvement

### Success Criteria
- ✅ All unit tests passing (25+/25+)
- ✅ All integration tests passing (3+/3+)
- ✅ Agent achieves goal in < 10 iterations
- ✅ Reflector generates actionable insights
- ✅ Strategy switching works correctly

---

## 📊 Validation

### Manual Testing Checklist

**Test 1: Goal Achievement**
```bash
python -m tools.fengshui.react_agent --goal "score >= 95" --max-iterations 10
# Expected: Achieves 95+ score within 10 iterations
```

**Test 2: Strategy Switching**
```bash
python -m tools.fengshui.react_agent --goal "score >= 90" --force-failures 3
# Expected: Switches strategy after 3 consecutive failures
```

**Test 3: Reflection Analysis**
```bash
python -m tools.fengshui.reflector --analyze
# Expected: Generates insights with priorities (CRITICAL/HIGH/MEDIUM/LOW)
```

**Test 4: Integration with Automation Engine**
```python
from tools.fengshui.automation_engine import FengShuiAutomationEngine

engine = FengShuiAutomationEngine()
report = engine.run_with_react_agent(goal="score >= 90")

print(f"Goal achieved: {report.goal_achieved}")
print(f"Iterations: {report.iterations}")
print(f"Score: {report.initial_score:.1f} → {report.final_score:.1f}")
```

---

## 🔄 Backward Compatibility

**CRITICAL**: Existing workflows must continue to work

```python
# EXISTING USAGE (still works)
engine = FengShuiAutomationEngine()
engine.run_full_automation(auto_fix=True)  # Sequential mode

# NEW USAGE (opt-in)
engine.run_with_react_agent(goal="score >= 90")  # Autonomous mode
```

---

## 📝 Update Index

**Add to `docs/knowledge/INDEX.md`**:

```markdown
### Feng Shui Framework
- [[Feng Shui Phase 4.15 Implementation Plan]] - Detailed plan (this document)
- [[Feng Shui Phase 4.15 ReAct Reflection]] - Architecture guide (to be created)
- [[Agentic Workflow Patterns]] - Pattern reference
```

---

## 🚀 Next Session Checklist

Before starting implementation:
- [ ] Review this plan completely
- [ ] Ensure git state clean (commit pending changes)
- [ ] Create feature branch: `feature/feng-shui-phase4-15-react-reflection`
- [ ] Verify pytest environment working
- [ ] Check Gu Wu reflection code as reference (tools/guwu/agent/reflector.py)

During implementation:
- [ ] Follow TDD: Write tests first, then implementation
- [ ] Test continuously (run pytest after each component)
- [ ] Document as you build (don't defer)
- [ ] Commit frequently (after each working component)

After implementation:
- [ ] Run full test suite (all 25+ tests must pass)
- [ ] Manual validation (4 test scenarios above)
- [ ] Update PROJECT_TRACKER.md
- [ ] Tag: `v3.36-feng-shui-phase4-15-complete`

---

## ⏱️ Time Estimates

| Task | Estimated Time | Cumulative |
|------|---------------|------------|
| Step 1: Database schema | 30 min | 0.5h |
| Step 2: State analyzer | 1 hour | 1.5h |
| Step 3: Action selector | 1 hour | 2.5h |
| Step 4: Strategy manager | 45 min | 3.25h |
| Step 5: Reflector | 2-3 hours | 5.5-6.25h |
| Step 6: ReAct agent | 3-4 hours | 8.5-10.25h |
| Step 7: Integration | 30 min | 9-10.75h |
| Step 8: Unit tests | 2-3 hours | 11-13.75h |
| Step 9: Integration tests | 1 hour | 12-14.75h |
| Step 10: Documentation | 1-2 hours | 13-16.75h |
| **TOTAL** | **13-17 hours** | - |

**Note**: Original estimate was 8-12 hours. Revised to 13-17 hours for comprehensive testing + documentation.

---

## 🎓 Key Learnings from Gu Wu

**Patterns to Reuse**:
1. ✅ SQLite for metrics storage (proven reliable)
2. ✅ Reflection generates insights, not just data
3. ✅ Confidence calibration catches over/under-confidence
4. ✅ Pattern recognition finds systemic issues
5. ✅ Autonomous agent works without human intervention

**Avoid These Pitfalls**:
1. ❌ Don't make database schema too complex upfront
2. ❌ Don't skip integration tests (caught real issues in Gu Wu)
3. ❌ Don't defer documentation (hard to retrofit later)
4. ❌ Don't assume confidence predictions are accurate initially

---

## 🔮 Future Consideration: Gu Wu Reorganization

**Question from User**: Should Gu Wu move from `tools/guwu/` to `tools/guwu/`?

**Analysis**: **YES - Makes sense long-term** ✅

**Benefits**:
- ✅ Conceptual clarity: Both are meta-frameworks (dev tools), not production code
- ✅ Consistency: Both Feng Shui & Gu Wu in same location
- ✅ Industry standard: Testing frameworks typically in tools/
- ✅ Import clarity: `from tools.guwu.agent` (clearer intent)
- ✅ Reusability: Both frameworks portable as standalone tools

**Migration Effort**: 2-3 hours
- Move directory: `git mv tests/guwu tools/guwu`
- Update ~20 files with import refactoring
- Update pytest configuration (conftest.py, pytest.ini)
- Run full test suite to verify

**Recommended Timing**: 
- **After Phase 4.15 Complete** (when both have ReAct/Reflection)
- Could be standalone "Phase 4.18: Framework Reorganization"
- Or combined with Phase 4.16 (Planning pattern)

**Rationale**: User correctly identified that both are development tools, not production code. Current location (`tools/guwu/`) is misleading since Gu Wu is a testing framework, not tests themselves. Similar to how pytest lives in site-packages, not in tests/.

**Decision**: Document for future, implement after Phase 4.15 complete

---

**Status**: 📋 PLAN COMPLETE - Ready for implementation in next session with full context

**Created**: 2026-02-06  
**Author**: AI Assistant (Cline)  
**Next Steps**: Review plan → Start fresh session → Implement Phase 4.15
