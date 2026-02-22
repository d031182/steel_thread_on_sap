# Feng Shui + Gu Wu Workflow Guide

**Created**: 2026-02-15  
**Purpose**: Clarify the correct workflow for using Feng Shui and Gu Wu together  
**Status**: ✅ Production Guide

---

## 🎯 Your Understanding (WITH CORRECTIONS)

### ❌ INCORRECT Understanding

> "user run guwu to run tests and create missing tests in the protocols of fengshui"

**This is WRONG because**:
- ❌ Gu Wu does NOT create tests automatically
- ❌ Gu Wu does NOT run tests (pytest does that)
- ❌ Tests are NOT generated from Feng Shui protocols

### ✅ CORRECT Understanding

**What Gu Wu Actually Does**:
- ✅ **ANALYZES** existing test quality
- ✅ **DETECTS** test gaps and issues
- ✅ **RECOMMENDS** what tests to write
- ✅ **VALIDATES** test methodology compliance

**Who Writes Tests**: **YOU** (the developer or AI assistant)

---

## ✅ CORRECT Workflow (6 Steps)

### Step 1: Run Feng Shui (Code Quality Analysis)

```bash
python -m tools.fengshui analyze --module [module_name]
```

**What Happens**:
- 7 agents analyze code in parallel
- Detects architecture violations, security issues, test gaps
- Generates report: `feng_shui_report_[module].json`

**Output Example**:
```
🔍 Running 7 specialized agents...
   7. Test Coverage Agent ⚠️ (3 issues)
      - Missing API contract test for POST /api/[module]/endpoint
      - Missing @pytest.mark.api_contract marker
      - Internal imports detected (should use HTTP)
```

---

### Step 2: Review Feng Shui Report

**Read the report**:
```bash
# Console output shows summary
# JSON file has details
cat feng_shui_report_[module].json
```

**Note all issues**:
- Architecture violations (DI, SOLID)
- Security issues (SQL injection, secrets)
- **Test coverage gaps** ⭐ IMPORTANT
- Performance problems
- Documentation gaps

---

### Step 3: Fix Code Issues (Manual)

**Fix the issues Feng Shui found**:
```python
# Example: Fix DI violation
# ❌ Before
def my_function():
    db = get_app().connection  # Hardwired

# ✅ After
def my_function(db_connection):
    db = db_connection  # Injected
```

**Write Missing API Contract Tests** ⭐ CRITICAL:
```python
# tests/e2e/app_v2/test_[module]_api_contracts.py

import requests
import pytest

@pytest.mark.e2e
@pytest.mark.api_contract
def test_backend_api_contract():
    """Test: Backend API returns valid contract"""
    # ARRANGE
    url = "http://localhost:5000/api/[module]/endpoint"
    payload = {"key": "value"}
    
    # ACT
    response = requests.post(url, json=payload, timeout=5)
    
    # ASSERT
    assert response.status_code == 200
    assert 'success' in response.json()
```

---

### Step 4: Run Tests (pytest, NOT Gu Wu)

```bash
# Run all tests
pytest tests/ -v

# Or run just API contract tests
pytest tests/ -m api_contract -v
```

**Verify**:
- ✅ All tests passing
- ✅ API contract tests work via HTTP
- ✅ No import errors

---

### Step 5: Run Gu Wu (Test Quality Analysis) - OPTIONAL

```bash
# Analyze test quality
python -m tools.guwu analyze

# Find remaining test gaps
python -m tools.guwu gap_analyzer

# Get intelligent recommendations
python -m tools.guwu intelligence
```

**What Gu Wu Reports**:
- Test quality score
- Remaining coverage gaps
- Flaky test detection
- Performance insights
- Recommendations for improvement

**Note**: This step is OPTIONAL. You can skip to Step 6 if tests are passing.

---

### Step 6: Commit & Push

```bash
git add -A
git commit -m "feat: [description]"
git push origin main

# Optional: Add tag
git tag -a v4.7 -m "Description"
git push origin v4.7
```

---

## 🔧 Tools Comparison

| Tool | Purpose | Automation | Output |
|------|---------|------------|--------|
| **Feng Shui** | Code quality inspector | ✅ Detects issues | Report (what's wrong) |
| **Gu Wu** | Test quality analyzer | ✅ Analyzes tests | Recommendations (what to improve) |
| **pytest** | Test runner | ✅ Runs tests | Pass/Fail results |
| **YOU** | Developer | ❌ Manual fixes | Code & tests |

---

## 🎓 Key Concepts

### Feng Shui = Code Quality Inspector
- **Scans**: All code files
- **Detects**: Architecture violations, security issues, **missing tests**
- **Reports**: Issues with severity levels
- **Does NOT**: Fix code or write tests automatically

### Gu Wu = Test Quality Analyzer
- **Scans**: Test files only
- **Detects**: Test quality issues, coverage gaps, flaky tests
- **Reports**: Recommendations and priorities
- **Does NOT**: Run tests or generate test files

### Gu Wu Methodology = How to Write Good Tests
- ⭐ Test API contracts (backend + frontend)
- ⭐ Use HTTP requests (`requests.post/get`)
- ⭐ Mark with `@pytest.mark.api_contract`
- ⭐ One API test validates entire call chain
- ⭐ DON'T test internal functions explicitly

---

## 📊 Workflow Diagram

```
┌─────────────────────────────────────────────────────────┐
│ STEP 1: Feng Shui Analyze                              │
│ $ python -m tools.fengshui analyze --module [name]     │
│                                                          │
│ Output: feng_shui_report_[module].json                  │
│ ├─ Architecture issues                                  │
│ ├─ Security issues                                      │
│ ├─ Performance issues                                   │
│ └─ TEST COVERAGE GAPS ⭐                                │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 2: Review Report (Manual)                          │
│ Read feng_shui_report_[module].json                     │
│ Note all issues, especially test gaps                   │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 3: Fix Issues (Manual - YOU write code)            │
│ ├─ Fix architecture violations                          │
│ ├─ Fix security issues                                  │
│ └─ WRITE API contract tests ⭐                          │
│    └─ Use requests.post/get (HTTP)                      │
│    └─ Mark @pytest.mark.api_contract                    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 4: Run Tests (pytest)                              │
│ $ pytest tests/ -v                                       │
│                                                          │
│ Verify: ✅ All tests passing                            │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 5: Gu Wu Analysis (OPTIONAL)                       │
│ $ python -m tools.guwu analyze                          │
│ $ python -m tools.guwu gap_analyzer                     │
│                                                          │
│ Output: Test quality insights & recommendations         │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 6: Commit & Push                                   │
│ $ git commit -m "fix: [description]"                    │
│ $ git push origin main                                   │
│ $ git tag -a v4.7 -m "Description"                      │
│ $ git push origin v4.7                                   │
└─────────────────────────────────────────────────────────┘
```

---

## 🚨 Common Misconceptions

### Misconception 1: "Gu Wu creates tests"
**Reality**: Gu Wu ANALYZES tests. YOU write tests (following Gu Wu methodology).

### Misconception 2: "Gu Wu runs tests"
**Reality**: pytest runs tests. Gu Wu analyzes the results.

### Misconception 3: "Feng Shui protocols contain test code"
**Reality**: Feng Shui reports GAPS. You write the missing tests.

### Misconception 4: "Gu Wu is required"
**Reality**: Gu Wu is OPTIONAL for quality validation. pytest is sufficient.

---

## 💡 When to Use Each Tool

### Use Feng Shui When:
- ✅ Starting new module development
- ✅ Before git push (pre-push hook)
- ✅ After major refactoring
- ✅ For quality gates (deployment)

### Use Gu Wu When:
- ✅ Want deeper test quality analysis
- ✅ Need test coverage recommendations
- ✅ Investigating flaky tests
- ✅ Optimizing test performance

### Use pytest When:
- ✅ **ALWAYS** - This runs your tests
- ✅ After writing new tests
- ✅ Before committing code
- ✅ In CI/CD pipelines

---

## 🎯 Example: Real Workflow

**Scenario**: Add new feature to `ai_assistant` module

```bash
# 1. Develop feature
# ... write code in modules/ai_assistant/ ...

# 2. Run Feng Shui
python -m tools.fengshui analyze --module ai_assistant
# Output: "Missing API contract test for POST /api/ai-assistant/chat"

# 3. Write missing test (Manual)
# Create: tests/e2e/app_v2/test_ai_assistant_api_contracts.py
# Write: test_chat_endpoint_contract() with requests.post()

# 4. Run tests
pytest tests/e2e/app_v2/test_ai_assistant_api_contracts.py -v
# Output: ✅ All tests passing

# 5. (Optional) Verify test quality
python -m tools.guwu analyze
# Output: Test quality score: 95/100

# 6. Commit
git add -A
git commit -m "feat: Add chat endpoint with API contract test"
git push origin main
```

---

## 📚 Related Documents

- [[Gu Wu API Contract Testing Foundation]] - Core methodology
- [[API-First Contract Testing Methodology]] - Complete testing guide
- [[Feng Shui Phase 4-17 Complete]] - Multi-agent architecture
- `.clinerules` - Development standards (Section 2: API-First, Section 4: Gu Wu)

---

## 🎓 Philosophy

> **Feng Shui** finds the problems.  
> **YOU** fix the problems.  
> **pytest** validates the fixes.  
> **Gu Wu** ensures quality.

**The automation**: Detection and analysis  
**The manual work**: Writing code and tests  
**The validation**: Running tests to verify

---

## ✅ Summary

**CORRECT Workflow**:
1. Feng Shui → Detect issues
2. Review → Understand issues
3. **YOU** → Fix code, write tests
4. pytest → Run tests
5. Gu Wu (optional) → Analyze quality
6. git → Commit & push

**KEY POINT**: Tools detect and analyze. **YOU write code and tests.**

---

**Status**: ✅ PRODUCTION GUIDE - Reference for all development workflows