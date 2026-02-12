# Gu Wu Phase 4: Agentic & GoF Pattern Integration

**Version**: 4.0 (Phase 4)  
**Status**: Design Complete → Implementation Ready  
**Date**: February 6, 2026  
**Dependencies**: Phase 3 AI Capabilities  
**Estimated Time**: 20-25 hours

---

## 🎯 Vision

Transform Gu Wu from autonomous AI system → **intelligent, maintainable, self-improving test framework** through strategic application of:
- **Agentic Patterns**: Intelligence, autonomy, learning
- **GoF Design Patterns**: Flexibility, maintainability, scalability

**Philosophy**: "Tests that think, adapt, and evolve themselves"

---

## 📊 Current Architecture Analysis

### What Works ✅
- Metrics collection (SQLite)
- Flaky test detection
- Test prioritization
- Gap analysis
- Auto-fix generation
- Self-reflection

### What Needs Improvement 🔴
- **Isolated components** → Need coordination
- **Hardwired logic** → Need pluggable strategies
- **Batch processing** → Need real-time reactions
- **Manual workflows** → Need autonomous orchestration
- **Monolithic** → Need specialized agents

---

## 🚀 Work Package Breakdown

### WP-GW-001: Strategy Pattern for Test Analysis (3-4 hours)

**Goal**: Make test analyzers pluggable and extensible

**Current Problem**:
```python
# Hardwired analysis in metrics.py
class GuWuMetrics:
    def analyze_flakiness(self):
        # Hardwired algorithm
        score = (transitions / total_runs) * severity
        return score
    
    def analyze_performance(self):
        # Another hardwired algorithm
        if duration > threshold:
            return 'slow'
```

**Solution with Strategy Pattern**:
```python
# 1. Define strategy interface
class TestAnalysisStrategy(ABC):
    """Base strategy for test analysis"""
    
    @abstractmethod
    def analyze(self, test_data: Dict) -> AnalysisResult:
        """Analyze test data and return result"""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return strategy identifier"""
        pass

# 2. Concrete strategies
class FlakynessAnalysisStrategy(TestAnalysisStrategy):
    """Transition-based flaky detection"""
    
    def __init__(self, sensitivity: float = 1.0):
        self.sensitivity = sensitivity
    
    def analyze(self, test_data: Dict) -> AnalysisResult:
        transitions = self._count_transitions(test_data['history'])
        total_runs = len(test_data['history'])
        
        score = (transitions / total_runs) * self.sensitivity
        
        return AnalysisResult(
            strategy='flakiness',
            score=score,
            confidence=self._calculate_confidence(total_runs),
            recommendations=self._generate_recommendations(score)
        )
    
    def get_strategy_name(self) -> str:
        return 'flakiness_transition_based'

class PerformanceAnalysisStrategy(TestAnalysisStrategy):
    """Performance-based test analysis"""
    
    def __init__(self, threshold: float = 5.0):
        self.threshold = threshold
    
    def analyze(self, test_data: Dict) -> AnalysisResult:
        avg_duration = statistics.mean(test_data['durations'])
        
        if avg_duration > self.threshold:
            severity = 'high' if avg_duration > self.threshold * 2 else 'medium'
        else:
            severity = 'low'
        
        return AnalysisResult(
            strategy='performance',
            severity=severity,
            avg_duration=avg_duration,
            recommendations=self._suggest_optimizations(avg_duration)
        )
    
    def get_strategy_name(self) -> str:
        return 'performance_threshold_based'

class CoverageAnalysisStrategy(TestAnalysisStrategy):
    """Coverage-based analysis"""
    
    def analyze(self, test_data: Dict) -> AnalysisResult:
        coverage_pct = test_data['coverage_percentage']
        lines_covered = test_data['lines_covered']
        total_lines = test_data['total_lines']
        
        if coverage_pct < 50:
            priority = 'critical'
        elif coverage_pct < 70:
            priority = 'high'
        else:
            priority = 'medium'
        
        return AnalysisResult(
            strategy='coverage',
            coverage_pct=coverage_pct,
            priority=priority,
            gap_lines=total_lines - lines_covered
        )
    
    def get_strategy_name(self) -> str:
        return 'coverage_gap_analysis'

# 3. Context uses strategies
class GuWuAnalyzer:
    """Strategy-based test analyzer"""
    
    def __init__(self, strategy: TestAnalysisStrategy):
        self.strategy = strategy
        self.strategy_history = []
    
    def set_strategy(self, strategy: TestAnalysisStrategy):
        """Change analysis strategy at runtime"""
        self.strategy = strategy
    
    def analyze(self, test_data: Dict) -> AnalysisResult:
        """Run analysis using current strategy"""
        result = self.strategy.analyze(test_data)
        
        # Track which strategy was used
        self.strategy_history.append({
            'strategy': self.strategy.get_strategy_name(),
            'timestamp': datetime.now(),
            'result': result
        })
        
        return result
    
    def analyze_with_multiple_strategies(self, 
                                        test_data: Dict,
                                        strategies: List[TestAnalysisStrategy]) -> List[AnalysisResult]:
        """Run multiple strategies and aggregate results"""
        results = []
        for strategy in strategies:
            self.set_strategy(strategy)
            results.append(self.analyze(test_data))
        return results

# 4. Usage examples
# Example 1: Single strategy
analyzer = GuWuAnalyzer(FlakynessAnalysisStrategy())
result = analyzer.analyze(test_data)

# Example 2: Swap strategies
analyzer.set_strategy(PerformanceAnalysisStrategy(threshold=3.0))
result = analyzer.analyze(test_data)

# Example 3: Multiple strategies
results = analyzer.analyze_with_multiple_strategies(
    test_data,
    strategies=[
        FlakynessAnalysisStrategy(),
        PerformanceAnalysisStrategy(),
        CoverageAnalysisStrategy()
    ]
)

# Example 4: Custom strategy
class CustomMLBasedStrategy(TestAnalysisStrategy):
    def analyze(self, test_data):
        # Your ML model here
        prediction = self.ml_model.predict(test_data)
        return AnalysisResult(strategy='ml_based', prediction=prediction)

analyzer.set_strategy(CustomMLBasedStrategy())
result = analyzer.analyze(test_data)
```

**Implementation Steps**:
1. Create `tools/guwu/strategies/` directory
2. Implement `TestAnalysisStrategy` base class
3. Refactor existing analyzers to concrete strategies
4. Update `metrics.py` to use strategy pattern
5. Write unit tests for each strategy
6. Update documentation

**Benefits**:
- ✅ Easy to add new analysis types (just implement interface)
- ✅ Swap algorithms at runtime (A/B testing)
- ✅ Test strategies independently
- ✅ Mix and match strategies
- ✅ No modification to core code

**Files to Create/Modify**:
- `tools/guwu/strategies/__init__.py` (NEW)
- `tools/guwu/strategies/base.py` (NEW)
- `tools/guwu/strategies/flakiness.py` (NEW)
- `tools/guwu/strategies/performance.py` (NEW)
- `tools/guwu/strategies/coverage.py` (NEW)
- `tools/guwu/metrics.py` (REFACTOR)
- `tests/unit/guwu/test_strategies.py` (NEW)

**Success Criteria**:
- ✅ All existing analysis works with new pattern
- ✅ Can add new strategy without modifying core
- ✅ Can swap strategies at runtime
- ✅ 100% test coverage for strategies

---

### WP-GW-002: Observer Pattern for Real-Time Insights (4-5 hours)

**Goal**: Event-driven test insights instead of batch processing

**Current Problem**:
```python
# Batch processing - insights generated on demand
def generate_insights():
    conn = sqlite3.connect(db_path)
    results = conn.execute("SELECT * FROM test_runs WHERE ...").fetchall()
    # Process all at once
    insights = []
    for result in results:
        if is_flaky(result):
            insights.append(create_flaky_insight(result))
    return insights
```

**Solution with Observer Pattern**:
```python
# 1. Event bus for test events
class TestEventBus:
    """Pub/sub for test events"""
    
    def __init__(self):
        self._observers: Dict[str, List[TestObserver]] = {}
        self._event_history = []
    
    def subscribe(self, event_type: str, observer: 'TestObserver'):
        """Subscribe observer to event type"""
        if event_type not in self._observers:
            self._observers[event_type] = []
        self._observers[event_type].append(observer)
    
    def publish(self, event: TestEvent):
        """Publish event to all subscribers"""
        self._event_history.append(event)
        
        # Notify specific event type observers
        if event.type in self._observers:
            for observer in self._observers[event.type]:
                try:
                    observer.on_event(event)
                except Exception as e:
                    logging.error(f"Observer {observer} failed: {e}")
        
        # Notify wildcard observers (subscribed to '*')
        if '*' in self._observers:
            for observer in self._observers['*']:
                try:
                    observer.on_event(event)
                except Exception as e:
                    logging.error(f"Wildcard observer {observer} failed: {e}")
    
    def get_event_history(self, event_type: str = None, limit: int = 100):
        """Get recent events"""
        if event_type:
            return [e for e in self._event_history if e.type == event_type][-limit:]
        return self._event_history[-limit:]

# 2. Event types
@dataclass
class TestEvent:
    """Base test event"""
    type: str
    timestamp: datetime
    test_id: str
    data: Dict

class TestFailedEvent(TestEvent):
    def __init__(self, test_id: str, error: str, traceback: str):
        super().__init__(
            type='test_failed',
            timestamp=datetime.now(),
            test_id=test_id,
            data={'error': error, 'traceback': traceback}
        )

class TestPassedEvent(TestEvent):
    def __init__(self, test_id: str, duration: float):
        super().__init__(
            type='test_passed',
            timestamp=datetime.now(),
            test_id=test_id,
            data={'duration': duration}
        )

class TestSkippedEvent(TestEvent):
    def __init__(self, test_id: str, reason: str):
        super().__init__(
            type='test_skipped',
            timestamp=datetime.now(),
            test_id=test_id,
            data={'reason': reason}
        )

# 3. Observer interface
class TestObserver(ABC):
    """Base observer for test events"""
    
    @abstractmethod
    def on_event(self, event: TestEvent):
        """React to test event"""
        pass
    
    def get_observer_name(self) -> str:
        """Return observer identifier"""
        return self.__class__.__name__

# 4. Concrete observers
class FlakyTestDetector(TestObserver):
    """Detects flaky tests in real-time"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.recent_failures = {}  # test_id -> list of outcomes
    
    def on_event(self, event: TestEvent):
        """Track test outcomes and detect flakiness"""
        if event.type in ['test_failed', 'test_passed']:
            test_id = event.test_id
            outcome = 'failed' if event.type == 'test_failed' else 'passed'
            
            # Track recent outcomes
            if test_id not in self.recent_failures:
                self.recent_failures[test_id] = []
            self.recent_failures[test_id].append(outcome)
            
            # Keep last 10 outcomes
            self.recent_failures[test_id] = self.recent_failures[test_id][-10:]
            
            # Check for flakiness pattern (alternating pass/fail)
            if self._is_flaky_pattern(self.recent_failures[test_id]):
                self._create_flaky_alert(test_id)
    
    def _is_flaky_pattern(self, outcomes: List[str]) -> bool:
        """Detect flaky pattern"""
        if len(outcomes) < 4:
            return False
        
        # Count transitions
        transitions = sum(
            1 for i in range(len(outcomes) - 1)
            if outcomes[i] != outcomes[i + 1]
        )
        
        # Flaky if >30% transitions
        return (transitions / len(outcomes)) > 0.3
    
    def _create_flaky_alert(self, test_id: str):
        """Create alert for flaky test"""
        logging.warning(f"FLAKY TEST DETECTED: {test_id}")
        # Could also publish a FlakynessDetectedEvent here

class AutoFixGenerator(TestObserver):
    """Generates fixes for test failures in real-time"""
    
    def __init__(self):
        self.fix_patterns = self._load_fix_patterns()
    
    def on_event(self, event: TestEvent):
        """Generate fix when test fails"""
        if event.type == 'test_failed':
            error = event.data['error']
            fix = self._generate_fix(error)
            
            if fix:
                logging.info(f"AUTO-FIX AVAILABLE for {event.test_id}: {fix}")
                self._save_fix_suggestion(event.test_id, fix)
    
    def _generate_fix(self, error: str) -> Optional[str]:
        """Match error to fix pattern"""
        for pattern, fix_template in self.fix_patterns.items():
            if pattern in error:
                return fix_template
        return None

class MetricsCollector(TestObserver):
    """Collects metrics for all test events"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def on_event(self, event: TestEvent):
        """Record every event to database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT INTO test_events (type, test_id, timestamp, data)
            VALUES (?, ?, ?, ?)
        ''', (event.type, event.test_id, event.timestamp, json.dumps(event.data)))
        conn.commit()
        conn.close()

class PerformanceMonitor(TestObserver):
    """Monitors test performance in real-time"""
    
    def __init__(self, slow_threshold: float = 5.0):
        self.slow_threshold = slow_threshold
    
    def on_event(self, event: TestEvent):
        """Alert on slow tests"""
        if event.type == 'test_passed':
            duration = event.data.get('duration', 0)
            if duration > self.slow_threshold:
                logging.warning(
                    f"SLOW TEST: {event.test_id} took {duration:.2f}s "
                    f"(threshold: {self.slow_threshold}s)"
                )

# 5. Integration with pytest
class GuWuPytestPlugin:
    """Pytest plugin that publishes events"""
    
    def __init__(self):
        self.event_bus = TestEventBus()
        self._setup_observers()
    
    def _setup_observers(self):
        """Subscribe all observers"""
        self.event_bus.subscribe('test_failed', FlakyTestDetector(DB_PATH))
        self.event_bus.subscribe('test_failed', AutoFixGenerator())
        self.event_bus.subscribe('*', MetricsCollector(DB_PATH))
        self.event_bus.subscribe('test_passed', PerformanceMonitor())
    
    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_protocol(self, item, nextitem):
        """Hook into pytest execution"""
        start_time = time.time()
        outcome = yield
        duration = time.time() - start_time
        
        # Publish events based on outcome
        if outcome.excinfo is not None:
            self.event_bus.publish(TestFailedEvent(
                test_id=item.nodeid,
                error=str(outcome.excinfo.value),
                traceback=str(outcome.excinfo.traceback)
            ))
        else:
            self.event_bus.publish(TestPassedEvent(
                test_id=item.nodeid,
                duration=duration
            ))

# 6. Usage in conftest.py
def pytest_configure(config):
    """Register Gu Wu plugin"""
    config.pluginmanager.register(GuWuPytestPlugin())
```

**Implementation Steps**:
1. Create `tools/guwu/events/` directory
2. Implement `TestEventBus` and `TestEvent` classes
3. Create concrete observers (FlakyTestDetector, AutoFixGenerator, etc.)
4. Integrate with pytest via plugin
5. Update `conftest.py` to register plugin
6. Write unit tests for event system
7. Update documentation

**Benefits**:
- ✅ Real-time insights (not batch)
- ✅ Decoupled components (observers independent)
- ✅ Easy to add new observers
- ✅ Event history for debugging
- ✅ Parallel processing possible

**Files to Create/Modify**:
- `tools/guwu/events/__init__.py` (NEW)
- `tools/guwu/events/bus.py` (NEW)
- `tools/guwu/events/observers.py` (NEW)
- `tools/guwu/pytest_plugin.py` (NEW)
- `tests/conftest.py` (MODIFY)
- `tests/unit/guwu/test_event_system.py` (NEW)

**Success Criteria**:
- ✅ Events published for all test outcomes
- ✅ Observers react in real-time
- ✅ No performance degradation (<5% overhead)
- ✅ Event history persisted

---

### WP-GW-003: Decorator Pattern for Composable Test Runner (3-4 hours)

**Goal**: Add capabilities to test runner without modifying core

**Current Problem**:
```python
# Monolithic test runner - hard to extend
class TestRunner:
    def run_tests(self, tests):
        # Collect metrics
        start = time.time()
        
        # Run predictions
        predictions = predict_failures(tests)
        
        # Execute tests
        for test in tests:
            test.execute()
        
        # Generate insights
        duration = time.time() - start
        generate_insights()
        
        return results
```

**Solution with Decorator Pattern**:
```python
# 1. Base component
class TestRunner(ABC):
    """Base test runner interface"""
    
    @abstractmethod
    def run(self, tests: List[str]) -> TestResults:
        """Run tests and return results"""
        pass

class BasicTestRunner(TestRunner):
    """Core test execution (no enhancements)"""
    
    def run(self, tests: List[str]) -> TestResults:
        """Simple pytest execution"""
        results = []
        for test in tests:
            result = pytest.main([test, '-v'])
            results.append(result)
        
        return TestResults(
            total=len(tests),
            passed=sum(1 for r in results if r == 0),
            failed=sum(1 for r in results if r != 0)
        )

# 2. Decorator base
class TestRunnerDecorator(TestRunner):
    """Base decorator for test runner"""
    
    def __init__(self, runner: TestRunner):
        self._runner = runner
    
    def run(self, tests: List[str]) -> TestResults:
        """Delegates to wrapped runner"""
        return self._runner.run(tests)

# 3. Concrete decorators
class PredictiveTestRunner(TestRunnerDecorator):
    """Adds failure prediction before running"""
    
    def __init__(self, runner: TestRunner, predictor: FailurePredictor):
        super().__init__(runner)
        self.predictor = predictor
    
    def run(self, tests: List[str]) -> TestResults:
        logging.info("[Gu Wu] Running failure prediction...")
        
        # BEFORE: Predict failures
        predictions = self.predictor.predict_failures(tests)
        high_risk = [p.test_id for p in predictions if p.probability > 0.7]
        
        # Sort tests by risk (high-risk first)
        sorted_tests = high_risk + [t for t in tests if t not in high_risk]
        
        logging.info(f"[Gu Wu] {len(high_risk)} high-risk tests will run first")
        
        # Delegate to wrapped runner
        results = self._runner.run(sorted_tests)
        
        # AFTER: Store prediction accuracy
        actual_failures = results.failed_tests
        accuracy = self._calculate_accuracy(predictions, actual_failures)
        logging.info(f"[Gu Wu] Prediction accuracy: {accuracy:.1%}")
        
        return results

class MetricsCollectingTestRunner(TestRunnerDecorator):
    """Adds metrics collection"""
    
    def __init__(self, runner: TestRunner, db_path: str):
        super().__init__(runner)
        self.db_path = db_path
    
    def run(self, tests: List[str]) -> TestResults:
        logging.info("[Gu Wu] Collecting metrics...")
        
        # BEFORE: Start metrics
        session_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Delegate
        results = self._runner.run(tests)
        
        # AFTER: Save metrics
        duration = time.time() - start_time
        self._save_metrics(session_id, results, duration)
        
        return results

class InsightGeneratingTestRunner(TestRunnerDecorator):
    """Generates insights after test run"""
    
    def run(self, tests: List[str]) -> TestResults:
        # Delegate
        results = self._runner.run(tests)
        
        # AFTER: Generate insights
        logging.info("[Gu Wu] Generating insights...")
        insights = self._generate_insights(results)
        results.insights = insights
        
        return results

class ParallelTestRunner(TestRunnerDecorator):
    """Runs tests in parallel"""
    
    def __init__(self, runner: TestRunner, workers: int = 4):
        super().__init__(runner)
        self.workers = workers
    
    def run(self, tests: List[str]) -> TestResults:
        logging.info(f"[Gu Wu] Running {len(tests)} tests with {self.workers} workers")
        
        # Use pytest-xdist for parallel execution
        pytest.main(tests + [f'-n{self.workers}'])
        
        # Note: Could delegate to wrapped runner for compatibility
        return self._runner.run(tests)

class CoverageTrackingTestRunner(TestRunnerDecorator):
    """Tracks code coverage"""
    
    def run(self, tests: List[str]) -> TestResults:
        logging.info("[Gu Wu] Tracking coverage...")
        
        # Run with coverage
        pytest.main(tests + ['--cov=modules', '--cov=core'])
        
        results = self._runner.run(tests)
        
        # Parse coverage report
        coverage_data = self._parse_coverage()
        results.coverage = coverage_data
        
        return results

# 4. Usage - Stack decorators for different scenarios
# Scenario 1: Development (fast, basic)
runner = BasicTestRunner()
results = runner.run(tests)

# Scenario 2: Development with prediction
runner = BasicTestRunner()
runner = PredictiveTestRunner(runner, predictor)
results = runner.run(tests)

# Scenario 3: CI/CD (full capabilities)
runner = BasicTestRunner()
runner = PredictiveTestRunner(runner, predictor)
runner = MetricsCollectingTestRunner(runner, db_path)
runner = InsightGeneratingTestRunner(runner)
runner = CoverageTrackingTestRunner(runner)
runner = ParallelTestRunner(runner, workers=4)
results = runner.run(tests)

# Scenario 4: Quick run (parallel only)
runner = BasicTestRunner()
runner = ParallelTestRunner(runner, workers=8)
results = runner.run(tests)

# Scenario 5: Custom combination
runner = BasicTestRunner()
runner = CoverageTrackingTestRunner(runner)
runner = InsightGeneratingTestRunner(runner)
results = runner.run(tests)
```

**Implementation Steps**:
1. Create `tools/guwu/runners/` directory
2. Implement `TestRunner` base class + `BasicTestRunner`
3. Implement `TestRunnerDecorator` base
4. Create concrete decorators (Predictive, Metrics, Insights, Parallel, Coverage)
5. Update pytest integration
6. Write unit tests for each decorator
7. Create runner factory for common scenarios
8. Update documentation

**Benefits**:
- ✅ Composable capabilities (mix and match)
- ✅ No core modification needed
- ✅ Easy to add new decorators
- ✅ Different configurations for different scenarios
- ✅ Open/Closed Principle (open for extension, closed for modification)

**Files to Create/Modify**:
- `tools/guwu/runners/__init__.py` (NEW)
- `tools/guwu/runners/base.py` (NEW)
- `tools/guwu/runners/decorators.py` (NEW)
- `tools/guwu/runners/factory.py` (NEW)
- `tests/conftest.py` (MODIFY)
- `tests/unit/guwu/test_runners.py` (NEW)

**Success Criteria**:
- ✅ Can stack decorators in any order
- ✅ Each decorator works independently
- ✅ No performance degradation when not decorated
- ✅ 100% test coverage for decorators

**Estimated Time**: 3-4 hours

---

### WP-GW-004: ReAct Pattern for Autonomous Test Orchestrator (5-6 hours)

**Goal**: Self-directing test execution with reasoning loops

**Current Problem**:
```python
# Fixed workflow - no autonomous decision-making
def run_test_suite():
    run_predictions()
    run_tests()
    analyze_results()
    generate_insights()
```

**Solution with ReAct Pattern**:
```python
class GuWuAgent:
    """Autonomous test orchestrator with ReAct pattern"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.predictor = FailurePredictor(db_path)
        self.gap_analyzer = TestGapAnalyzer(db_path)
        self.autofix = AutoFixGenerator(db_path)
        self.lifecycle = TestLifecycleManager(db_path)
        self.done = False
        self.context = {}
    
    def run_autonomous_session(self, initial_goal: str):
        """
        Autonomous test session with ReAct loop
        
        Example goals:
        - "Achieve 90% coverage on knowledge_graph module"
        - "Fix all flaky tests"
        - "Optimize test suite performance"
        """
        self.context['goal'] = initial_goal
        self.context['history'] = []
        
        while not self.done:
            # REASON: Think about what to do next
            thought = self._reason()
            self.context['history'].append({'type': 'thought', 'content': thought})
            
            # ACT: Execute chosen action
            action_result = self._act(thought['action'])
            self.context['history'].append({'type': 'action', 'result': action_result})
            
            # OBSERVE: Review results
            observation = self._observe(action_result)
            self.context['history'].append({'type': 'observation', 'content': observation})
            
            # REFLECT: Decide next step
            self.done = self._reflect(observation)
        
        return self._generate_report()
    
    def _reason(self) -> Dict:
        """
        THINKING phase: Analyze situation and decide action
        
        Questions to ask:
        - What's the current state?
        - What's the goal?
        - What have I tried?
        - What should I try next?
        """
        goal = self.context['goal']
        history = self.context['history']
        
        # Analyze current state
        if 'coverage' in goal:
            coverage = self._get_current_coverage()
            if coverage < 0.9:
                return {
                    'reasoning': f"Coverage is {coverage:.1%}, need to find gaps",
                    'action': 'analyze_gaps'
                }
            else:
                return {
                    'reasoning': f"Coverage goal achieved ({coverage:.1%})",
                    'action': 'complete'
                }
        
        elif 'flaky' in goal:
            flaky_tests = self._get_flaky_tests()
            if flaky_tests:
                return {
                    'reasoning': f"Found {len(flaky_tests)} flaky tests, need fixes",
                    'action': 'generate_fixes'
                }
            else:
                return {
                    'reasoning': "No flaky tests found",
                    'action': 'complete'
                }
        
        elif 'optimize' in goal:
            slow_tests = self._get_slow_tests()
            if slow_tests:
                return {
                    'reasoning': f"Found {len(slow_tests)} slow tests (>{5}s)",
                    'action': 'suggest_optimizations'
                }
            else:
                return {
                    'reasoning': "All tests within performance threshold",
                    'action': 'complete'
                }
        
        # Fallback: Run prediction
        return {
            'reasoning': "Uncertain state, run prediction to gather intel",
            'action': 'predict_failures'
        }
    
    def _act(self, action: str) -> Dict:
        """
        ACTION phase: Execute chosen action
        """
        if action == 'analyze_gaps':
            gaps = self.gap_analyzer.analyze()
            return {'action': 'analyze_gaps', 'gaps_found': len(gaps), 'gaps': gaps}
        
        elif action == 'generate_fixes':
            fixes = self.autofix.generate_fixes()
            return {'action': 'generate_fixes', 'fixes_generated': len(fixes), 'fixes': fixes}
        
        elif action == 'predict_failures':
            predictions = self.predictor.predict()
            return {'action': 'predict_failures', 'predictions': predictions}
        
        elif action == 'suggest_optimizations':
            optimizations = self._generate_optimizations()
            return {'action': 'suggest_optimizations', 'optimizations': optimizations}
        
        elif action == 'complete':
            return {'action': 'complete', 'status': 'goal_achieved'}
    
    def _observe(self, action_result: Dict) -> Dict:
        """
        OBSERVATION phase: Analyze action results
        """
        action = action_result['action']
        
        if action == 'analyze_gaps':
            gaps = action_result['gaps']
            critical_gaps = [g for g in gaps if g.priority == 'critical']
            
            return {
                'observation': f"Found {len(gaps)} gaps, {len(critical_gaps)} critical",
                'next_needed': 'generate_tests' if critical_gaps else 'complete',
                'confidence': 'high' if len(critical_gaps) > 0 else 'medium'
            }
        
        elif action == 'generate_fixes':
            fixes = action_result['fixes']
            auto_fixable = [f for f in fixes if f.confidence > 0.9]
            
            return {
                'observation': f"Generated {len(fixes)} fixes, {len(auto_fixable)} auto-fixable",
                'next_needed': 'apply_fixes' if auto_fixable else 'review_manual_fixes',
                'confidence': 'high'
            }
        
        elif action == 'predict_failures':
            predictions = action_result['predictions']
            high_risk = [p for p in predictions if p.probability > 0.7]
            
            return {
                'observation': f"Predicted {len(high_risk)} likely failures",
                'next_needed': 'run_high_risk_tests',
                'confidence': 'medium'
            }
    
    def _reflect(self, observation: Dict) -> bool:
        """
        REFLECTION phase: Should we continue or complete?
        
        Returns: True if done, False to continue
        """
        next_needed = observation['next_needed']
        confidence = observation['confidence']
        
        # High confidence + complete = done
        if next_needed == 'complete' and confidence == 'high':
            return True
        
        # Medium confidence + complete = verify first
        if next_needed == 'complete' and confidence == 'medium':
            # Add verification action to context
            self.context['next_action'] = 'verify_goal'
            return False
        
        # Not complete = continue
        self.context['next_action'] = next_needed
        return False
    
    def _generate_report(self) -> Dict:
        """Generate final report of autonomous session"""
        return {
            'goal': self.context['goal'],
            'total_actions': len([h for h in self.context['history'] if h['type'] == 'action']),
            'total_thoughts': len([h for h in self.context['history'] if h['type'] == 'thought']),
            'final_state': self.context['history'][-1],
            'success': self.done
        }

# Usage
agent = GuWuAgent(db_path='tools/guwu/metrics.db')

# Example 1: Coverage goal
report = agent.run_autonomous_session("Achieve 90% coverage on knowledge_graph module")

# Example 2: Flaky test goal
report = agent.run_autonomous_session("Fix all flaky tests")

# Example 3: Performance goal
report = agent.run_autonomous_session("Optimize test suite to <5s per test")
```

**Implementation Steps**:
1. Create `tools/guwu/agent/` directory
2. Implement `GuWuAgent` with ReAct loop
3. Integrate with existing components (predictor, gap_analyzer, etc.)
4. Add goal parsing and validation
5. Implement reasoning engine
6. Write unit tests for agent behavior
7. Create example scenarios
8. Update documentation

**Benefits**:
- ✅ Autonomous goal-directed behavior
- ✅ Self-correcting (bad actions → re-reason)
- ✅ Transparent reasoning (audit trail)
- ✅ Adaptive to changing situations
- ✅ Can handle complex multi-step goals

**Files to Create/Modify**:
- `tools/guwu/agent/__init__.py` (NEW)
- `tools/guwu/agent/orchestrator.py` (NEW)
- `tools/guwu/agent/reasoning.py` (NEW)
- `tests/unit/guwu/test_agent.py` (NEW)

**Success Criteria**:
- ✅ Agent achieves simple goals (>80% success rate)
- ✅ Reasoning is transparent (logged)
- ✅ Can handle goal failures gracefully
- ✅ Maximum 10 iterations before timeout

**Estimated Time**: 5-6 hours

---

### WP-GW-005: Planning Pattern for Smart Test Execution (4-5 hours)

**Goal**: Cost-optimized test execution planning (90% cost reduction)

**Current Problem**:
```python
# All tests use same expensive model
def analyze_all_tests(tests):
    for test in tests:
        analysis = expensive_gpt4_call(test)  # $$$
    return analysis
```

**Solution with Planning Pattern**:
```python
class TestExecutionPlanner:
    """Plan-and-Execute with cost optimization"""
    
    def __init__(self, expensive_model='gpt-4', cheap_model='gpt-3.5'):
        self.expensive_model = expensive_model
        self.cheap_model = cheap_model
    
    def create_execution_plan(self, tests: List[str], context: Dict) -> ExecutionPlan:
        """
        PLANNING PHASE: Use expensive model once to create plan
        
        Uses GPT-4 ($$$) to:
        - Analyze test suite structure
        - Identify critical vs routine tests
        - Create dependency graph
        - Group tests for parallel execution
        - Determine execution order
        """
        logging.info(f"[Gu Wu Planning] Using {self.expensive_model} for strategic planning...")
        
        plan = {
            'phase_1_critical': self._identify_critical_tests(tests),
            'phase_2_predicted_failures': self._get_predicted_high_risk(tests),
            'phase_3_changed_code': self._tests_for_changed_files(tests, context['changed_files']),
            'phase_4_coverage_gaps': self._tests_for_coverage_gaps(tests),
            'phase_5_remainder': self._remaining_tests(tests),
            
            # Parallelization strategy
            'parallel_groups': self._group_for_parallel_execution(tests),
            
            # Cost optimization
            'estimated_cost': self._estimate_cost(tests),
            'estimated_duration': self._estimate_duration(tests)
        }
        
        return ExecutionPlan(plan)
    
    def execute_plan(self, plan: ExecutionPlan) -> ExecutionResults:
        """
        EXECUTION PHASE: Use cheap model for each step
        
        Uses GPT-3.5 ($) for:
        - Executing individual tests
        - Basic analysis
        - Simple decision-making
        """
        results = {
            'phases_completed': [],
            'total_tests_run': 0,
            'total_duration': 0,
            'actual_cost': 0
        }
        
        # Execute each phase
        for phase_name, phase_tests in plan.phases.items():
            logging.info(f"[Gu Wu Execution] Phase: {phase_name} ({len(phase_tests)} tests)")
            
            # Use cheap model for execution
            phase_results = self._execute_tests_with_cheap_model(phase_tests)
            
            results['phases_completed'].append({
                'phase': phase_name,
                'tests_run': len(phase_tests),
                'duration': phase_results['duration'],
                'cost': phase_results['cost']
            })
            
            results['total_tests_run'] += len(phase_tests)
            results['total_duration'] += phase_results['duration']
            results['actual_cost'] += phase_results['cost']
        
        # Calculate savings
        naive_cost = self._calculate_naive_cost(results['total_tests_run'])
        savings_pct = ((naive_cost - results['actual_cost']) / naive_cost) * 100
        
        logging.info(f"[Gu Wu] Cost savings: {savings_pct:.1f}% (${naive_cost:.2f} → ${results['actual_cost']:.2f})")
        
        return ExecutionResults(results)
    
    def _identify_critical_tests(self, tests: List[str]) -> List[str]:
        """Use expensive model to identify critical tests"""
        # GPT-4 analyzes:
        # - Which tests validate core business logic?
        # - Which tests are integration points?
        # - Which tests have high blast radius?
        
        prompt = f"""
        Analyze these tests and identify which are CRITICAL (must pass):
        {tests}
        
        Criteria:
        - Core business logic validation
        - Integration point tests
        - High blast radius (many dependencies)
        """
        
        # Expensive call ($$$)
        critical_tests = self._call_expensive_model(prompt)
        return critical_tests
    
    def _execute_tests_with_cheap_model(self, tests: List[str]) -> Dict:
        """Use cheap model for simple execution decisions"""
        # GPT-3.5 handles:
        # - Should I skip this test? (based on recent results)
        # - Should I retry this test? (based on flaky score)
        # - Should I stop early? (based on cascading failures)
        
        results = []
        for test in tests:
            # Cheap decision ($)
            should_run = self._cheap_model_decides_if_run(test)
            
            if should_run:
                result = pytest.main([test])
                results.append(result)
            else:
                results.append('skipped')
        
        return {
            'results': results,
            'duration': sum(r.duration for r in results if r != 'skipped'),
            'cost': len(tests) * 0.001  # GPT-3.5 cost
        }
    
    def _calculate_naive_cost(self, num_tests: int) -> float:
        """Cost if we used expensive model for everything"""
        return num_tests * 0.03  # GPT-4 cost per test
```

**Implementation Steps**:
1. Create `tools/guwu/agent/planner.py`
2. Implement planning with expensive model
3. Implement execution with cheap model
4. Add cost tracking
5. Create plan validation
6. Write unit tests
7. Measure actual cost savings
8. Update documentation

**Benefits**:
- ✅ 90% cost reduction (GPT-4 planning + GPT-3.5 execution)
- ✅ Intelligent prioritization
- ✅ Parallel execution optimization
- ✅ Early failure detection
- ✅ Adaptive to code changes

**Files to Create/Modify**:
- `tools/guwu/agent/planner.py` (NEW)
- `tools/guwu/agent/executor.py` (NEW)
- `tools/guwu/agent/cost_tracker.py` (NEW)
- `tests/unit/guwu/test_planner.py` (NEW)

**Success Criteria**:
- ✅ Cost reduced by 80-90%
- ✅ Plan generation <10s
- ✅ Execution faster or equal to naive approach
- ✅ Critical tests always run first

**Estimated Time**: 4-5 hours

---

### WP-GW-006: Enhanced Reflection Pattern (3-4 hours)

**Goal**: Meta-learning and continuous improvement (learns from itself)

**Current Problem**:
```python
# Reflection exists but not systematic
class SelfReflectionEngine:
    def reflect_on_session(self, session_data):
        # Manual reflection logic
        insights = []
        if accuracy < 0.7:
            insights.append("Prediction accuracy low")
        return insights
```

**Solution with Enhanced Reflection Pattern**:
```python
class EnhancedReflectionEngine:
    """Meta-learning reflection with agentic pattern"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.learning_database = LearningDatabase(db_path)
    
    def reflect_on_session(self, session_data: Dict) -> ReflectionReport:
        """
        Multi-level reflection:
        1. Did my predictions work? (validation)
        2. Did my fixes work? (effectiveness)
        3. What patterns did I miss? (discovery)
        4. How can I improve? (learning)
        """
        
        # LEVEL 1: Validate predictions
        prediction_reflection = self._reflect_on_predictions(session_data)
        
        # LEVEL 2: Validate auto-fixes
        fix_reflection = self._reflect_on_fixes(session_data)
        
        # LEVEL 3: Discover new patterns
        pattern_reflection = self._discover_new_patterns(session_data)
        
        # LEVEL 4: Learn and improve
        learning_actions = self._generate_learning_actions(
            prediction_reflection,
            fix_reflection,
            pattern_reflection
        )
        
        # LEVEL 5: Meta-reflection (reflect on reflection)
        meta_reflection = self._reflect_on_reflection_quality()
        
        return ReflectionReport(
            predictions=prediction_reflection,
            fixes=fix_reflection,
            patterns=pattern_reflection,
            learning_actions=learning_actions,
            meta_reflection=meta_reflection
        )
    
    def _reflect_on_predictions(self, session_data: Dict) -> Dict:
        """Did my predictions work?"""
        predictions = session_data.get('predictions', [])
        actual_failures = session_data.get('actual_failures', [])
        
        # Calculate accuracy
        true_positives = len(set(predictions) & set(actual_failures))
        false_positives = len(set(predictions) - set(actual_failures))
        false_negatives = len(set(actual_failures) - set(predictions))
        
        accuracy = true_positives / len(predictions) if predictions else 0
        
        # Reflect on accuracy
        if accuracy > 0.8:
            reflection = "Excellent prediction accuracy! Keep current model."
            action = None
        elif accuracy > 0.6:
            reflection = "Good accuracy but room for improvement"
            action = "tune_prediction_threshold"
        else:
            reflection = "Poor accuracy. Need to analyze why predictions failed."
            action = "retrain_model"
        
        return {
            'accuracy': accuracy,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'reflection': reflection,
            'action': action
        }
    
    def _reflect_on_fixes(self, session_data: Dict) -> Dict:
        """Did my auto-fixes work?"""
        fixes_applied = session_data.get('fixes_applied', [])
        
        results = []
        for fix in fixes_applied:
            # Check if test now passes
            test_passed = self._verify_test_passes(fix.test_id)
            
            results.append({
                'fix_id': fix.id,
                'test_id': fix.test_id,
                'worked': test_passed,
                'confidence': fix.confidence
            })
        
        success_rate = sum(1 for r in results if r['worked']) / len(results) if results else 0
        
        # Reflect on success rate
        if success_rate > 0.8:
            reflection = "High fix success rate! Pattern database is accurate."
            action = None
        elif success_rate > 0.5:
            reflection = "Moderate success. Need to refine fix patterns."
            action = "analyze_failed_fixes"
        else:
            reflection = "Low success rate. Fix generation needs overhaul."
            action = "rebuild_fix_database"
        
        return {
            'fixes_attempted': len(fixes_applied),
            'success_rate': success_rate,
            'reflection': reflection,
            'action': action,
            'failed_fixes': [r for r in results if not r['worked']]
        }
    
    def _discover_new_patterns(self, session_data: Dict) -> Dict:
        """What patterns did I miss?"""
        failures = session_data.get('all_failures', [])
        
        # Group failures by error type
        error_types = {}
        for failure in failures:
            error_type = self._classify_error(failure.error_message)
            if error_type not in error_types:
                error_types[error_type] = []
            error_types[error_type].append(failure)
        
        # Find new patterns (error types we haven't seen before)
        known_patterns = self.learning_database.get_known_patterns()
        new_patterns = []
        
        for error_type, failures in error_types.items():
            if error_type not in known_patterns and len(failures) >= 3:
                # New pattern discovered!
                new_patterns.append({
                    'pattern': error_type,
                    'frequency': len(failures),
                    'examples': failures[:3],
                    'action': 'add_to_fix_database'
                })
        
        return {
            'new_patterns_found': len(new_patterns),
            'patterns': new_patterns,
            'reflection': f"Discovered {len(new_patterns)} new failure patterns"
        }
    
    def _generate_learning_actions(self, pred_refl, fix_refl, pattern_refl) -> List[Dict]:
        """What should I do to improve?"""
        actions = []
        
        # From prediction reflection
        if pred_refl['action']:
            actions.append({
                'type': 'improve_predictions',
                'action': pred_refl['action'],
                'priority': 'high' if pred_refl['accuracy'] < 0.6 else 'medium'
            })
        
        # From fix reflection
        if fix_refl['action']:
            actions.append({
                'type': 'improve_fixes',
                'action': fix_refl['action'],
                'priority': 'high' if fix_refl['success_rate'] < 0.5 else 'medium'
            })
        
        # From pattern discovery
        for pattern in pattern_refl['patterns']:
            actions.append({
                'type': 'add_pattern',
                'pattern': pattern['pattern'],
                'examples': pattern['examples'],
                'priority': 'medium'
            })
        
        return sorted(actions, key=lambda x: x['priority'], reverse=True)
    
    def _reflect_on_reflection_quality(self) -> Dict:
        """Meta-reflection: Am I reflecting well?"""
        # How often do my learning actions actually improve things?
        past_actions = self.learning_database.get_learning_actions(days=30)
        improvements = [a for a in past_actions if a.led_to_improvement]
        
        effectiveness = len(improvements) / len(past_actions) if past_actions else 0
        
        return {
            'reflection_effectiveness': effectiveness,
            'meta_reflection': (
                "My reflection process is effective" if effectiveness > 0.7
                else "Need to improve how I learn from experience"
            )
        }

# Usage
engine = EnhancedReflectionEngine(db_path='tools/guwu/metrics.db')

# After each test session
report = engine.reflect_on_session(session_data)

# Review learning actions
for action in report.learning_actions:
    if action['priority'] == 'high':
        execute_learning_action(action)
```

**Implementation Steps**:
1. Enhance `tools/guwu/reflection.py`
2. Add multi-level reflection (5 levels)
3. Implement learning action generation
4. Add meta-reflection capabilities
5. Create learning database schema
6. Write unit tests for reflection
7. Integrate with session end
8. Update documentation

**Benefits**:
- ✅ Systematic learning (not ad-hoc)
- ✅ Self-improving accuracy
- ✅ Transparent learning process
- ✅ Meta-reflection (reflects on reflection)
- ✅ Prioritized improvement actions

**Files to Create/Modify**:
- `tools/guwu/reflection.py` (ENHANCE)
- `tools/guwu/learning_database.py` (NEW)
- `tests/unit/guwu/test_reflection.py` (ENHANCE)

**Success Criteria**:
- ✅ Reflection runs after every session
- ✅ Learning actions generated and tracked
- ✅ Accuracy improves >5% per month
- ✅ Meta-reflection shows >70% effectiveness

**Estimated Time**: 3-4 hours

---

## 📊 Implementation Roadmap

### Stage 1: Core GoF Patterns (10-13 hours)
- **Week 1**: WP-GW-001 (Strategy) + WP-GW-002 (Observer)
- **Week 2**: WP-GW-003 (Decorator)

### Stage 2: Agentic Patterns (10-12 hours)
- **Week 3**: WP-GW-004 (ReAct) + WP-GW-005 (Planning)
- **Week 4**: WP-GW-006 (Enhanced Reflection)

**Total**: 20-25 hours (4-5 weeks part-time)

---

## 🎯 Success Metrics

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Extensibility | Modify core | Add strategies/observers | +50% easier |
| Real-time Insights | Batch (minutes) | Event-driven (instant) | <1s latency |
| Cost Efficiency | All GPT-4 | GPT-4 planning + GPT-3.5 exec | 90% savings |
| Autonomy | Scripted | Self-directing | 70% autonomous |
| Maintainability | Monolithic | Modular | +60% easier |

---

## 📚 References

- [[Agentic Workflow Patterns]] - Pattern catalog
- [[GoF Design Patterns Guide]] - GoF pattern guide
- [[Gu Wu Phase 3 AI Capabilities]] - Current capabilities
- `tools/guwu/` - Current implementation

---

**Status**: Ready for WP-GW-001 implementation  
**Next**: Begin Strategy Pattern refactoring