# Feng Shui + Gu Wu Pre-Commit Integration

**Purpose**: Enhance pre-commit hook with intelligent test execution and architecture analysis  
**Status**: 📋 PROPOSAL - Awaiting implementation approval  
**Created**: 2026-02-09  

Related: [[Feng Shui Pre-Commit Hook Documentation]], [[Gu Wu Testing Framework]], [[Feng Shui Phase 4-17]], [[Quality Ecosystem Vision]]

---

## 🎯 Vision

**Current State** (Basic Pre-Commit):
```
1. File organization check (< 1s)
2. Critical security check (< 1s)
✅ Fast (< 2s) but limited intelligence
```

**Proposed State** (Intelligent Pre-Commit):
```
1. File organization check (< 1s)
2. Critical security check (< 1s)
3. Gu Wu: Run tests for staged files (< 10s) ⭐ NEW
4. Feng Shui: Orchestrator analysis (< 10s) ⭐ NEW
5. Feng Shui → Gu Wu: Generate missing tests ⭐ NEW
✅ Smart (< 30s) with proactive quality assurance
```

---

## 🏗️ Architecture Design

### Three-Tier Integration

**Tier 1: Current Checks** (< 2s) - KEEP AS-IS
- File organization validation
- Critical security patterns
- **Why keep**: Fast feedback for obvious issues

**Tier 2: Gu Wu Test Execution** (< 10s) ⭐ NEW
- Run unit tests for staged Python files
- Incremental testing (only affected tests)
- Fast feedback on breaking changes

**Tier 3: Feng Shui Intelligence** (< 10s) ⭐ NEW
- Orchestrator analyzes staged files (6 agents in parallel)
- Detects architecture gaps, security issues
- Identifies missing test coverage
- Generates test recommendations → Gu Wu

---

## 📋 Detailed Design

### Component 1: Gu Wu Pre-Commit Test Runner

**Purpose**: Run tests for staged files BEFORE commit

**File**: `tools/guwu/pre_commit_test_runner.py`

**Responsibilities**:
1. Get staged Python files
2. Find related test files (unit tests only for speed)
3. Run pytest on affected tests
4. Report results (pass/fail)
5. Exit with appropriate code (0 = pass, 1 = fail)

**Key Features**:
- **Incremental Testing**: Only run tests for changed files
- **Fast Execution**: Unit tests only (< 10s target)
- **Smart Discovery**: Use pytest's collection + Gu Wu metadata
- **Clear Output**: Show which tests ran and why

**Example Output**:
```
[GU WU] Pre-Commit Test Execution
==================================================
[>] Staged files: 3 Python files
[>] Affected tests: 12 unit tests

Running tests...
✅ test_api.py::test_get_data_products ........... PASSED
✅ test_service.py::test_create_product .......... PASSED
...
==================================================
[OK] 12/12 tests passed (8.2s)
==================================================
```

---

### Component 2: Feng Shui Pre-Commit Orchestrator

**Purpose**: Analyze staged files for architecture/security gaps

**File**: `tools/fengshui/pre_commit_orchestrator.py`

**Responsibilities**:
1. Get staged files (Python only for speed)
2. Run 6 specialized agents in parallel
3. Analyze for DI violations, security issues, complexity
4. Identify coverage gaps (areas without tests)
5. Generate test recommendations
6. Save recommendations for Gu Wu to consume

**Key Features**:
- **Parallel Execution**: 6 agents run concurrently (< 10s)
- **Focused Analysis**: Only staged files, not entire codebase
- **Test Gap Detection**: Compare code changes vs test coverage
- **Actionable Output**: Clear recommendations, not just problems

**Example Output**:
```
[FENG SHUI] Orchestrator Analysis
==================================================
[>] Analyzing 3 staged files...

ArchitectAgent:    ✅ No DI violations
SecurityAgent:     ⚠️ 1 issue (hardcoded API key line 42)
PerformanceAgent:  ✅ No performance issues
UXArchitectAgent:  N/A (no UI files)
FileOrgAgent:      ✅ Files properly organized
DocumentationAgent: ⚠️ Missing docstring (MyService.create)

[!] Test Coverage Gaps:
    • modules/data_products_v2/backend/service.py:42-58
      → No tests for create_product() error handling
    • modules/data_products_v2/backend/api.py:89-102
      → No tests for pagination edge cases

==================================================
[REPORT] 2 issues, 2 test gaps
Recommendations saved to: .fengshui_test_gaps.json
==================================================
```

---

### Component 3: Feng Shui → Gu Wu Test Gap Bridge

**Purpose**: Communicate test gaps from Feng Shui to Gu Wu

**File**: `.fengshui_test_gaps.json` (temporary file)

**Format**:
```json
{
  "timestamp": "2026-02-09T09:35:00Z",
  "commit_hash": "abc123...",
  "test_gaps": [
    {
      "file": "modules/data_products_v2/backend/service.py",
      "lines": "42-58",
      "function": "create_product",
      "gap_type": "error_handling",
      "severity": "HIGH",
      "recommendation": "Add unit tests for validation errors, duplicate key errors",
      "suggested_test_file": "tests/unit/modules/data_products_v2/test_service_error_handling.py"
    },
    {
      "file": "modules/data_products_v2/backend/api.py",
      "lines": "89-102",
      "function": "get_paginated_data",
      "gap_type": "edge_cases",
      "severity": "MEDIUM",
      "recommendation": "Add tests for: empty results, last page, invalid page numbers",
      "suggested_test_file": "tests/unit/modules/data_products_v2/test_api_pagination.py"
    }
  ],
  "summary": {
    "total_gaps": 2,
    "high_severity": 1,
    "medium_severity": 1,
    "low_severity": 0
  }
}
```

**Gu Wu Consumption**:
- Gu Wu's Gap Analyzer reads `.fengshui_test_gaps.json`
- Displays actionable recommendations to developer
- Can auto-generate test stubs if requested
- Tracks gap resolution over time

---

## 🔄 Complete Workflow

### Happy Path (All Checks Pass)

```bash
$ git add modules/data_products_v2/backend/service.py
$ git commit -m "Add create_product method"

============================================================
FENG SHUI + GU WU PRE-COMMIT VALIDATION
============================================================

[1/5] File Organization Check...           ✅ PASSED (0.5s)
[2/5] Critical Security Check...           ✅ PASSED (0.4s)
[3/5] Gu Wu Test Execution...              ✅ PASSED (7.2s, 8/8 tests)
[4/5] Feng Shui Orchestrator Analysis...   ✅ PASSED (8.1s, 0 issues)
[5/5] Test Coverage Analysis...            ✅ PASSED (1.2s, 0 gaps)

✅ Pre-commit validation passed!
============================================================

[Commit proceeds normally]
```

---

### Test Failure Path

```bash
$ git add modules/data_products_v2/backend/service.py
$ git commit -m "Add create_product method"

============================================================
FENG SHUI + GU WU PRE-COMMIT VALIDATION
============================================================

[1/5] File Organization Check...           ✅ PASSED (0.5s)
[2/5] Critical Security Check...           ✅ PASSED (0.4s)
[3/5] Gu Wu Test Execution...              ❌ FAILED (6.8s, 6/8 tests)

[X] TESTS FAILED
==================================================
test_service.py::test_create_product ... FAILED
  AssertionError: Expected 201, got 500

test_service.py::test_create_duplicate ... FAILED
  AttributeError: 'NoneType' object has no attribute 'id'
==================================================

[FIX] Fix failing tests before committing:
  1. Run: pytest tests/unit/modules/data_products_v2/test_service.py -v
  2. Debug and fix issues
  3. Verify: python run_tests.py
  4. Commit again

[!] To bypass (NOT RECOMMENDED): git commit --no-verify
==================================================

[Commit blocked]
```

---

### Architecture Issue Path

```bash
$ git add modules/data_products_v2/backend/service.py
$ git commit -m "Add create_product method"

============================================================
FENG SHUI + GU WU PRE-COMMIT VALIDATION
============================================================

[1/5] File Organization Check...           ✅ PASSED (0.5s)
[2/5] Critical Security Check...           ❌ FAILED (0.6s)

[X] CRITICAL SECURITY ISSUES FOUND
==================================================
📄 modules/data_products_v2/backend/service.py
   Line 42: Hardcoded API key detected
   → api_key = "sk-1234567890abcdef"
==================================================

[FIX] Move API key to environment variable:
  1. Add to .env: API_KEY=sk-1234567890abcdef
  2. Update code: api_key = os.getenv('API_KEY')
  3. Commit again

[!] CANNOT COMMIT - Fix security issues first
==================================================

[Commit blocked - doesn't reach later stages]
```

---

### Test Gap Detection Path

```bash
$ git add modules/data_products_v2/backend/service.py
$ git commit -m "Add create_product method"

============================================================
FENG SHUI + GU WU PRE-COMMIT VALIDATION
============================================================

[1/5] File Organization Check...           ✅ PASSED (0.5s)
[2/5] Critical Security Check...           ✅ PASSED (0.4s)
[3/5] Gu Wu Test Execution...              ✅ PASSED (7.2s, 8/8 tests)
[4/5] Feng Shui Orchestrator Analysis...   ⚠️  WARNINGS (8.3s)
[5/5] Test Coverage Analysis...            ⚠️  GAPS DETECTED (1.5s)

[!] TEST COVERAGE GAPS DETECTED
==================================================
📄 modules/data_products_v2/backend/service.py

Gap 1: Error Handling Not Tested (HIGH)
  Lines: 42-58 (create_product function)
  Missing: Validation errors, duplicate key errors, DB connection failures
  Recommendation: Add tests/unit/modules/data_products_v2/test_service_error_handling.py

Gap 2: Edge Cases Not Tested (MEDIUM)
  Lines: 89-102 (get_paginated_data function)
  Missing: Empty results, last page boundary, invalid page numbers
  Recommendation: Add tests/unit/modules/data_products_v2/test_api_pagination.py

==================================================

[OPTION 1] Continue commit (tests will run, but gaps exist)
[OPTION 2] Abort and add missing tests first (RECOMMENDED)

Proceed with commit? [y/N]: 
```

**User Choice**:
- **Y**: Commit proceeds (gaps logged for later)
- **N**: Commit aborted, user adds tests first

**Philosophy**: Warn but don't block (education > enforcement for test gaps)

---

## ⚙️ Configuration Options

### Environment Variables

```bash
# Enable/disable each check
PRECOMMIT_RUN_TESTS=true          # Run Gu Wu tests
PRECOMMIT_RUN_ORCHESTRATOR=true   # Run Feng Shui analysis
PRECOMMIT_DETECT_GAPS=true        # Detect test gaps
PRECOMMIT_BLOCK_ON_GAPS=false     # Block commit if gaps found (default: warn only)

# Performance tuning
PRECOMMIT_TEST_TIMEOUT=10         # Max seconds for test execution
PRECOMMIT_ORCHESTRATOR_TIMEOUT=10 # Max seconds for Feng Shui analysis
PRECOMMIT_MAX_FILES=20            # Skip if >20 files staged (too slow)

# Output verbosity
PRECOMMIT_VERBOSE=false           # Show detailed output
PRECOMMIT_QUIET=false             # Minimal output
```

### Feature Flags (`feature_flags.json`)

```json
{
  "pre_commit_intelligence": {
    "enabled": true,
    "description": "Enable Gu Wu + Feng Shui integration in pre-commit",
    "components": {
      "gu_wu_tests": true,
      "feng_shui_orchestrator": true,
      "test_gap_detection": true,
      "test_gap_blocking": false
    }
  }
}
```

---

## 🎯 Performance Targets

| Check | Current | Target | Max Acceptable |
|-------|---------|--------|----------------|
| File Organization | 0.5s | 0.5s | 1s |
| Security Patterns | 0.4s | 0.4s | 1s |
| **Gu Wu Tests** | N/A | **7s** | **10s** |
| **Feng Shui Orchestrator** | N/A | **8s** | **10s** |
| **Test Gap Detection** | N/A | **1s** | **2s** |
| **TOTAL** | **< 2s** | **< 20s** | **< 30s** |

**Performance Strategies**:
1. **Incremental Testing**: Only run tests for changed files
2. **Parallel Execution**: Feng Shui agents run concurrently
3. **Early Exit**: If security fails, skip expensive checks
4. **Caching**: Cache orchestrator results for unchanged files
5. **Smart Thresholds**: Skip if >20 files staged (too big for pre-commit)

---

## 🚀 Implementation Plan

### Phase 1: Gu Wu Test Runner (4-6 hours)
- ✅ Create `tools/guwu/pre_commit_test_runner.py`
- ✅ Implement staged file → test discovery logic
- ✅ Integrate with pytest (incremental execution)
- ✅ Add clear output formatting
- ✅ Write tests for test runner itself

### Phase 2: Feng Shui Orchestrator Integration (6-8 hours)
- ✅ Create `tools/fengshui/pre_commit_orchestrator.py`
- ✅ Adapt orchestrator for pre-commit context (fast mode)
- ✅ Implement parallel agent execution
- ✅ Add test gap detection logic
- ✅ Write gap report generator

### Phase 3: Feng Shui → Gu Wu Bridge (2-3 hours)
- ✅ Design `.fengshui_test_gaps.json` format
- ✅ Implement gap file writer (Feng Shui side)
- ✅ Implement gap file reader (Gu Wu side)
- ✅ Add gap display in Gu Wu output
- ✅ Integrate with Gap Analyzer

### Phase 4: Enhanced Pre-Commit Hook (2-3 hours)
- ✅ Update `.git/hooks/pre-commit` script
- ✅ Add configuration file support
- ✅ Implement performance limits (timeouts, file counts)
- ✅ Add bypass mechanisms
- ✅ Create comprehensive error handling

### Phase 5: Testing & Documentation (3-4 hours)
- ✅ End-to-end testing (all scenarios)
- ✅ Performance validation (< 30s target)
- ✅ Update pre-commit hook documentation
- ✅ Create migration guide for team
- ✅ Add troubleshooting guide

**Total Effort**: 17-24 hours (3-4 days part-time)

---

## 🎓 Benefits

### For Developers

**Before** (Basic Pre-Commit):
- ❌ Commit code, tests run in CI later (slow feedback)
- ❌ Discover broken tests 5-10 minutes after commit
- ❌ No visibility into architecture issues until manual review
- ❌ Test gaps discovered much later (or never)

**After** (Intelligent Pre-Commit):
- ✅ Instant feedback on breaking tests (< 10s)
- ✅ Proactive architecture analysis before commit
- ✅ Clear recommendations for missing tests
- ✅ Learn best practices through validation messages

### For Project Quality

1. **Prevents Broken Commits**: Tests run BEFORE code enters repository
2. **Proactive Quality**: Architecture issues caught at source
3. **Better Test Coverage**: Feng Shui identifies gaps, Gu Wu tracks them
4. **Faster Feedback**: 20s local check vs 5min CI pipeline
5. **Educational**: Developers learn patterns through recommendations

### For Quality Ecosystem

1. **Feng Shui + Gu Wu Collaboration**: First real integration (proof of concept)
2. **Bi-Directional Flow**: Feng Shui detects → Gu Wu validates → Feng Shui learns
3. **Continuous Learning**: Gap patterns inform future detectors
4. **Measurable Impact**: Track gap resolution over time

---

## ⚠️ Risks & Mitigation

### Risk 1: Performance (Hook Too Slow)

**Problem**: 30s pre-commit might frustrate developers  
**Mitigation**:
- Strict timeouts (10s per check, 30s total)
- Skip if >20 files staged (too big for pre-commit)
- Allow bypass with clear messaging
- Make components toggleable (env vars)

### Risk 2: False Positives

**Problem**: Feng Shui flags issues that aren't real problems  
**Mitigation**:
- Warn-only mode for test gaps (don't block)
- High confidence thresholds for architecture issues
- Clear bypass instructions
- Feedback mechanism (`.fengshui_ignore` file)

### Risk 3: Developer Resistance

**Problem**: "Pre-commit is annoying, I'll just use --no-verify"  
**Mitigation**:
- Make it opt-in initially (feature flag)
- Demonstrate value through metrics (bugs prevented)
- Keep output concise and actionable
- Celebrate successes (dashboard showing prevented issues)

### Risk 4: Maintenance Burden

**Problem**: Two more scripts to maintain  
**Mitigation**:
- Comprehensive test coverage for new scripts
- Clear documentation and examples
- Reuse existing Feng Shui/Gu Wu components
- Monitor performance metrics

---

## 📊 Success Metrics

**Quantitative**:
- **Performance**: 90% of commits complete in < 30s
- **Test Failures Prevented**: >50% of test failures caught pre-commit (vs CI)
- **Test Gap Reduction**: 30% increase in test coverage within 3 months
- **Architecture Issues Prevented**: >20 DI violations caught pre-commit

**Qualitative**:
- **Developer Satisfaction**: Survey after 1 month (target: 70% positive)
- **Adoption Rate**: 80% of commits pass through full validation (not bypassed)
- **Bug Reduction**: Fewer production bugs from unvalidated code

---

## 🔄 Future Enhancements

### Phase 2 Enhancements (Post-MVP)

1. **Shi Fu Integration**: Meta-analysis of pre-commit patterns
2. **Auto-Fix**: Generate test stubs automatically
3. **Smart Caching**: Remember results for unchanged files
4. **Dashboard**: Visualize pre-commit metrics over time
5. **ML Integration**: Learn which gaps are highest risk

---

## 📚 See Also

- [[Feng Shui Pre-Commit Hook Documentation]] - Current hook documentation
- [[Gu Wu Testing Framework]] - Test framework capabilities
- [[Feng Shui Phase 4-17]] - Orchestrator architecture
- [[Quality Ecosystem Vision]] - Overall quality strategy
- [[Gu Wu Fengshui Future Integration]] - Long-term integration roadmap

---

## 🎯 Decision Required

**Question**: Should we proceed with implementation?

**Options**:
1. **Full Implementation** (17-24 hours) - All 5 phases
2. **Minimal Implementation** (10-12 hours) - Phases 1-2 only (tests + orchestrator, no gap bridge)
3. **Pilot Phase** (6-8 hours) - Phase 1 only (Gu Wu tests), validate before expanding
4. **Defer** - Keep current simple hook, revisit later

**Recommendation**: **Option 3 (Pilot Phase)** 
- Start with Gu Wu test runner only
- Validate performance and developer experience
- Add Feng Shui integration in Phase 2 if successful
- Lower risk, faster delivery, measurable value

---

**Last Updated**: 2026-02-09  
**Status**: 📋 AWAITING DECISION  
**Estimated Effort**: 6-24 hours (depending on option chosen)