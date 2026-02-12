# Shi Fu (师傅) - Quality Ecosystem Orchestrator

**Version**: 4.8 (Phase 8 Complete)  
**Philosophy**: "The Master Teacher" - Code and Tests are Yin and Yang

## 🎯 Overview

Shi Fu is a meta-agent that observes both Feng Shui (code quality) and Gu Wu (test quality) to detect cross-domain patterns invisible to individual tools. Like a master teacher, Shi Fu sees the relationships between code and tests, identifying root causes that span both domains.

### Key Features

- **Cross-Domain Intelligence**: Observes both code and test quality
- **5 Correlation Patterns**: Detects root causes across domains
- **Holistic Health Scoring**: Ecosystem score with correlation penalties
- **Priority-Based Teachings**: Actionable recommendations ranked by urgency
- **Non-Invasive**: Read-only observation, guides rather than commands
- **Auto-Integration**: Weekly checks + PROJECT_TRACKER.md updates

## 🚀 Quick Start

### Installation

No installation needed - Shi Fu is part of the project tools.

### Basic Usage

```bash
# Show help and available commands
python -m tools.shifu

# Session start check (run at beginning of session)
python -m tools.shifu --session-start

# Manual weekly analysis
python -m tools.shifu --weekly-analysis

# Quick health check
python -m tools.shifu --health-check
```

## 📋 Commands

### `--session-start` - Auto Session Check ⭐ RECOMMENDED

Runs automatically at session start to check ecosystem health.

```bash
# Run at session start
python -m tools.shifu --session-start
```

**What it does**:
1. Checks if 7 days passed since last analysis
2. Runs weekly analysis if needed
3. Generates prioritized teachings
4. Notifies if URGENT/HIGH patterns detected
5. Updates PROJECT_TRACKER.md with high-priority items
6. Presents top recommendations

**AI Response Handling**:
- **Healthy**: "✅ Ecosystem health looks good! Continue current work."
- **Issues found**: Present recommendations, ask to work on patterns
- **URGENT**: Recommend addressing immediately before other work

### `--weekly-analysis` - Manual Full Analysis

Force full ecosystem analysis (bypasses 7-day check).

```bash
# Run full analysis
python -m tools.shifu --weekly-analysis
```

**Analyzes**:
- Feng Shui code quality metrics
- Gu Wu test quality metrics
- Correlation patterns across domains
- Root cause identification
- Priority-based teachings

**Duration**: 30-60 seconds (comprehensive)

### `--health-check` - Quick Status

Quick ecosystem health check without full analysis.

```bash
# Quick check
python -m tools.shifu --health-check
```

**Shows**:
- Current ecosystem score
- Number of active patterns
- Days since last analysis
- Quick recommendations

**Duration**: < 5 seconds (fast)

## 🔍 The 5 Correlation Patterns

Shi Fu detects root causes that span both code and tests:

### 1. DI Violations → Flaky Tests (URGENT/HIGH)

**Pattern**: Hardwired dependencies cause non-deterministic test behavior

**Evidence**:
- Feng Shui detects: 10 DI violations in module
- Gu Wu detects: 5 flaky tests in same module
- Correlation confidence: 0.9

**Wisdom**: "Fix DI violations, flaky tests heal automatically"

**Example**:
```python
# ❌ Hardwired dependency causes flaky test
def get_data():
    db = get_app().connection  # Non-deterministic in tests
    return db.query(...)

# ✅ Injected dependency = stable test
def get_data(db_connection):
    return db_connection.query(...)
```

### 2. High Complexity → Low Coverage (HIGH)

**Pattern**: Complex code has many paths, hard to test thoroughly

**Evidence**:
- Feng Shui detects: Cyclomatic complexity > 10
- Gu Wu detects: Coverage < 70%
- Correlation confidence: 0.85

**Wisdom**: "Simplify code, testing becomes easier, coverage rises"

**Example**:
```python
# ❌ Complex function (hard to test)
def process_order(order):
    if order.type == 'A':
        if order.priority == 'high':
            if order.region == 'US':
                # ... 10 more nested conditions
                
# ✅ Simple functions (easy to test)
def route_order(order):
    strategy = get_strategy(order)
    return strategy.process(order)
```

### 3. Security Issues → Test Gaps (URGENT)

**Pattern**: Vulnerabilities lack regression prevention

**Evidence**:
- Feng Shui detects: SQL injection risk
- Gu Wu detects: No security tests
- Correlation confidence: 0.95

**Wisdom**: "Add security tests, vulnerabilities stay fixed"

**Example**:
```python
# ❌ Vulnerability without test
def execute_query(user_input):
    return db.execute(f"SELECT * FROM users WHERE name = '{user_input}'")

# ✅ Test prevents regression
def test_sql_injection_prevented():
    malicious_input = "'; DROP TABLE users; --"
    result = execute_query(malicious_input)
    assert result == []  # Should be safely handled
```

### 4. Performance Issues → Slow Tests (MEDIUM)

**Pattern**: Inefficient code (N+1 queries) slows test suite

**Evidence**:
- Feng Shui detects: N+1 query pattern
- Gu Wu detects: Tests taking > 10s
- Correlation confidence: 0.75

**Wisdom**: "Optimize code, tests run faster, better DX"

### 5. Module Health → Test Health (HIGH)

**Pattern**: Modules with high violation count have failing tests

**Evidence**:
- Feng Shui detects: Module health score < 60
- Gu Wu detects: High test failure rate
- Correlation confidence: 0.8

**Wisdom**: "Technical debt affects both code and tests together"

## 📊 Output & Reports

### Session Start Output

```
======================================================================
  师傅 SHI FU - Quality Ecosystem Orchestrator
  'The Master Teacher' - Holistic Quality Intelligence
======================================================================

🔍 Checking ecosystem health...

✅ Feng Shui Health: 92/100 (Healthy)
✅ Gu Wu Health: 88/100 (Good)

📋 Pattern Detection:
   [URGENT] DI Violations → Flaky Tests
      • 10 DI violations in knowledge_graph_v2
      • 5 flaky tests in same module
      • Confidence: 0.9
      • Teaching: Fix DI violations first, flaky tests heal automatically

💡 Recommendation:
   Work on DI violations before other features
   Estimated impact: -5 flaky tests, +10 health score

🔄 Auto-Update:
   Added to PROJECT_TRACKER.md as HIGH priority
```

### Weekly Analysis Report

```
======================================================================
Shi Fu Weekly Analysis - Holistic Quality Review
======================================================================

📊 ECOSYSTEM HEALTH
   Overall Score: 90/100
   Feng Shui (Code): 92/100
   Gu Wu (Tests): 88/100

🔍 PATTERNS DETECTED (3 active)
   1. [URGENT] DI Violations → Flaky Tests (confidence: 0.9)
   2. [HIGH] Complexity → Coverage (confidence: 0.85)
   3. [MEDIUM] Performance → Slow Tests (confidence: 0.75)

🎓 TOP TEACHINGS
   1. Fix 10 DI violations → 5 flaky tests heal (ROOT CAUSE)
   2. Simplify complex functions → coverage rises naturally
   3. Optimize N+1 queries → test suite runs 2x faster

📈 TRENDS
   7-day: +5 health points
   30-day: +12 health points
   Direction: Improving ✅
```

## 🔧 Integration

### Automatic Integration (Phase 4)

Shi Fu automatically integrates with project workflows:

**Weekly Analysis** (automatic):
- Checks every 7 days since last run
- Generates prioritized teachings
- Updates PROJECT_TRACKER.md with HIGH priority items
- Notifies if URGENT patterns detected

**Manual Trigger** (when needed):
```bash
python -m tools.shifu --weekly-analysis
```

### AI Assistant Integration

Shi Fu guides AI decision-making:

```
AI: Starting work on feature X
     ↓
AI: Run python -m tools.shifu --session-start
     ↓
Shi Fu: [URGENT] DI Violations → Flaky Tests detected
     ↓
AI: Recommends fixing DI violations first
     ↓
User: Agrees, fixes root cause
     ↓
Result: Both problems solved with one fix
```

## 🎓 Best Practices

### When to Use Each Command

| Scenario | Command | Frequency |
|----------|---------|-----------|
| Session start | `--session-start` | Daily |
| Weekly review | `--weekly-analysis` | Weekly |
| Quick check | `--health-check` | As needed |

### Understanding Priority Levels

**URGENT** (Action required immediately):
- Security issues without tests
- DI violations causing flaky tests
- Critical bugs affecting both domains

**HIGH** (Action required soon):
- Complexity causing low coverage
- Module health affecting test health
- Performance issues slowing CI/CD

**MEDIUM** (Plan to address):
- Performance → slow tests
- Documentation gaps
- Minor architectural issues

**LOW** (Monitor):
- File organization
- Code style
- Minor optimizations

### Interpreting Confidence Scores

- **0.9-1.0**: Strong correlation (definite root cause)
- **0.7-0.89**: Good correlation (likely root cause)
- **0.5-0.69**: Moderate correlation (possible relationship)
- **< 0.5**: Weak correlation (coincidental)

## 📈 Ecosystem Health Scoring

### Formula

```
Ecosystem Score = (
    Feng Shui Score * 0.5 +
    Gu Wu Score * 0.5 -
    Correlation Penalties
)
```

**Correlation Penalties**:
- Each URGENT pattern: -5 points
- Each HIGH pattern: -3 points
- Each MEDIUM pattern: -1 point

### Example Calculation

```
Feng Shui: 92/100
Gu Wu: 88/100
Patterns: 1 URGENT, 1 HIGH, 1 MEDIUM

Base Score = (92 * 0.5) + (88 * 0.5) = 90
Penalties = -5 (URGENT) - 3 (HIGH) - 1 (MEDIUM) = -9
Final Score = 90 - 9 = 81/100
```

## 🔍 Troubleshooting

### No Patterns Detected

If Shi Fu shows no patterns but issues exist:
- Check Feng Shui and Gu Wu individually
- Verify both tools have updated metrics
- Review correlation thresholds (may be too high)

### False Correlations

If Shi Fu suggests incorrect relationships:
- Review confidence score (< 0.7 = questionable)
- Check if issues are in different modules
- Consider timing (did both issues appear together?)

### Missing Data

If Shi Fu can't analyze:
- Run Feng Shui first: `python -m tools.fengshui analyze`
- Run Gu Wu first: `python -m tools.guwu intelligence`
- Both must have recent data (< 7 days old)

## 📚 Advanced Usage

### Legacy Commands

```bash
# Direct Python API (legacy)
from tools.shifu.shifu import ShiFu

shifu = ShiFu()
teachings = shifu.generate_weekly_analysis()
```

### Custom Pattern Detection

```python
# Add new correlation pattern
from tools.shifu.patterns.base_pattern import BasePattern

class MyPattern(BasePattern):
    def detect(self, fengshui_data, guwu_data):
        # Custom detection logic
        ...
```

### Integration Testing

```bash
# Run Shi Fu integration tests
pytest tests/unit/tools/test_shifu.py -v
# Expected: 21 tests passing
```

## 📖 Related Documentation

- [[Shi Fu Phase 1 Implementation]] - Core architecture
- [[Shi Fu Meta-Architecture Intelligence]] - Meta-agent design
- [[Quality Ecosystem Vision]] - Overall quality strategy
- `.clinerules` - Development standards (Section 8)

## 🤝 Quality Ecosystem

Shi Fu completes the quality trinity:

```
┌─────────────┐
│ Feng Shui   │ → Code Architecture Quality
│  (风水)      │    • DI violations
└──────┬──────┘    • SOLID principles
       │           • Module coupling
       ↓
┌─────────────┐
│   Shi Fu    │ → Cross-Domain Intelligence
│   (师傅)     │    • Finds correlations
└──────┬──────┘    • Identifies root causes
       │           • Holistic insights
       ↓
┌─────────────┐
│   Gu Wu     │ → Test Quality Intelligence
│   (顾武)     │    • Flaky detection
└─────────────┘    • Coverage gaps
                   • Performance tracking
```

**Together they provide**:
- **Complete Picture**: See both code and test quality
- **Root Cause Analysis**: Find underlying issues, not symptoms
- **Efficient Fixes**: One fix solves multiple problems
- **Proactive Guidance**: Prevent issues before they compound

## 📜 Philosophy

> "The student sees problems. The master sees patterns. The student fixes symptoms. The master heals roots. Code and tests are yin and yang - they must balance. When code has DI violations (yang imbalance), tests become flaky (yin imbalance). The master restores balance by healing the root."

**Core Principles**:
- 🔗 **Holistic View**: Code and tests are interconnected
- 🎯 **Root Causes**: Fix one, heal many
- 🧘 **Balance**: Maintain equilibrium across domains
- 🎓 **Wisdom**: Guide with understanding, not commands
- 📚 **Learning**: Each insight includes WHY + HOW + VALUE

## 🎓 When to Use Shi Fu

### Use Shi Fu When:

1. ✅ User mentions "quality ecosystem", "holistic view"
2. ✅ Both Feng Shui and Gu Wu show issues (potential correlation)
3. ✅ User asks "why are tests flaky?"
4. ✅ Weekly quality review sessions
5. ✅ Before major refactoring (assess current state)
6. ✅ After implementing features (validate no quality degradation)
7. ✅ Starting work session (ecosystem health baseline)

### Don't Use Shi Fu When:

- ❌ Only code issues (use Feng Shui directly)
- ❌ Only test issues (use Gu Wu directly)
- ❌ Every commit (it's strategic, not tactical)

## 🔧 Integration

### Automatic Session Start

Shi Fu runs automatically at session start via Cline integration:

```python
# tools/shifu/cline_integration.py
# Checks weekly + presents recommendations
```

**AI Workflow**:
1. AI starts session
2. Runs `python -m tools.shifu --session-start`
3. Shi Fu checks if analysis needed (7 days)
4. If patterns found, AI presents to user
5. User decides whether to address immediately

### PROJECT_TRACKER.md Updates

Shi Fu automatically adds HIGH priority items:

```markdown
## ACTIVE TASKS

### [NEW] WP-XXX: Fix DI Violations → Flaky Tests
**Priority**: P1 (HIGH - Shi Fu detected)
**Effort**: 4-6 hours
**Status**: Blocked (requires architecture refactor)
**Context**: Shi Fu detected correlation (confidence: 0.9)
  - 10 DI violations in knowledge_graph_v2
  - 5 flaky tests in same module
  - Fix DI violations → flaky tests heal automatically
```

### Manual Override

Bypass automatic weekly check:

```bash
# Force analysis even if < 7 days
python -m tools.shifu --weekly-analysis

# Quick check without full analysis
python -m tools.shifu --health-check
```

## 📊 Example Scenarios

### Scenario 1: DI Violations Causing Flaky Tests

**Before Shi Fu**:
```
Developer: "Tests are flaky, spending hours debugging..."
Dev fixes: Flaky tests one-by-one (6 hours work)
Result: Symptoms treated, root cause remains
```

**With Shi Fu**:
```
Shi Fu: "DI violations CAUSE flaky tests (confidence: 0.9)"
Dev fixes: 10 DI violations (2 hours work)
Result: Root cause fixed, 5 flaky tests heal automatically
Savings: 4 hours + more stable codebase
```

### Scenario 2: Complexity Causing Low Coverage

**Before Shi Fu**:
```
Developer: "Coverage is low, need more tests..."
Dev adds: More test cases (4 hours)
Result: Coverage improves slightly, code still complex
```

**With Shi Fu**:
```
Shi Fu: "High complexity causes low coverage (confidence: 0.85)"
Dev refactors: Simplify complex functions (3 hours)
Result: Code cleaner, coverage rises naturally, easier to maintain
Benefit: Better code + better tests from one fix
```

## 🎓 Teaching Generation

### Teaching Structure

Each teaching includes:

1. **Pattern** - What correlation was detected
2. **Evidence** - Concrete metrics from both domains
3. **Confidence** - How certain (0.0-1.0)
4. **Priority** - Urgency level (URGENT/HIGH/MEDIUM/LOW)
5. **Wisdom** - Core insight/lesson
6. **Action** - Specific steps to take
7. **Impact** - Expected improvements

### Example Teaching

```
🎓 TEACHING #1 (URGENT - Confidence: 0.9)

Pattern: DI Violations → Flaky Tests
Module: knowledge_graph_v2

Evidence:
  Feng Shui: 10 DI violations detected
  Gu Wu: 5 flaky tests (scores: 0.7-0.9)
  
Wisdom:
  "Hardwired dependencies create non-deterministic behavior in tests.
   When code reaches into global state, tests cannot control that state.
   Fix the architectural issue (DI), and test stability follows."

Action:
  1. Refactor 10 DI violations to use dependency injection
  2. Run tests to verify flakiness scores improve
  3. Expected: Flakiness scores drop to < 0.3

Impact:
  - Code: +8 architecture score
  - Tests: -5 flaky tests (auto-heal)
  - Overall: +5-10 ecosystem score
  - Time savings: 4-6 hours debugging eliminated
```

## 📚 Advanced Usage

### Python API

```python
from tools.shifu.shifu import ShiFu

# Create Shi Fu instance
shifu = ShiFu()

# Generate weekly analysis
teachings = shifu.generate_weekly_analysis()

# Check ecosystem health
health = shifu.get_ecosystem_health()
print(f"Ecosystem Score: {health['overall_score']}/100")

# Get specific pattern
from tools.shifu.patterns.di_flakiness import DIFlakinessPattern
pattern = DIFlakinessPattern()
correlation = pattern.detect(fengshui_data, guwu_data)
```

### Custom Patterns

Extend Shi Fu with custom correlation detection:

```python
from tools.shifu.patterns.base_pattern import BasePattern
from dataclasses import dataclass

@dataclass
class MyCustomPattern(BasePattern):
    """Detect custom cross-domain correlation"""
    
    def detect(self, fengshui_data, guwu_data):
        # Custom detection logic
        feng_shui_issue = self.analyze_code(fengshui_data)
        guwu_issue = self.analyze_tests(guwu_data)
        
        if self.correlated(feng_shui_issue, guwu_issue):
            return {
                'detected': True,
                'confidence': 0.85,
                'priority': 'HIGH',
                'wisdom': 'Your wisdom here',
                ...
            }
        return {'detected': False}
```

## 🔍 Troubleshooting

### No Patterns Detected

If Shi Fu reports healthy but you know issues exist:
- Run Feng Shui: `python -m tools.fengshui analyze`
- Run Gu Wu: `python -m tools.guwu intelligence`
- Both must have recent metrics (< 7 days)
- Check confidence thresholds (may need adjustment)

### Stale Data

If "Last analysis: 30 days ago":
```bash
# Force fresh analysis
python -m tools.shifu --weekly-analysis
```

### Missing Metrics

If "No Feng Shui/Gu Wu data found":
1. Run Feng Shui first: `python -m tools.fengshui analyze`
2. Run Gu Wu first: `python -m tools.guwu run`
3. Re-run Shi Fu: `python -m tools.shifu --session-start`

## 📖 Related Documentation

- [[Shi Fu Phase 1 Implementation]] - Core architecture (v4.2)
- [[Shi Fu Meta-Architecture Intelligence]] - Phase 3+ design
- [[Quality Ecosystem Vision]] - Overall strategy
- `.clinerules` - Development standards (Section 8)

## 🤝 Contributing

When extending Shi Fu:

1. Add new pattern in `tools/shifu/patterns/`
2. Extend base pattern class
3. Register in correlation engine
4. Add tests in `tests/unit/tools/shifu/`
5. Update documentation

**Example Pattern Structure**:
```
tools/shifu/patterns/
├── base_pattern.py        # Base class
├── di_flakiness.py        # DI → Flaky
├── complexity_coverage.py # Complexity → Coverage
├── security_gaps.py       # Security → Test Gaps
├── performance_timing.py  # Performance → Slow Tests
└── module_health.py       # Module → Test Health
```

---

**Version**: 4.8 (Phase 8 Complete)  
**Last Updated**: 2026-02-12  
**License**: MIT