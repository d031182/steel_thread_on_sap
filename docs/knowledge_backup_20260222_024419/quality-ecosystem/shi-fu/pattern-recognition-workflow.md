# Shi Fu Pattern Recognition & Feng Shui Enhancement Workflow

**Created**: 2026-02-12  
**Purpose**: Explain how Shi Fu detects new patterns and triggers Feng Shui improvements  
**Status**: ✅ PRODUCTION (Currently Active)

---

## 🎯 The Question

**"How does Shi Fu recognize new patterns which can be triggered to Feng Shui?"**

---

## 📊 Current Architecture (Production - v4.8)

### 3-Layer Intelligence System

```
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 1: DATA SOURCES                    │
├─────────────────────────────────────────────────────────────┤
│  Feng Shui Analysis  │  Gu Wu Metrics   │  Historical Data │
│  (code quality)      │  (test quality)  │  (growth.db)    │
└──────────────┬──────────────┬────────────────┬──────────────┘
               │              │                │
               ▼              ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│              LAYER 2: PATTERN DETECTION ENGINE              │
├─────────────────────────────────────────────────────────────┤
│  CorrelationEngine (tools/shifu/correlation_engine.py)     │
│                                                             │
│  Uses 5 Specialized Pattern Detectors:                     │
│  1. DIFlakinessPattern       (DI violations → flaky tests) │
│  2. ComplexityCoveragePattern (complexity → low coverage)  │
│  3. SecurityGapsPattern      (security → missing tests)    │
│  4. PerformanceTimingPattern (perf issues → slow tests)    │
│  5. ModuleHealthPattern      (violations → test failures)  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│            LAYER 3: WISDOM GENERATION & ACTION              │
├─────────────────────────────────────────────────────────────┤
│  WisdomGenerator (tools/shifu/wisdom_generator.py)         │
│  - Prioritizes patterns (URGENT/HIGH/MEDIUM/LOW)           │
│  - Generates actionable teachings                           │
│  - Updates PROJECT_TRACKER.md                               │
│  - Recommends Feng Shui enhancements                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 How Pattern Detection Works (Real-Time)

### Step 1: Weekly Analysis Trigger

**Automatic** (via Cline Integration):
```bash
# Runs automatically at session start (if 7+ days since last analysis)
python -m tools.shifu --session-start
```

**Manual** (developer-initiated):
```bash
# Force weekly analysis anytime
python -m tools.shifu --weekly-analysis
```

### Step 2: Data Collection

```python
# In tools/shifu/shifu.py (main orchestrator)

# 1. Collect Feng Shui data
fengshui_interface = FengShuiInterface()
fengshui_data = fengshui_interface.get_latest_analysis()
# Returns: {
#   'di_violations': 10,
#   'security_issues': 5,
#   'performance_issues': 3,
#   'module_scores': {...}
# }

# 2. Collect Gu Wu data
guwu_interface = GuWuInterface()
guwu_data = guwu_interface.get_latest_metrics()
# Returns: {
#   'flaky_tests': 5,
#   'coverage': 0.82,
#   'slow_tests': 3,
#   'test_failures': 2
# }

# 3. Pass to Correlation Engine
correlation_engine = CorrelationEngine()
patterns = correlation_engine.detect_patterns(fengshui_data, guwu_data)
```

### Step 3: Pattern Detection (Parallel Execution)

```python
# In tools/shifu/correlation_engine.py

# Each pattern detector runs independently
for detector in self.pattern_detectors:  # 5 detectors
    match = detector.detect(fengshui_data, guwu_data)
    if match:
        correlations.append(match)
```

**Example: DI → Flaky Pattern Detection**

```python
# In tools/shifu/patterns/di_flakiness.py

class DIFlakinessPattern(BasePattern):
    """Detects correlation between DI violations and flaky tests"""
    
    def detect(self, fengshui_data: Dict, guwu_data: Dict) -> Optional[PatternMatch]:
        # Extract relevant data
        di_violations = fengshui_data.get('di_violations', 0)
        flaky_tests = guwu_data.get('flaky_tests', 0)
        
        # Check if pattern exists (both present)
        if di_violations > 0 and flaky_tests > 0:
            # Calculate correlation strength
            correlation = min(di_violations, flaky_tests) / max(di_violations, flaky_tests)
            
            # If strong correlation (0.5+), create match
            if correlation >= 0.5:
                return PatternMatch(
                    pattern_name="DI Violations → Flaky Tests",
                    confidence=correlation,
                    severity="URGENT",
                    fengshui_evidence={'di_violations': di_violations},
                    guwu_evidence={'flaky_tests': flaky_tests},
                    root_cause="Hardwired dependencies cause non-deterministic test behavior",
                    recommendation="Fix DI violations using Feng Shui auto-fix",
                    estimated_effort="2-4 hours",
                    combined_value="Both quality AND productivity improvement"
                )
        
        return None  # No pattern detected
```

### Step 4: Wisdom Generation

```python
# In tools/shifu/wisdom_generator.py

def generate_teachings(patterns: List[PatternMatch]) -> List[Teaching]:
    """Transform patterns into actionable teachings"""
    
    teachings = []
    for pattern in patterns:
        teaching = Teaching(
            title=pattern.pattern_name,
            priority=pattern.severity,
            root_cause=pattern.root_cause,
            action=pattern.recommendation,
            effort=pattern.estimated_effort,
            value=pattern.combined_value,
            confidence=pattern.confidence
        )
        teachings.append(teaching)
    
    # Sort by priority (URGENT first)
    return sorted(teachings, key=lambda t: priority_score(t.priority))
```

---

## 🚀 How Shi Fu Triggers Feng Shui Enhancements

### Two Mechanisms:

### 1. **Automatic: Via Correlation Patterns** ⭐ CURRENT (Production)

**When it happens**: During weekly analysis, Shi Fu detects patterns and recommends Feng Shui auto-fix

**Example Workflow**:

```
Week 1: User makes changes
  ↓
Week 2: Shi Fu runs weekly analysis
  ↓
Correlation Engine detects:
  - Feng Shui: 10 DI violations
  - Gu Wu: 5 flaky tests
  - Pattern: DI → Flaky (confidence: 0.90)
  ↓
Wisdom Generator creates teaching:
  "Fix 10 DI violations → 5 flaky tests heal automatically"
  ↓
Shi Fu presents recommendation:
  "Run: python -m tools.fengshui fix --target-score 95"
  ↓
User approves
  ↓
Feng Shui ReAct Agent executes fixes autonomously
  ↓
Result: Both code and tests improve together
```

**Key Point**: Shi Fu **recommends** Feng Shui run, but doesn't trigger it automatically (user approval required)

---

### 2. **Manual: Via Enhancement Proposer** ⭐ CONSULTANT MODE

**When it happens**: User reports "Feng Shui missed X" → Shi Fu generates enhancement proposal

**Example Workflow**:

```
User: "Feng Shui missed empty /app folder"
  ↓
Shi Fu Enhancement Proposer activates
  ↓
Step 1: Route to Agent
  - Analyzes issue: "empty folder"
  - Routes to: FileOrganizationAgent (best fit)
  - Confidence: 0.85 (high)
  ↓
Step 2: Generate Detector Plan
  - Detector name: _detect_empty_directories
  - What it checks: Folders with only artifacts (__pycache__, .DS_Store)
  - How it works: Recursive scan → flag if no source files
  ↓
Step 3: Create Implementation Plan
  - Files to modify: file_organization_agent.py
  - Files to create: test_detect_empty_directories.py
  - Effort: 2-2.5 hours
  - Priority: P2 (MEDIUM)
  ↓
Step 4: Generate Proposal Document
  - Saved to: docs/feng-shui-proposals/20260212-FILE-detector_empty_directories.md
  - Includes: Complete code skeleton, tests, acceptance criteria
  ↓
User reviews proposal
  ↓
If approved: AI implements detector
  ↓
Feng Shui gains new capability!
```

**Usage**:
```bash
# Generate proposal for missing detector
python -m tools.shifu.meta.enhancement_proposer "Empty /app folder with only __pycache__"

# Output:
# ✅ Proposal Generated!
#    ID: 20260212-FILE-empty_directories
#    Agent: FileOrganizationAgent
#    Detector: _detect_empty_directories
#    Priority: P2 (MEDIUM)
#    Effort: 2-2.5 hours
# 
# 📄 Proposal saved to: docs/feng-shui-proposals/20260212-FILE-empty_directories.md
```

---

## 🔄 Complete Pattern Recognition Lifecycle

### Phase 1: Discovery (How Patterns Are Found)

**Method A: Correlation Analysis** (Weekly)
```
Shi Fu observes:
  - Feng Shui findings (violations, scores)
  - Gu Wu metrics (flaky, coverage, speed)
  - Historical trends (growth.db)

If correlation detected (confidence ≥ 0.5):
  → Create PatternMatch
  → Generate Teaching
  → Recommend action
```

**Method B: User Report** (Ad-hoc)
```
User says: "Feng Shui missed X"
  ↓
Enhancement Proposer:
  - Routes to correct agent
  - Validates fit
  - Generates proposal
  ↓
User reviews and approves
```

**Method C: Meta-Architecture Analysis** (Proposed - Phase 6)
```
Shi Fu runs Feng Shui ON Feng Shui itself
  ↓
Detects: Feng Shui violates patterns it enforces
  ↓
Example: "Feng Shui detects Service Layer violations,
          but has business logic in routes itself!"
  ↓
Self-improvement proposal generated
```

---

### Phase 2: Validation (Is This a Real Pattern?)

```python
# In pattern detector (e.g., di_flakiness.py)

def detect(self, fengshui_data, guwu_data):
    # 1. Check threshold: Both issues present?
    if di_violations < THRESHOLD or flaky_tests < THRESHOLD:
        return None  # Not enough evidence
    
    # 2. Calculate correlation strength
    correlation = calculate_correlation(di_violations, flaky_tests)
    
    # 3. Check confidence threshold
    if correlation < 0.5:  # Weak correlation
        return None
    
    # 4. Return match only if strong correlation
    return PatternMatch(...)
```

**Confidence Levels**:
- **0.9+ (Very High)**: Definitely correlated (trigger immediately)
- **0.7-0.9 (High)**: Likely correlated (high priority recommendation)
- **0.5-0.7 (Medium)**: Possibly correlated (medium priority)
- **<0.5 (Low)**: Not enough evidence (don't report)

---

### Phase 3: Prioritization (What to Act On First?)

```python
# In tools/shifu/wisdom_generator.py

def prioritize_patterns(patterns: List[PatternMatch]) -> List[Teaching]:
    # Sort by:
    # 1. Severity (URGENT > HIGH > MEDIUM > LOW)
    # 2. Confidence (0.9 > 0.7 > 0.5)
    # 3. Impact score (affected modules count)
    
    priority_map = {
        'URGENT': 0,   # Security + Flaky (user pain + risk)
        'HIGH': 1,     # DI violations, Complexity
        'MEDIUM': 2,   # Performance, Module health
        'LOW': 3       # Minor issues
    }
    
    sorted_patterns = sorted(
        patterns,
        key=lambda p: (
            priority_map[p.severity],
            -p.confidence,
            -p.impact_score
        )
    )
    
    return [create_teaching(p) for p in sorted_patterns]
```

---

### Phase 4: Action Recommendation (How to Fix?)

**Shi Fu Generates 3 Types of Recommendations**:

#### Type 1: Run Existing Feng Shui Capability ⭐ MOST COMMON
```
Pattern Detected: "DI Violations → Flaky Tests" (confidence: 0.9)

Recommendation:
  "Fix DI violations using Feng Shui autonomous agent"
  
Command:
  python -m tools.fengshui fix --target-score 95
  
Expected Result:
  - Feng Shui: 10 violations → 0 violations
  - Gu Wu: 5 flaky tests → 2 flaky tests (60% improvement)
  
Estimated Time: 2-4 hours (autonomous execution)
```

#### Type 2: Propose New Feng Shui Detector ⭐ ENHANCEMENT MODE
```
User Report: "Feng Shui missed empty /app folder"

Shi Fu Analysis:
  - Issue type: File organization
  - Best agent: FileOrganizationAgent
  - Detector needed: _detect_empty_directories
  - Confidence: 0.85 (high fit)

Proposal Generated:
  docs/feng-shui-proposals/20260212-FILE-empty_directories.md
  
Proposal Includes:
  - Complete implementation plan
  - Code skeleton with examples
  - Unit test scenarios
  - Effort estimate (2-2.5 hours)
  - Priority (P2 - MEDIUM)

User Decision:
  ✅ Approve → AI implements detector
  ❌ Reject → Close proposal
  ⚠️ Modify → Refine requirements
```

#### Type 3: Meta-Architecture Improvement (Proposed - Phase 6)
```
Shi Fu Self-Reflection: "Feng Shui violates patterns it enforces"

Example Finding:
  - Feng Shui detects: Service Layer violations in apps
  - Shi Fu detects: Feng Shui has business logic in routes
  - Irony: "Physician, heal thyself!"

Recommendation:
  - Pattern: Service Layer (from Cosmic Python)
  - Apply to: tools/fengshui/violation_tracker.py
  - Benefit: Credibility + quality
  - Teaching: "Practice what you preach"

Status: PROPOSAL (Phase 6 - not yet implemented)
```

---

## 🧠 Intelligence: How Shi Fu "Learns" New Patterns

### Current System (v4.8): Pattern Library

**Fixed Pattern Detectors** (5 currently):
```python
# tools/shifu/patterns/__init__.py

from .di_flakiness import DIFlakinessPattern
from .complexity_coverage import ComplexityCoveragePattern
from .security_gaps import SecurityGapsPattern
from .performance_timing import PerformanceTimingPattern
from .module_health import ModuleHealthPattern

# Correlation Engine uses these detectors
pattern_detectors = [
    DIFlakinessPattern(),
    ComplexityCoveragePattern(),
    SecurityGapsPattern(),
    PerformanceTimingPattern(),
    ModuleHealthPattern()
]
```

**How to Add New Pattern** (Developer workflow):

1. **Create Pattern Detector**:
```python
# tools/shifu/patterns/new_pattern.py

class NewCorrelationPattern(BasePattern):
    """Detects X in code correlates with Y in tests"""
    
    def detect(self, fengshui_data, guwu_data):
        # Your detection logic here
        if condition_met:
            return PatternMatch(...)
        return None
```

2. **Register in __init__.py**:
```python
# tools/shifu/patterns/__init__.py
from .new_pattern import NewCorrelationPattern

# Add to list
pattern_detectors.append(NewCorrelationPattern())
```

3. **Shi Fu automatically uses it** (no other changes needed!)

---

### Future System (Proposed): Dynamic Pattern Learning

**Machine Learning Approach** (Phase 7+):

```python
# Future: Shi Fu learns patterns from historical data

class AdaptivePatternDetector:
    """Learns new correlation patterns from historical data"""
    
    def learn_from_history(self):
        """Analyze growth.db to find new patterns"""
        
        # 1. Query historical correlations
        history = query_growth_db("""
            SELECT 
                feng_shui_metric,
                guwu_metric,
                correlation_coefficient
            FROM weekly_analyses
            WHERE date > DATE('now', '-6 months')
        """)
        
        # 2. Find strong correlations (>0.7) not in pattern library
        for row in history:
            if row.correlation > 0.7 and not in_pattern_library(row):
                # New pattern discovered!
                new_pattern = {
                    'fengshui_metric': row.feng_shui_metric,
                    'guwu_metric': row.guwu_metric,
                    'correlation': row.correlation,
                    'confidence': 'HIGH',
                    'discovered': datetime.now()
                }
                
                # 3. Propose adding to pattern library
                self.propose_new_pattern(new_pattern)
```

**Example Discovery**:
```
Shi Fu learns from 6 months of data:
  - "Modules with >3 facades have 2x more integration test failures"
  - Correlation: 0.82 (strong)
  - Not in current 5 patterns
  → Propose: FacadeOverusePattern detector
  → User approves
  → Add to pattern library
  → Shi Fu now detects this automatically!
```

---

## 🎯 Real-World Example: Complete Workflow

### Scenario: User Discovers Feng Shui Gap

**Day 1: Discovery**
```
User: "Feng Shui didn't catch that /app folder is empty (only __pycache__)"

AI: "Let me generate an enhancement proposal using Shi Fu"
```

**Day 1: Proposal Generation** (2 minutes)
```bash
# AI runs Enhancement Proposer
python -m tools.shifu.meta.enhancement_proposer \
  "Empty /app folder containing only __pycache__ subdirectory"

# Output:
✅ Proposal Generated!
   ID: 20260212-FILE-empty_directories
   Agent: FileOrganizationAgent
   Detector: _detect_empty_directories
   Priority: P2 (MEDIUM)
   Effort: 2-2.5 hours

📄 Proposal saved to:
   docs/feng-shui-proposals/20260212-FILE-empty_directories.md
```

**Day 1: User Review** (5 minutes)
```
User reviews proposal:
  ✓ Routes to correct agent (FileOrganizationAgent)
  ✓ Detector name makes sense (_detect_empty_directories)
  ✓ Implementation plan is complete
  ✓ Effort estimate reasonable (2-2.5 hours)
  ✓ Priority appropriate (P2)

User: "Approved! Implement this detector."
```

**Day 2: AI Implementation** (2 hours)
```python
# AI implements detector in FileOrganizationAgent

def _detect_empty_directories(self, module_path: Path) -> List[Finding]:
    """Detect directories with only build artifacts"""
    
    ARTIFACT_FILES = {'__pycache__', '.DS_Store', 'Thumbs.db', '.pytest_cache'}
    findings = []
    
    for dirpath in module_path.rglob('*'):
        if dirpath.is_dir():
            contents = set(item.name for item in dirpath.iterdir())
            
            # Check if only artifacts
            if contents and contents.issubset(ARTIFACT_FILES):
                findings.append(Finding(
                    category="FILE_ORGANIZATION",
                    severity="MEDIUM",
                    message=f"Empty directory (only artifacts): {dirpath}",
                    recommendation="Remove directory or add source files"
                ))
    
    return findings
```

**Day 2: Validation** (30 minutes)
```bash
# AI writes unit tests
pytest tests/unit/tools/fengshui/test_detect_empty_directories.py -v

# AI runs integration test
python -m tools.fengshui analyze --module test_module

# All tests pass ✅
```

**Day 3: Future Use** (Forever)
```
Next time: Feng Shui automatically detects empty directories!

Example:
  python -m tools.fengshui analyze

  Output:
    ⚠️ FILE_ORGANIZATION (MEDIUM)
       Empty directory (only artifacts): /app
       Recommendation: Remove directory or add source files
```

---

## 🎓 The Intelligence Layers

### Layer 1: Pattern Detection (Current - Production)

**What it does**: Detects known patterns (5 types)

**How it works**: Correlation analysis between Feng Shui + Gu Wu data

**Triggers**: Weekly analysis (`--session-start`)

**Output**: Teachings with recommendations

---

### Layer 2: Enhancement Proposals (Current - Production)

**What it does**: Generates proposals for new Feng Shui capabilities

**How it works**: Routes user-reported gaps to correct agent, creates implementation plan

**Triggers**: User reports "Feng Shui missed X"

**Output**: Complete proposal document with code skeleton

---

### Layer 3: Meta-Architecture (Proposed - Phase 6)

**What it does**: Shi Fu analyzes quality tools' own architecture

**How it works**: Runs Feng Shui ON Feng Shui/Gu Wu/Shi Fu

**Triggers**: Meta-analysis command or self-reflection

**Output**: Architecture improvement proposals for quality tools

---

## 📊 Current vs Future Capabilities

### Current (v4.8) - PRODUCTION ✅

| Capability | Status | How It Works |
|------------|--------|--------------|
| **Detect Known Patterns** | ✅ Active | 5 correlation detectors |
| **Generate Teachings** | ✅ Active | Wisdom generator with priority |
| **Recommend Actions** | ✅ Active | "Run python -m tools.fengshui fix" |
| **Enhancement Proposals** | ✅ Active | User reports → AI generates proposal |
| **Auto PROJECT_TRACKER** | ✅ Active | HIGH priority items auto-added |

### Future (Phase 6+) - PROPOSED 🚧

| Capability | Status | How It Would Work |
|------------|--------|-------------------|
| **Learn New Patterns** | 🚧 Proposed | ML analysis of historical data |
| **Meta-Architecture** | 🚧 Proposed | Feng Shui analyzes Feng Shui |
| **Auto-Add Detectors** | 🚧 Proposed | Generate + test + deploy detectors |
| **Self-Improvement** | 🚧 Proposed | Shi Fu improves itself |

---

## 🛠️ For Developers: Adding New Patterns

### Quick Guide

**1. Identify Pattern** (What correlates?)
```
Observation: "Modules with facades have more integration test failures"
```

**2. Create Detector**
```python
# tools/shifu/patterns/facade_integration_pattern.py

from .base_pattern import BasePattern, PatternMatch

class FacadeIntegrationPattern(BasePattern):
    pattern_name = "Facade Complexity → Integration Failures"
    description = "Modules with complex facades have more integration test failures"
    
    def detect(self, fengshui_data, guwu_data):
        facade_count = fengshui_data.get('facade_count', 0)
        integration_failures = guwu_data.get('integration_failures', 0)
        
        if facade_count > 3 and integration_failures > 0:
            correlation = min(facade_count, integration_failures) / max(facade_count, integration_failures)
            
            if correlation >= 0.6:
                return PatternMatch(
                    pattern_name=self.pattern_name,
                    confidence=correlation,
                    severity="HIGH",
                    # ... rest of fields
                )
        return None
```

**3. Register Pattern**
```python
# tools/shifu/patterns/__init__.py
from .facade_integration_pattern import FacadeIntegrationPattern

# Add to exports
__all__ = [..., 'FacadeIntegrationPattern']
```

**4. Test Pattern**
```python
# tests/unit/tools/shifu/test_facade_integration_pattern.py

def test_detects_facade_integration_correlation():
    detector = FacadeIntegrationPattern()
    
    fengshui_data = {'facade_count': 5}
    guwu_data = {'integration_failures': 4}
    
    match = detector.detect(fengshui_data, guwu_data)
    
    assert match is not None
    assert match.confidence >= 0.6
    assert match.severity == "HIGH"
```

**5. Deploy** (Automatic)
```
Shi Fu automatically uses new pattern in next weekly analysis!
No configuration changes needed.
```

---

## 🎯 Summary: The Complete Answer

### How Shi Fu Recognizes New Patterns:

**Automatic Detection** (Weekly):
1. ✅ Collects Feng Shui + Gu Wu data
2. ✅ Runs 5 correlation detectors in parallel
3. ✅ Calculates confidence scores (0.0-1.0)
4. ✅ Filters by threshold (0.5+)
5. ✅ Generates prioritized teachings
6. ✅ Recommends Feng Shui actions

**Manual Enhancement** (On-Demand):
1. ✅ User reports gap: "Feng Shui missed X"
2. ✅ Enhancement Proposer routes to correct agent
3. ✅ Generates complete implementation proposal
4. ✅ User reviews and approves
5. ✅ AI implements new detector
6. ✅ Feng Shui gains new capability

**Future Learning** (Proposed):
1. 🚧 ML analysis of historical data (growth.db)
2. 🚧 Auto-discovery of new correlation patterns
3. 🚧 Self-improvement via meta-architecture analysis

---

## 🔗 Key Files to Explore

**Pattern Detection**:
- `tools/shifu/correlation_engine.py` - Core detection engine
- `tools/shifu/patterns/` - 5 pattern detectors
- `tools/shifu/patterns/base_pattern.py` - Pattern interface

**Enhancement System**:
- `tools/shifu/meta/enhancement_proposer.py` - Proposal generator
- `tools/shifu/meta/agent_registry.py` - Agent routing
- `docs/feng-shui-proposals/` - Generated proposals

**Wisdom Generation**:
- `tools/shifu/wisdom_generator.py` - Teaching creation
- `tools/shifu/cline_integration.py` - AI assistant workflow

---

## 📚 Related Documentation

- [[Quality Ecosystem Vision]] - Overall philosophy
- [[Shi Fu Meta-Architecture]] - Phase 6 proposal (meta-intelligence)
- [Feng Shui Documentation](../feng-shui/) - What patterns Shi Fu can trigger
- [Gu Wu Documentation](../gu-wu/) - Test metrics Shi Fu observes

---

**Version**: 1.0  
**Last Updated**: 2026-02-12  
**Status**: ✅ PRODUCTION (Actively used in weekly analysis)

**Navigation**: [← Back to Shi Fu Documentation](README.md) | [↑ Quality Ecosystem](../README.md)