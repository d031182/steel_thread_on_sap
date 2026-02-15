# Feng Shui Test Coverage Agent - Implementation Plan

**Date**: 2026-02-15  
**Status**: PROPOSED  
**Severity**: ARCHITECTURE (replaces standalone analyzer)

---

## 🎯 OBJECTIVE

Replace standalone `api_contract_analyzer.py` with proper **Test Coverage Agent** integrated into Feng Shui multi-agent system.

---

## 🏗️ ARCHITECTURE

### Current (INCORRECT)
```
tools/fengshui/
├── api_contract_analyzer.py  # ❌ Standalone script
└── agents/
    ├── architect_agent.py
    ├── security_agent.py
    └── ...
```

**Problems**:
- Not integrated with multi-agent system
- Requires manual invocation
- Doesn't follow BaseAgent pattern
- Can't be used by quality gates, ReAct agent, etc.

### Proposed (CORRECT)
```
tools/fengshui/
└── agents/
    ├── architect_agent.py
    ├── security_agent.py
    ├── test_coverage_agent.py  # ✅ NEW - Proper agent
    └── ...
```

**Benefits**:
- ✅ Integrated with `fengshui analyze`
- ✅ Follows BaseAgent pattern
- ✅ Auto-invoked with other agents
- ✅ Works with quality gates
- ✅ Participates in ReAct agent workflow

---

## 📋 IMPLEMENTATION STEPS

### 1. Create Test Coverage Agent

**File**: `tools/fengshui/agents/test_coverage_agent.py`

**Capabilities**:
1. **API Contract Test Detection** (CRITICAL priority)
   - Backend API tests: `tests/test_{module}_backend.py`
   - Frontend API tests: `tests/test_{module}_frontend_api.py`
   - Requires: `@pytest.mark.api_contract` marker
   - Requires: `requests.post/get` (HTTP calls)

2. **General Test Coverage** (HIGH priority)
   - Unit test existence
   - Integration test existence
   - Test file naming conventions

3. **Test Quality** (MEDIUM priority)
   - Proper test structure (Arrange/Act/Assert)
   - Test isolation
   - Mock usage

**Interface**:
```python
class TestCoverageAgent(BaseAgent):
    def analyze_module(self, module_path: Path) -> AgentReport:
        """
        Analyze test coverage for a module
        
        Returns findings:
        - CRITICAL: Missing backend API contract test
        - HIGH: Missing frontend API contract test
        - MEDIUM: Missing unit tests
        - LOW: Test quality issues
        """
        pass
    
    def get_capabilities(self) -> List[str]:
        return [
            "API contract test detection (Gu Wu methodology)",
            "Backend API test validation (@pytest.mark.api_contract)",
            "Frontend API test validation (metadata endpoints)",
            "General test coverage analysis",
            "Test quality assessment"
        ]
```

### 2. Integrate into Orchestrator

**File**: `tools/fengshui/agents/orchestrator.py`

Add TestCoverageAgent to agent ensemble (6 → 7 agents):
```python
from .test_coverage_agent import TestCoverageAgent

agents = [
    ("Architecture", ArchitectAgent),
    ("Security", SecurityAgent),
    ("Performance", PerformanceAgent),
    ("UX", UXArchitectAgent),
    ("FileOrg", FileOrganizationAgent),
    ("Documentation", DocumentationAgent),
    ("TestCoverage", TestCoverageAgent),  # NEW
]
```

### 3. Update CLI

**File**: `tools/fengshui/__main__.py`

Update agent count: "6 agents" → "7 agents"
```python
print("🔍 Running 7 specialized agents in parallel...")
print("   1. Architecture Agent (DI violations, SOLID principles)")
print("   2. Security Agent (hardcoded secrets, SQL injection)")
print("   3. UX Architect Agent (SAP Fiori compliance)")
print("   4. File Organization Agent (structure, obsolete files)")
print("   5. Performance Agent (N+1 queries, caching)")
print("   6. Documentation Agent (README quality, docstrings)")
print("   7. Test Coverage Agent (API contracts, test quality)")  # NEW
```

### 4. Delete Standalone Analyzer

**Delete**:
- `tools/fengshui/api_contract_analyzer.py`
- `test_api_contract_detection.py` (demo script)

**Why**: Replaced by proper agent architecture

### 5. Update Documentation

**File**: `.clinerules` (Development Standards)

Update Feng Shui description:
```
7 Specialized Agents:
  1. Architecture  - DI violations, SOLID principles
  2. Security      - SQL injection, secrets, authentication
  3. UX Architect  - SAP Fiori compliance, UI/UX patterns
  4. FileOrg       - Structure, misplaced files, obsolete code
  5. Performance   - N+1 queries, caching, optimization
  6. Documentation - README quality, docstrings, comments
  7. TestCoverage  - API contracts (Gu Wu), test quality  # NEW
```

---

## 🎯 GU WU METHODOLOGY INTEGRATION

The Test Coverage Agent enforces Gu Wu API-First Contract Testing:

```python
def _check_api_contract_tests(self, module_path: Path) -> List[Finding]:
    """
    Check if module has proper API contract tests
    
    Gu Wu Foundation (Feb 15, 2026):
    "Test the API contract, trust the implementation"
    
    Backend API: Tests /api/{module}/endpoints via HTTP
    Frontend API: Tests /api/modules/frontend-registry
    
    One API test validates entire call chain implicitly:
    Controller → Service → Repository → Database
    """
    findings = []
    
    # Check for backend/api.py
    api_file = module_path / "backend" / "api.py"
    if not api_file.exists():
        return findings  # No API to test
    
    module_name = module_path.name
    
    # Check backend API contract test
    backend_test = Path(f"tests/test_{module_name}_backend.py")
    if not backend_test.exists():
        findings.append(Finding(
            category="Missing Backend API Contract Test",
            severity=Severity.CRITICAL,
            file_path=api_file,
            line_number=None,
            description=f"Module '{module_name}' has API but no backend contract test",
            recommendation=(
                f"CREATE tests/test_{module_name}_backend.py with:\n"
                f"  @pytest.mark.api_contract\n"
                f"  requests.post/get() (HTTP calls)\n"
                f"  Test endpoints as black boxes"
            )
        ))
    else:
        # Verify test has proper markers
        if not self._has_api_contract_marker(backend_test):
            findings.append(Finding(
                category="Invalid API Contract Test",
                severity=Severity.HIGH,
                file_path=backend_test,
                line_number=None,
                description="Backend test missing @pytest.mark.api_contract marker",
                recommendation="Add @pytest.mark.api_contract decorator to test functions"
            ))
    
    # Check frontend API contract test (metadata)
    frontend_test = Path(f"tests/test_{module_name}_frontend_api.py")
    if not frontend_test.exists():
        findings.append(Finding(
            category="Missing Frontend API Contract Test",
            severity=Severity.HIGH,
            file_path=module_path,
            line_number=None,
            description=f"Module '{module_name}' missing frontend metadata test",
            recommendation=(
                f"CREATE tests/test_{module_name}_frontend_api.py to test:\n"
                f"  /api/modules/frontend-registry endpoint\n"
                f"  Module metadata structure"
            )
        ))
    
    return findings
```

---

## 📊 USAGE

### Before (Manual)
```bash
# Manual invocation required
python tools/fengshui/api_contract_analyzer.py
python test_api_contract_detection.py
```

### After (Automatic)
```bash
# Automatically invoked with other agents
python -m tools.fengshui analyze

# Or for specific module
python -m tools.fengshui analyze --module ai_assistant

# Quality gate (includes test coverage)
python -m tools.fengshui gate --module logger
```

**Output Example**:
```
TestCoverageAgent: 🔴 3 CRITICAL issue(s)
   - ai_assistant: Missing backend API contract test
   - logger: Missing backend API contract test
   - logger: Missing frontend API contract test
```

---

## 🎯 VALIDATION

### Test the Agent

**Unit Test**: `tests/unit/tools/fengshui/test_test_coverage_agent.py`
```python
def test_detects_missing_api_contract_tests():
    """Verify agent detects missing API contract tests"""
    agent = TestCoverageAgent()
    
    # Test with module that has API but no tests
    module_path = Path("modules/logger")
    report = agent.analyze_module(module_path)
    
    # Should find CRITICAL findings
    assert report.get_critical_count() >= 1
    assert any("API contract test" in f.description for f in report.findings)

def test_accepts_valid_api_contract_tests():
    """Verify agent accepts modules with proper tests"""
    agent = TestCoverageAgent()
    
    # Test with module that has proper tests
    module_path = Path("modules/ai_assistant")  # Has frontend API test
    report = agent.analyze_module(module_path)
    
    # May have backend gap, but frontend should pass
    frontend_findings = [
        f for f in report.findings 
        if "frontend" in f.description.lower()
    ]
    # Frontend test exists, should not be in findings
    assert len(frontend_findings) == 0
```

### Integration Test

**Run Feng Shui**:
```bash
python -m tools.fengshui analyze --module logger
```

**Expected Output**:
```
TestCoverageAgent: 🔴 2 CRITICAL issue(s)
   - Missing backend API contract test (tests/test_logger_backend.py)
   - Missing frontend API contract test (tests/test_logger_frontend_api.py)
```

---

## ✅ BENEFITS

1. **Architecture**: Proper agent-based design (not standalone script)
2. **Integration**: Works with quality gates, ReAct agent, Shi Fu
3. **Automation**: Auto-invoked with `fengshui analyze`
4. **Consistency**: Follows same pattern as other 6 agents
5. **Ecosystem**: Participates in quality scoring, metrics, etc.

---

## 🚀 MIGRATION PLAN

1. ✅ Create `test_coverage_agent.py`
2. ✅ Update orchestrator to include agent
3. ✅ Update CLI help text (6 → 7 agents)
4. ✅ Delete `api_contract_analyzer.py`
5. ✅ Delete `test_api_contract_detection.py`
6. ✅ Update `.clinerules`
7. ✅ Test with `fengshui analyze`
8. ✅ Commit with detailed explanation

---

## 📝 COMMIT MESSAGE

```
feat: Add Test Coverage Agent to Feng Shui (7th agent)

RATIONALE:
- Standalone api_contract_analyzer.py didn't fit architecture
- Should be integrated agent, not manual script
- Enables automatic API contract test validation

CHANGES:
+ tools/fengshui/agents/test_coverage_agent.py (NEW - 7th agent)
  - Validates API contract tests (Gu Wu methodology)
  - Checks backend/frontend API test coverage
  - Enforces @pytest.mark.api_contract marker
  - Requires requests.post/get (HTTP calls)

~ tools/fengshui/agents/orchestrator.py
  - Added TestCoverageAgent to 7-agent ensemble

~ tools/fengshui/__main__.py
  - Updated help text: 6 agents → 7 agents
  - Added Test Coverage Agent description

- tools/fengshui/api_contract_analyzer.py (DELETED)
  - Replaced by proper agent architecture

- test_api_contract_detection.py (DELETED)
  - Demo script no longer needed

~ .clinerules
  - Updated Feng Shui agent list (7 agents)

INTEGRATION:
- Auto-invoked: python -m tools.fengshui analyze
- Quality gates: python -m tools.fengshui gate --module X
- Parallel execution with other 6 agents

ENFORCEMENT:
API-First Contract Testing (Gu Wu Foundation):
- Backend API: tests/test_{module}_backend.py (CRITICAL)
- Frontend API: tests/test_{module}_frontend_api.py (HIGH)
- Markers: @pytest.mark.api_contract required
- Method: HTTP calls (requests), not internal imports

This completes the proper integration of API contract test
validation into the Feng Shui multi-agent architecture.