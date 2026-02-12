# Gu Wu + Feng Shui Integration Architecture

**Date**: 2026-02-08  
**Status**: FUTURE ROADMAP  
**Question**: "Will Gu Wu integrate via the orchestrator?"

---

## 🎯 Answer: YES - Via Feng Shui Orchestrator

The **Feng Shui Orchestrator** will be the central hub for both code quality (Feng Shui agents) and test quality (Gu Wu integration).

---

## 🏗️ Current Architecture (v4.9)

```
┌──────────────────────────────────────────────────┐
│  QUALITY ECOSYSTEM                               │
├──────────────────────────────────────────────────┤
│                                                  │
│  Feng Shui (Code Quality) 🔧                    │
│  ├── 6 Specialized Agents                       │
│  │   ├── ArchitectAgent                         │
│  │   ├── SecurityAgent                          │
│  │   ├── UXArchitectAgent                       │
│  │   ├── PerformanceAgent                       │
│  │   ├── FileOrgAgent                           │
│  │   └── DocumentationAgent                     │
│  └── Orchestrator (parallel execution)          │
│                                                  │
│  Gu Wu (Test Quality) 🧪                        │
│  ├── Intelligence Hub                           │
│  │   ├── Recommendations Engine                 │
│  │   ├── Dashboard                              │
│  │   └── Predictive Analytics                   │
│  └── Test Execution (pytest)                    │
│                                                  │
│  Shi Fu (Meta-Intelligence) 🧘                  │
│  ├── Observes Feng Shui + Gu Wu                │
│  ├── Finds cross-domain correlations           │
│  └── Provides holistic wisdom                   │
│                                                  │
└──────────────────────────────────────────────────┘

**Current State**: Feng Shui and Gu Wu work independently
**Integration Point**: Shi Fu correlates findings post-execution
```

---

## 🚀 Future Integration (Roadmap)

### **Phase 1: Gu Wu Agent in Feng Shui Orchestrator** ⏳

Add Gu Wu as the **7th specialized agent** in Feng Shui orchestrator:

```python
# tools/fengshui/agents/orchestrator.py (FUTURE)

class FengShuiOrchestrator:
    def __init__(self):
        self.agents = [
            ArchitectAgent(),
            SecurityAgent(),
            UXArchitectAgent(),
            PerformanceAgent(),
            FileOrganizationAgent(),
            DocumentationAgent(),
            GuWuTestAgent()  # NEW: Test quality agent
        ]
```

**GuWuTestAgent Responsibilities**:
- Analyze test coverage (via Gu Wu Intelligence Hub)
- Detect flaky tests
- Identify slow tests
- Find gaps in test pyramid (70/20/10 ratio)
- Generate test recommendations

**Benefits**:
- Single entry point: `orchestrator.analyze_module(module_path)`
- Parallel execution: 7 agents run simultaneously (7x speedup potential)
- Unified report: Code quality + Test quality in one view
- Conflict detection: E.g., "Security issue but no security test"

---

### **Phase 2: Feng Shui → Gu Wu Feedback Loop** ⏳

**Bidirectional Integration**:

```
Feng Shui Finds Issues → Gu Wu Generates Tests
    ↓
1. Feng Shui: "DI violation in data_products_v2"
2. Orchestrator: Signals Gu Wu agent
3. Gu Wu: Generates test to prevent regression
4. Result: Issue fixed + test prevents future occurrence
```

**Example Workflow**:
```python
# Feng Shui detects issue
orchestrator.analyze_module("data_products_v2")
# → Finding: "Facade not using repository factory (HIGH)"

# Gu Wu generates test automatically
guwu_agent = orchestrator.get_agent("GuWuTestAgent")
test_code = guwu_agent.generate_regression_test(
    issue_type="FACADE_NOT_USING_FACTORY",
    module="data_products_v2"
)
# → Creates: tests/unit/modules/data_products_v2/test_facade_factory.py

# Next analysis: Issue fixed + test validates
```

---

### **Phase 3: Predictive Quality Gate** ⏳

**Pre-Deployment Validation** via unified orchestrator:

```bash
# Single command validates EVERYTHING
python -m tools.fengshui.react_agent --module data_products_v2 --pre-deploy

# Orchestrator runs 7 agents in parallel:
# 1. ArchitectAgent: Check DI, patterns
# 2. SecurityAgent: Check vulnerabilities
# 3. UXArchitectAgent: Check Fiori compliance
# 4. PerformanceAgent: Check efficiency
# 5. FileOrgAgent: Check structure
# 6. DocumentationAgent: Check docs
# 7. GuWuTestAgent: Check test quality, run tests

# Output: Unified health score (0-100)
# - Code Health: 95/100 (Feng Shui agents)
# - Test Health: 88/100 (Gu Wu agent)
# - Overall: 92/100
# - Gate: PASS (threshold: 85)
```

**Benefits**:
- Single command replaces multiple tool runs
- Comprehensive validation (code + tests)
- Fast feedback (parallel execution)
- CI/CD ready (exit code 0/1 based on threshold)

---

## 📊 Architecture Comparison

### **Current (v4.9)**:
```
Feng Shui → Code analysis (6 agents)
   ↓
Gu Wu → Test analysis (separate)
   ↓
Shi Fu → Correlates findings (post-execution)
   ↓
User → Reviews 3 separate reports
```

**Time**: ~10 seconds (sequential tools)  
**Reports**: 3 separate outputs  
**Integration**: Manual correlation via Shi Fu

---

### **Future (Orchestrator Integration)**:
```
Orchestrator → 7 agents in parallel
   ├── Feng Shui agents (1-6): Code quality
   └── Gu Wu agent (7): Test quality
      ↓
Unified Report → Code + Test health in one view
   ↓
Auto-Actions → Gu Wu generates tests for Feng Shui findings
   ↓
User → Reviews 1 comprehensive report
```

**Time**: ~3-5 seconds (parallel execution)  
**Reports**: 1 unified output  
**Integration**: Automatic test generation

---

## 🎯 Integration Points

### **What Gu Wu Brings to Orchestrator**:

1. **Test Coverage Analysis**
   - Identifies untested code paths
   - Maps tests to architectural layers
   - Validates test pyramid ratio

2. **Test Health Scoring**
   - Flaky test detection (0.0-1.0 score)
   - Slow test identification (>5s threshold)
   - Test complexity analysis

3. **Intelligent Test Generation**
   - Creates regression tests for Feng Shui findings
   - Generates unit tests for uncovered code
   - Proposes integration tests for module boundaries

4. **Test Execution**
   - Runs test suite during analysis
   - Provides real-time feedback
   - Integrates with CI/CD pipelines

---

## 🚀 Migration Path

### **Step 1: Create GuWuTestAgent** (Future)
```python
# tools/fengshui/agents/guwu_test_agent.py

from tools.guwu.intelligence.intelligence_hub import IntelligenceHub

class GuWuTestAgent:
    """Gu Wu integration as Feng Shui agent"""
    
    def analyze(self, module_path):
        """Analyze test quality via Gu Wu Intelligence Hub"""
        hub = IntelligenceHub()
        findings = []
        
        # 1. Check test coverage
        coverage = hub.get_coverage_gaps(module_path)
        findings.extend(coverage.to_findings())
        
        # 2. Detect flaky tests
        flaky = hub.get_flaky_tests(module_path)
        findings.extend(flaky.to_findings())
        
        # 3. Identify slow tests
        slow = hub.get_slow_tests(module_path)
        findings.extend(slow.to_findings())
        
        return findings
```

### **Step 2: Register in Orchestrator** (Future)
```python
# tools/fengshui/agents/orchestrator.py

from .guwu_test_agent import GuWuTestAgent

class FengShuiOrchestrator:
    def __init__(self):
        self.agents = [
            # ... existing 6 agents ...
            GuWuTestAgent()  # Add as 7th agent
        ]
```

### **Step 3: Update Usage** (Future)
```bash
# Before (separate tools):
python -m tools.fengshui.react_agent --module data_products_v2
pytest tests/unit/modules/data_products_v2/

# After (unified orchestrator):
python -m tools.fengshui.react_agent --module data_products_v2 --include-tests
# Runs Feng Shui + Gu Wu in single command
```

---

## 💡 Benefits of Orchestrator Integration

1. **Single Entry Point**
   - One command for complete quality analysis
   - Simpler CI/CD integration
   - Easier for developers to use

2. **Faster Execution**
   - Parallel agent execution (7x potential speedup)
   - Shared module context (no re-parsing)
   - Optimized resource usage

3. **Deeper Intelligence**
   - Cross-domain correlations (code ↔ tests)
   - Automatic test generation
   - Holistic quality scoring

4. **Better Developer Experience**
   - Unified report format
   - Clear action items
   - Integrated fix workflows

---

## 🎓 Design Principle

**"The orchestrator is the hub. Agents are the spokes. Gu Wu is a spoke, not a separate wheel."**

- ✅ Feng Shui Orchestrator = Central hub
- ✅ 6 Code Quality Agents = Specialized spokes
- ✅ 1 Test Quality Agent (Gu Wu) = 7th spoke
- ✅ Unified reports, parallel execution, integrated workflows

**Why This Matters**:
- Avoids tool sprawl (multiple entry points)
- Leverages existing orchestrator infrastructure
- Maintains clean separation of concerns (agents are pluggable)
- Enables future expansion (8th agent, 9th agent, etc.)

---

## 📝 Current State vs Future State

### **Today (v4.9)**:
```bash
# Validate module quality (separate commands)
python -m tools.fengshui.react_agent --module data_products_v2
pytest tests/unit/modules/data_products_v2/
python -m tools.guwu.intelligence.intelligence_hub

# 3 separate tool invocations
# Manual correlation of findings
```

### **Future (Orchestrator Integration)**:
```bash
# Validate module quality (single command)
python -m tools.fengshui.react_agent --module data_products_v2 --complete

# Output:
# ✅ ArchitectAgent: 95/100 (0 violations)
# ✅ SecurityAgent: 100/100 (0 vulnerabilities)
# ✅ UXArchitectAgent: 90/100 (2 suggestions)
# ✅ PerformanceAgent: 88/100 (3 optimizations)
# ✅ FileOrgAgent: 100/100 (perfect structure)
# ✅ DocumentationAgent: 85/100 (missing 2 docstrings)
# ✅ GuWuTestAgent: 92/100 (2 flaky tests, 88% coverage)
#
# Overall Health: 93/100
# Status: PASS (threshold: 85)
#
# Recommendations:
# 1. Fix 2 flaky tests (GuWuTestAgent)
# 2. Add docstrings for X, Y (DocumentationAgent)
# 3. Optimize query in Z (PerformanceAgent)
```

**One command. Complete picture. Actionable insights.**

---

## ✅ Summary

**Question**: "Will Gu Wu integrate via the orchestrator?"  
**Answer**: **YES** - That's the correct architecture!

**Current State**: Gu Wu works independently (Intelligence Hub)  
**Future State**: Gu Wu as 7th agent in Feng Shui Orchestrator  
**Benefits**: Unified entry point, faster execution, deeper intelligence  
**Timeline**: Future roadmap (Phase 1, 2, 3)

**The Vision**: One orchestrator, seven agents, complete quality validation. 🎯