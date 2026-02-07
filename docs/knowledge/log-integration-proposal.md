# System Log Integration Proposal
**Integrating Application Logs into Feng Shui, Gu Wu, and Shi Fu**

**Version**: 1.0  
**Date**: February 7, 2026  
**Status**: 🟡 Proposal (Awaiting Approval)

---

## 📋 EXECUTIVE SUMMARY

**Problem**: We have rich application log data (SQLite database at `logs/app_logs.db`) that's currently isolated from our quality ecosystem (Feng Shui, Gu Wu, Shi Fu).

**Opportunity**: Logs contain runtime intelligence (errors, warnings, performance) that can enhance:
- **Feng Shui**: Detect runtime architecture issues
- **Gu Wu**: Correlate test failures with production errors
- **Shi Fu**: Cross-domain pattern detection (code → tests → runtime)

**Approach**: Create a unified **Log Intelligence Layer** that feeds into existing quality tools.

---

## 🎯 CURRENT LOG INFRASTRUCTURE

### What We Have ✅

**Database**: `logs/app_logs.db` (SQLite)

**Schema**:
```sql
CREATE TABLE application_logs (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    level VARCHAR(10) NOT NULL,        -- INFO, WARNING, ERROR
    logger VARCHAR(100) NOT NULL,       -- Module/component name
    message TEXT NOT NULL,
    duration_ms REAL DEFAULT NULL,      -- Performance timing
    created_at DATETIME NOT NULL
);
```

**Indices** (Optimized for queries):
- `idx_timestamp` - Time-based queries
- `idx_level` - Filter by severity
- `idx_created_at` - Retention cleanup
- `idx_duration` - Performance analysis

**Retention Policy** (Industry-standard):
- ERROR: 30 days (critical, low volume)
- WARNING: 14 days (important patterns)
- INFO: 7 days (high volume, recent context)

**API Access**:
- `GET /api/logs?level=ERROR&limit=100` - Query logs
- `GET /api/logs/stats` - Statistics by level
- Python: `LoggingService().get_logs(level='ERROR')`

---

## 🔮 PROPOSED INTEGRATION ARCHITECTURE

### Design Philosophy

**"Logs are the voice of runtime - quality tools should listen"**

```
┌─────────────────────────────────────────────────────────┐
│          APPLICATION LOGS (SQLite Database)             │
│  Levels: ERROR, WARNING, INFO  |  Retention: 7-30 days │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ (Single Source of Truth)
                          ▼
┌─────────────────────────────────────────────────────────┐
│             LOG INTELLIGENCE LAYER (NEW)                │
│  • Aggregation  • Pattern Detection  • Correlation     │
│  • Time-series Analysis  • Anomaly Detection           │
└─────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
   │ Feng Shui    │    │   Gu Wu      │    │   Shi Fu     │
   │ (Code)       │    │   (Tests)    │    │ (Ecosystem)  │
   └──────────────┘    └──────────────┘    └──────────────┘
```

### Three-Layer Approach

1. **Layer 1: Log Intelligence Layer** (NEW)
   - Central service for log analysis
   - Aggregation, pattern detection, correlation
   - Shared by all quality tools

2. **Layer 2: Tool-Specific Adapters** (NEW)
   - Feng Shui Log Adapter
   - Gu Wu Log Adapter
   - Shi Fu Log Correlation Engine (extend existing)

3. **Layer 3: Enhanced Quality Tools** (EXTEND)
   - Existing tools gain log-aware capabilities
   - New patterns detected via runtime data

---

## 🔧 DETAILED INTEGRATION PROPOSALS

### 1. FENG SHUI: Runtime Architecture Intelligence 🏛️

**Goal**: Detect architecture violations that only appear at runtime

#### New Capabilities

**A. Runtime DI Violation Detection**
```python
# Example: Detect hardwired connections causing runtime errors
ERROR: AttributeError: 'NoneType' object has no attribute 'connection'
      at modules/knowledge_graph/backend/service.py:45
      → Likely DI violation (hardwired .connection access)
```

**Pattern**: Correlate ERROR logs with code locations → Feng Shui violation detection

**B. Performance Hotspot Detection**
```python
# Example: Detect slow operations from duration_ms field
WARNING: Slow query detected (2450ms) at modules/data_products/backend/api.py:78
        → Feng Shui Performance Agent flags N+1 query pattern
```

**Pattern**: Aggregate `duration_ms` logs → Performance bottleneck analysis

**C. Module Health from Error Rate**
```python
# Example: Module with high error rate = architectural issue
ERROR: modules/csn_validation/backend/service.py (15 errors in 1 hour)
      → Feng Shui flags module for architectural review
```

**Pattern**: Error concentration → Module quality degradation

#### Implementation Strategy

**New File**: `tools/fengshui/disciples/log_adapter.py`

```python
class FengShuiLogAdapter:
    """Adapter for integrating logs into Feng Shui analysis"""
    
    def __init__(self, log_service: LoggingService):
        self.log_service = log_service
    
    def detect_runtime_di_violations(self, hours: int = 24) -> List[Dict]:
        """Find DI violations from runtime errors"""
        errors = self.log_service.get_logs(
            level='ERROR',
            start_date=(datetime.now() - timedelta(hours=hours)).isoformat()
        )
        
        violations = []
        for error in errors:
            # Pattern: AttributeError with .connection, .service, .db_path
            if 'AttributeError' in error['message'] and \
               any(attr in error['message'] for attr in ['.connection', '.service', '.db_path']):
                violations.append({
                    'type': 'DI_VIOLATION',
                    'severity': 'HIGH',
                    'location': self._extract_location(error['message']),
                    'timestamp': error['timestamp'],
                    'evidence': error['message']
                })
        
        return violations
    
    def detect_performance_hotspots(self, threshold_ms: float = 1000) -> List[Dict]:
        """Find slow operations from duration_ms logs"""
        # Query logs with duration > threshold
        # Aggregate by module/function
        # Return hotspots sorted by frequency + severity
        pass
    
    def get_module_error_rate(self, module_name: str, hours: int = 24) -> float:
        """Calculate error rate for module (errors per hour)"""
        # Query ERROR logs for module
        # Calculate rate over time period
        # Compare to baseline
        pass
```

**Integration Point**: Feng Shui Multi-Agent System

```python
# In tools/fengshui/agents/orchestrator.py
from tools.fengshui.disciples.log_adapter import FengShuiLogAdapter

class ArchitectAgent:
    def __init__(self, log_adapter: Optional[FengShuiLogAdapter] = None):
        self.log_adapter = log_adapter
    
    def analyze(self, module_path: Path) -> List[Violation]:
        violations = self._static_analysis(module_path)  # Existing
        
        # NEW: Add runtime violations from logs
        if self.log_adapter:
            runtime_violations = self.log_adapter.detect_runtime_di_violations()
            violations.extend(runtime_violations)
        
        return violations
```

---

### 2. GU WU: Test-Runtime Correlation 🧪

**Goal**: Understand relationship between test failures and production errors

#### New Capabilities

**A. Flaky Test Root Cause Analysis**
```python
# Example: Test fails intermittently, but logs show runtime error pattern
Test: test_knowledge_graph_query FAILED (flaky score: 0.7)
Logs: ERROR at modules/knowledge_graph/backend/service.py:45 (10 occurrences)
      → Root cause: Runtime DI issue, not test issue
```

**Pattern**: Correlate flaky tests with runtime errors → True vs False flakes

**B. Test Coverage Gap Detection**
```python
# Example: Production errors in untested code paths
ERROR: modules/data_products/backend/parser.py:123 (8 occurrences)
Coverage: 0% test coverage for parser.py:120-130
         → Gu Wu recommends: Add test for error scenario
```

**Pattern**: Runtime errors in low-coverage areas → Prioritize test creation

**C. Performance Regression Detection**
```python
# Example: Tests pass but production performance degrades
Test: test_api_performance PASSED (350ms)
Logs: WARNING Slow query (2450ms) in production (same code path)
     → Performance regression not caught by tests
```

**Pattern**: Test timing vs production timing → Test environment gaps

#### Implementation Strategy

**New File**: `tests/guwu/intelligence/log_correlation.py`

```python
class LogCorrelationEngine:
    """Correlate test results with production logs for intelligence"""
    
    def __init__(self, log_service: LoggingService, gu_wu_db: str):
        self.log_service = log_service
        self.gu_wu_db = gu_wu_db
    
    def analyze_flaky_test_root_causes(self) -> List[Dict]:
        """Find production errors that explain flaky tests"""
        flaky_tests = self._get_flaky_tests()  # From Gu Wu DB
        
        insights = []
        for test in flaky_tests:
            # Extract module/function being tested
            module = self._extract_module_from_test(test['test_name'])
            
            # Query logs for errors in that module
            errors = self.log_service.get_logs(
                level='ERROR',
                start_date=test['last_failure_date']
            )
            
            related_errors = [e for e in errors if module in e['message']]
            
            if related_errors:
                insights.append({
                    'test_name': test['test_name'],
                    'flaky_score': test['flaky_score'],
                    'likely_cause': 'runtime_error',
                    'evidence': related_errors,
                    'recommendation': 'Fix runtime error, test flakiness should resolve'
                })
        
        return insights
    
    def detect_coverage_gaps_from_errors(self) -> List[Dict]:
        """Find production errors in untested code"""
        # Get ERROR logs
        # Extract file:line from stack traces
        # Query coverage data
        # Return gaps with error frequency
        pass
    
    def compare_test_vs_production_performance(self) -> List[Dict]:
        """Compare test performance metrics with production"""
        # Query test timing from Gu Wu DB
        # Query production duration_ms from logs
        # Identify discrepancies
        pass
```

**Integration Point**: Gu Wu Intelligence Hub

```python
# In tests/guwu/intelligence/intelligence_hub.py
from tests.guwu.intelligence.log_correlation import LogCorrelationEngine

class IntelligenceHub:
    def __init__(self):
        # Existing engines
        self.recommendations = RecommendationEngine()
        self.dashboard = DashboardEngine()
        self.predictive = PredictiveAnalytics()
        
        # NEW: Log correlation engine
        self.log_correlation = LogCorrelationEngine(
            log_service=LoggingService(),
            gu_wu_db='tests/guwu/gu_wu.db'
        )
    
    def generate_report(self) -> Dict:
        report = {
            'recommendations': self.recommendations.generate(),
            'dashboard': self.dashboard.generate(),
            'predictive': self.predictive.generate(),
            'log_insights': self.log_correlation.analyze()  # NEW
        }
        return report
```

---

### 3. SHI FU: Cross-Domain Runtime Intelligence 🧘‍♂️

**Goal**: Detect patterns across code, tests, AND runtime (holistic view)

#### New Capabilities

**A. Code → Test → Runtime Triangle Pattern**
```python
# Example: Shi Fu detects complete causal chain
Code: 10 DI violations (Feng Shui)
Tests: 5 flaky tests (Gu Wu)
Logs: 15 runtime AttributeErrors (Logs)
     → Shi Fu teaching: "DI violations cause both test flakiness AND runtime errors"
```

**Pattern**: Three-way correlation → Root cause identification

**B. Deployment Impact Analysis**
```python
# Example: Error spike after code change
Before: 2 errors/hour (baseline)
After: 15 errors/hour (spike)
Correlation: Recent git commit changed modules/knowledge_graph/backend/service.py
            → Shi Fu recommendation: "Revert or hotfix immediately"
```

**Pattern**: Time-series error rate + git history → Deployment risk

**C. Learning from Production**
```python
# Example: Production teaches development
Production: ERROR pattern detected 50 times in 7 days
Tests: No test covers this error scenario
      → Shi Fu wisdom: "Production is teaching us - add regression test"
```

**Pattern**: Recurring errors without tests → Test gap prioritization

#### Implementation Strategy

**Extend Existing**: `tools/shifu/correlation_engine.py`

```python
# Add new correlation pattern
class RuntimeErrorPattern(BasePattern):
    """Detect correlation between code issues, test issues, and runtime errors"""
    
    def __init__(self, log_service: LoggingService):
        super().__init__(
            name="runtime_error_correlation",
            priority="URGENT",
            description="Code/test issues causing production errors"
        )
        self.log_service = log_service
    
    def detect(self, feng_shui_data: Dict, gu_wu_data: Dict) -> Optional[Dict]:
        """Detect three-way correlation pattern"""
        
        # Get runtime errors from logs
        errors = self.log_service.get_logs(level='ERROR', limit=1000)
        error_modules = self._extract_modules(errors)
        
        # Find modules with: DI violations + flaky tests + runtime errors
        problem_modules = []
        for module in error_modules:
            di_violations = self._count_di_violations(feng_shui_data, module)
            flaky_tests = self._count_flaky_tests(gu_wu_data, module)
            error_count = len([e for e in errors if module in e['message']])
            
            if di_violations > 0 and flaky_tests > 0 and error_count > 5:
                problem_modules.append({
                    'module': module,
                    'di_violations': di_violations,
                    'flaky_tests': flaky_tests,
                    'runtime_errors': error_count,
                    'severity': self._calculate_severity(di_violations, flaky_tests, error_count)
                })
        
        if problem_modules:
            return {
                'pattern_detected': True,
                'confidence': self._calculate_confidence(problem_modules),
                'affected_modules': problem_modules,
                'evidence': {
                    'feng_shui': 'DI violations detected',
                    'gu_wu': 'Flaky tests detected',
                    'logs': 'Runtime errors detected'
                }
            }
        
        return None
```

**Integration Point**: Shi Fu Wisdom Generator

```python
# In tools/shifu/wisdom_generator.py
class WisdomGenerator:
    def generate_teaching(self, pattern: Dict) -> Dict:
        if pattern['name'] == 'runtime_error_correlation':
            return {
                'teaching': "Code violations cause BOTH test flakiness AND production errors",
                'wisdom': "Fix the root cause (DI violations), and both symptoms heal together",
                'action': f"Prioritize fixing {len(pattern['affected_modules'])} modules with three-way correlation",
                'value': "Single fix resolves multiple problems (10x efficiency)",
                'priority': 'URGENT'
            }
```

---

## 📊 IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Week 1) - 8-12 hours

**Goal**: Create Log Intelligence Layer

- [ ] Create `core/services/log_intelligence.py` (central service)
- [ ] Implement aggregation functions (error rate, hotspots)
- [ ] Implement pattern detection (DI errors, performance issues)
- [ ] Add unit tests (100% coverage via Gu Wu)
- [ ] Update `core/interfaces/logger.py` if needed

**Deliverable**: Reusable log analysis service for all tools

### Phase 2: Feng Shui Integration (Week 2) - 6-8 hours

**Goal**: Runtime architecture intelligence

- [ ] Create `tools/fengshui/disciples/log_adapter.py`
- [ ] Implement DI violation detection from logs
- [ ] Implement performance hotspot detection
- [ ] Integrate with Feng Shui Multi-Agent System
- [ ] Add tests and documentation

**Deliverable**: Feng Shui detects runtime architecture issues

### Phase 3: Gu Wu Integration (Week 2) - 6-8 hours

**Goal**: Test-runtime correlation

- [ ] Create `tests/guwu/intelligence/log_correlation.py`
- [ ] Implement flaky test root cause analysis
- [ ] Implement coverage gap detection from errors
- [ ] Integrate with Gu Wu Intelligence Hub
- [ ] Add tests and documentation

**Deliverable**: Gu Wu correlates test results with production

### Phase 4: Shi Fu Integration (Week 3) - 4-6 hours

**Goal**: Cross-domain runtime intelligence

- [ ] Extend `tools/shifu/correlation_engine.py`
- [ ] Add `RuntimeErrorPattern` detector
- [ ] Implement three-way correlation (code-test-runtime)
- [ ] Extend Wisdom Generator for runtime patterns
- [ ] Add tests and documentation

**Deliverable**: Shi Fu provides holistic runtime insights

### Phase 5: Polish & Deploy (Week 3) - 4-6 hours

**Goal**: Production-ready integration

- [ ] Performance optimization (query efficiency)
- [ ] Dashboard/UI updates (show runtime insights)
- [ ] Update `.clinerules` with log integration guidelines
- [ ] Create knowledge vault documentation
- [ ] User training materials

**Deliverable**: Production-ready log intelligence system

**Total Effort**: 28-40 hours (3-4 weeks)

---

## 🎯 SUCCESS METRICS

### Quantitative Metrics

1. **Detection Rate**: % of runtime issues detected by quality tools
   - Target: 80%+ of production errors detected by Feng Shui/Gu Wu
   
2. **Root Cause Accuracy**: % of Shi Fu correlations that are correct
   - Target: 90%+ accuracy on three-way correlations
   
3. **Response Time**: Time from error to detection
   - Target: < 1 hour for URGENT patterns
   
4. **False Positive Rate**: % of incorrect detections
   - Target: < 10% false positives

### Qualitative Benefits

1. **Proactive Quality**: Detect issues before they become critical
2. **Faster Debugging**: Runtime errors directly linked to code locations
3. **Better Testing**: Production errors drive test prioritization
4. **Holistic View**: Complete picture (code + tests + runtime)

---

## ⚠️ RISKS & MITIGATIONS

### Risk 1: Performance Impact
**Concern**: Log queries could slow down quality tools

**Mitigation**:
- Use indexed queries (existing indices on timestamp, level)
- Implement caching for frequent queries
- Async log analysis (background processing)
- Limit query timeframes (e.g., last 24 hours)

### Risk 2: Data Quality
**Concern**: Poor log quality → Poor insights

**Mitigation**:
- Validate log structure during analysis
- Filter noise (suppress known harmless patterns)
- Require structured logging (JSON format where possible)
- Monitor log quality metrics

### Risk 3: False Correlations
**Concern**: Tools detect spurious correlations

**Mitigation**:
- Confidence scoring (0.0-1.0)
- Evidence requirements (multiple data points)
- Manual review for URGENT patterns
- Learn from false positives (ML improvement)

### Risk 4: Log Retention
**Concern**: Old logs deleted before analysis

**Mitigation**:
- ERROR logs kept 30 days (sufficient for most patterns)
- Export critical error patterns to long-term storage
- Real-time analysis for time-sensitive patterns
- Alerts for critical error spikes

---

## 💡 ALTERNATIVE APPROACHES CONSIDERED

### Option A: Direct Database Integration (REJECTED)
**Why rejected**: Tight coupling between tools and log database schema

### Option B: Message Queue (Kafka/RabbitMQ) (OVERKILL)
**Why rejected**: Too complex for current scale, adds dependencies

### Option C: Log File Parsing (REJECTED)
**Why rejected**: Already have structured SQLite database, parsing is inefficient

### Option D: Layered Intelligence Approach (SELECTED) ✅
**Why selected**: 
- Loose coupling (tools use adapter pattern)
- Reusable intelligence layer
- Incremental adoption
- No schema changes required

---

## 🚀 NEXT STEPS

### Immediate Actions

1. **User Review**: Get feedback on proposal (this document)
2. **Prioritization**: Confirm this fits project roadmap
3. **Safety Checkpoint**: `git commit + push` before starting
4. **Phase 1 Start**: Implement Log Intelligence Layer

### Questions for User

1. **Priority**: Should we tackle this before or after security fixes (45 SQL injections)?
2. **Scope**: Start with all 3 tools (Feng Shui + Gu Wu + Shi Fu) or one at a time?
3. **Timeline**: 3-4 weeks effort - does this fit current schedule?
4. **Features**: Any specific log patterns you want detected first?

---

## 📚 REFERENCES

**Related Documentation**:
- `modules/log_manager/README.md` - Current log system
- `tools/fengshui/README.md` - Feng Shui architecture
- `tests/guwu/README.md` - Gu Wu testing framework
- `tools/shifu/README.md` - Shi Fu ecosystem orchestrator
- `.clinerules` - Development standards (section 5, 7, 8)

**Key Files**:
- `modules/log_manager/backend/logging_service.py` - Log service interface
- `modules/log_manager/backend/sqlite_logger.py` - SQLite log handler
- `logs/app_logs.db` - Application log database

---

**Conclusion**: This proposal creates a unified Log Intelligence Layer that enhances all three quality tools (Feng Shui, Gu Wu, Shi Fu) with runtime awareness. The layered architecture ensures loose coupling, incremental adoption, and reusability. Estimated effort: 3-4 weeks for complete implementation.

**Status**: 🟡 Awaiting user approval to proceed