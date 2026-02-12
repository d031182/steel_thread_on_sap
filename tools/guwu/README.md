# Gu Wu (顾武) - Self-Healing Test Intelligence

**Version**: 7.0 (Phase 7 Intelligence Complete)  
**Philosophy**: "Attending to martial affairs" - Disciplined, self-healing tests

## 🎯 Overview

Gu Wu is a self-healing, self-optimizing testing framework that learns from test execution patterns and provides intelligent recommendations. Like its namesake - attending to martial affairs with discipline - Gu Wu maintains test suite readiness through continuous improvement.

### Key Features

- **Test Pyramid Enforcement**: 70% unit / 20% integration / 10% E2E (automatic)
- **Auto-Prioritization**: Likely-to-fail tests run first
- **Flaky Detection**: Transition-based algorithm (score 0.0-1.0)
- **Performance Tracking**: Slow tests flagged (>5s threshold)
- **Gap Detection**: Automatically finds untested code
- **Meta-Learning**: Learns from execution history
- **Intelligence Hub**: 3 engines (Recommendations, Dashboard, Predictive)

## 🚀 Quick Start

### Installation

No installation needed - Gu Wu is part of the project tools.

### Basic Usage

```bash
# Show help and available commands
python -m tools.guwu

# Run tests with Gu Wu optimization
python -m tools.guwu run

# Run specific tests
python -m tools.guwu run tests/unit/ -v

# Get comprehensive intelligence report
python -m tools.guwu intelligence
```

## 📋 Commands

### `run` - Execute Tests with Optimization

Run tests with automatic prioritization and performance tracking.

```bash
# Run all tests
python -m tools.guwu run

# Run specific path
python -m tools.guwu run tests/unit/

# Verbose output
python -m tools.guwu run -v

# With pytest markers
python -m tools.guwu run -m "unit and fast"
```

**What it does**:
- Auto-prioritizes tests (likely-to-fail first)
- Tracks execution time
- Records flakiness scores
- Updates test metrics database
- Enforces test pyramid (70/20/10)

### `intelligence` - Intelligence Hub Report

Comprehensive analysis combining all 3 intelligence engines.

```bash
# Run full intelligence hub
python -m tools.guwu intelligence
```

**Provides**:
1. **Recommendations** - 8 types of actionable insights
2. **Dashboard** - Visual health metrics + trends
3. **Predictive** - ML failure forecasting

**Use when**:
- Starting work session (baseline health check)
- After test failures (root cause analysis)
- Weekly quality reviews

### `dashboard` - Health Dashboard

Visual metrics showing test suite health over time.

```bash
# Show health dashboard
python -m tools.guwu dashboard
```

**Displays**:
- Overall health score (0-100)
- Failure rate trends (7/30 day moving average)
- Execution time trends
- Flaky test score distribution
- Coverage percentage over time

### `recommend` - Actionable Recommendations

Get prioritized recommendations for test improvements.

```bash
# Show recommendations
python -m tools.guwu recommend
```

**8 Types of Insights**:
1. Flaky tests (prioritized by impact)
2. Slow tests (> 5s threshold)
3. Failing tests (recent failures)
4. Coverage gaps (untested code)
5. Test debt (accumulating issues)
6. Maintenance needs (code smells)
7. Optimization opportunities (parallelization)
8. Best practices (test quality)

### `predict` - ML Failure Prediction

ML-powered failure forecasting with pre-flight checks.

```bash
# Show failure predictions
python -m tools.guwu predict

# Pre-flight check (before commit)
python -m tools.guwu predict --pre-flight
```

**Capabilities**:
- Predicts test failures before commit
- ML-powered probability scores
- Historical pattern analysis
- Risk assessment with confidence

### `gaps` - Test Coverage Gaps

Identify untested code and missing test files.

```bash
# Show coverage gaps
python -m tools.guwu gaps
```

**Detects**:
- Missing test files (untested modules)
- Incomplete coverage (< 70% threshold)
- Untested functions/classes
- Critical code without tests

### `metrics` - Detailed Test Metrics

Show detailed execution metrics from the database.

```bash
# Show metrics
python -m tools.guwu metrics
```

**Tracks**:
- Test execution history (pass/fail/skip)
- Duration tracking (performance trends)
- Flakiness scores (0.0-1.0 scale)
- Coverage percentages (per module)
- Learning events (meta-learning insights)

## 🧪 Test Pyramid

Gu Wu automatically enforces the test pyramid distribution:

```
         /\
        /  \  10% E2E Tests (< 30s each)
       /____\
      /      \
     /  20%   \ Integration Tests (< 5s each)
    /__________\
   /            \
  /     70%      \ Unit Tests (< 1s each)
 /________________\
```

**Enforced via pytest hooks** (automatic)

## 📊 Intelligence Engines

### 1. Recommendations Engine

Analyzes test metrics and generates 8 types of actionable insights.

**Example Output**:
```
💡 Actionable Recommendations

[URGENT] Flaky Tests (3 found):
  1. test_data_refresh (flakiness: 0.8)
     → Fix non-deterministic behavior
  
[HIGH] Slow Tests (5 found):
  1. test_full_integration (15.2s)
     → Optimize or split into smaller tests

[MEDIUM] Coverage Gaps (2 areas):
  1. modules/logger/service.py (45% coverage)
     → Add tests for error handling
```

### 2. Dashboard Engine

Visual representation of test suite health trends.

**Metrics**:
- Overall health score trend
- Failure rate (7-day/30-day moving average)
- Execution time trends
- Flaky test distribution
- Coverage evolution

### 3. Predictive Engine

ML-powered failure prediction using historical patterns.

**Features**:
- Pre-flight checks (predict before commit)
- Failure probability per test
- Risk assessment scores
- Confidence intervals

## 🔧 Integration

### Pytest Hooks (Automatic)

Gu Wu integrates with pytest via conftest.py hooks:

```python
# tests/conftest.py
from tests.guwu.plugins import GuWuPlugin

# Automatically prioritizes, tracks, and learns from tests
```

### Pre-Commit Integration

```bash
# Runs automatically via .git/hooks/pre-commit
# - Executes affected tests
# - Validates coverage
# - Pre-flight failure prediction
```

### Feng Shui Integration

Gu Wu integrates with Feng Shui for E2E test generation:

```bash
# Complete pipeline (Feng Shui → Gu Wu → pytest)
python -m tools.guwu.feng_shui_integration knowledge_graph_v2
```

**Pipeline**:
1. Feng Shui analyzes module architecture
2. Gu Wu generates E2E tests from report
3. Pytest executes generated tests

## 📝 Writing Tests

### Unit Test Example

```python
import pytest

@pytest.mark.unit
@pytest.mark.fast
def test_calculate_total():
    """Test calculate_total returns correct sum (AAA pattern)"""
    # ARRANGE
    items = [10, 20, 30]
    
    # ACT
    result = calculate_total(items)
    
    # ASSERT
    assert result == 60
```

###Integration Test Example

```python
import pytest

@pytest.mark.integration
@pytest.mark.slow
def test_api_database_integration():
    """Test API correctly saves to database"""
    # ARRANGE
    api_client = create_test_client()
    db = create_test_database()
    
    # ACT
    response = api_client.post('/items', json={'name': 'Test'})
    
    # ASSERT
    assert response.status_code == 201
    assert db.query(Item).count() == 1
```

### E2E Test Example

```python
import pytest

@pytest.mark.e2e
@pytest.mark.critical
def test_user_workflow():
    """Test complete user checkout workflow"""
    # Critical business workflow test
    # Maximum 30 seconds execution time
    ...
```

## 🎓 Best Practices

### When to Use Each Command

| Scenario | Command | Frequency |
|----------|---------|-----------|
| Development | `run` | Continuous |
| Session start | `intelligence` | Daily |
| Test failures | `recommend` | As needed |
| Before commit | `predict --pre-flight` | Always |
| Weekly review | `dashboard` | Weekly |
| Coverage check | `gaps` | Weekly |

### Interpreting Health Scores

- **90-100**: Excellent (well-maintained test suite)
- **75-89**: Good (minor improvements needed)
- **60-74**: Fair (address issues soon)
- **< 60**: Poor (requires immediate attention)

### Fixing Flaky Tests

```python
# ❌ Flaky (non-deterministic)
def test_with_timing():
    time.sleep(0.1)  # Race condition
    assert result == expected

# ✅ Stable (deterministic)
def test_with_mock(mock_timer):
    mock_timer.return_value = fixed_time
    assert result == expected
```

### Optimizing Slow Tests

```python
# ❌ Slow (> 5s)
def test_full_database():
    populate_entire_database()  # Expensive setup
    run_test()

# ✅ Fast (< 1s)
@pytest.fixture
def minimal_data():
    return create_minimal_test_data()

def test_with_fixture(minimal_data):
    run_test(minimal_data)  # Only what's needed
```

## 🔍 Troubleshooting

### Tests Not Auto-Prioritized

Check conftest.py includes Gu Wu plugin:
```python
from tests.guwu.plugins import GuWuPlugin
pytest_plugins = ['tests.guwu.plugins.human_readable_errors']
```

### Metrics Not Tracking

Verify database exists:
```bash
ls tests/guwu/guwu_metrics.db
```

If missing, it will be created automatically on first test run.

### Intelligence Hub Errors

Ensure Phase 7 is complete:
```bash
# Check if intelligence engines exist
ls tests/guwu/intelligence/
# Should show: intelligence_hub.py, recommendations.py, dashboard.py, predictive.py
```

## 📚 Advanced Usage

### Legacy Commands (Still Supported)

```bash
# Direct pytest (auto-optimized via hooks)
pytest

# Direct Intelligence Hub
python -m tests.guwu.intelligence.intelligence_hub

# Individual engines
python -m tests.guwu.intelligence.recommendations
python -m tests.guwu.intelligence.dashboard
python -m tests.guwu.intelligence.predictive
```

### Custom Configuration

```python
# Via pytest.ini
[tool:pytest]
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests
    e2e: End-to-end tests
    fast: Tests that run in < 1s
    slow: Tests that run in > 5s
```

### API Usage

```python
from tools.guwu.metrics import TestMetrics

metrics = TestMetrics()
flaky_tests = metrics.get_flaky_tests(threshold=0.7)
slow_tests = metrics.get_slow_tests(threshold=5.0)
```

## 📊 Performance Metrics

| Metric | Before (Manual) | After (Gu Wu) | Improvement |
|--------|----------------|---------------|-------------|
| **Test Speed** | 60-300s (browser) | 1-5s (pytest) | **60-180x faster** |
| **Flaky Detection** | Manual guess | Automated (0.0-1.0 score) | 100% reliable |
| **Coverage Tracking** | Manual check | Automated gaps detection | Real-time |
| **Failure Prediction** | None | ML-powered | Proactive |

## 📖 Related Documentation

- [[Gu Wu Testing Framework]] - Architecture details
- [[Gu Wu Phase 7 Intelligence]] - Intelligence engines
- `tests/README.md` - Test structure guide
- `.clinerules` - Development standards (Section 7)

## 🤝 Contributing

Gu Wu is part of the quality ecosystem:

```
Feng Shui → Analyzes code architecture
    ↓
Gu Wu → Analyzes test quality
    ↓
Shi Fu → Finds correlations (meta-intelligence)
```

When extending Gu Wu:
1. Add new intelligence engine in `tests/guwu/intelligence/`
2. Update Intelligence Hub to include new engine
3. Add tests in `tests/unit/tools/guwu/`
4. Update documentation

## 📜 Philosophy

> "In martial affairs, readiness is maintained through discipline and continuous training. In testing, quality is maintained through self-healing frameworks and continuous learning. The warrior trains daily; the test suite learns continuously."

**Core Principles**:
- 🎯 **Discipline**: Follow test pyramid (70/20/10)
- 🔄 **Self-Healing**: Automatically detect and report issues
- 📈 **Continuous Learning**: Learn from execution history
- 🚀 **Speed**: Fast feedback loops (< 5s for most tests)
- 🎓 **Intelligence**: Proactive recommendations, not reactive fixes

---

**Version**: 7.0 (Phase 7 Intelligence Complete)  
**Last Updated**: 2026-02-12  
**License**: MIT