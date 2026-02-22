# Three-Tier Quality Gate System

**Status**: ✅ IMPLEMENTED (Phase 8.3 Complete - Feb 8, 2026)  
**Version**: 1.0  
**Integration**: Feng Shui + Gu Wu + Shi Fu

---

## 🎯 Overview

The Three-Tier Quality Gate System provides **automated quality validation** at different stages of development, balancing **speed** (fast commits) with **thoroughness** (comprehensive push validation).

**Philosophy**: 
> "Catch critical issues immediately (< 2s), validate comprehensively before sharing (30-60s), analyze strategically over time (weekly)."

---

## 🏗️ Architecture

```
Tier 1: Pre-Commit (FAST)
├─→ File organization check (< 1s)
└─→ Critical security scan (< 1s)
    └─→ Total: < 2 seconds

Tier 2: Weekly Analysis (AUTOMATIC)
├─→ Shi Fu triggers every 7 days
├─→ Feng Shui multi-agent (10-30s)
├─→ Gu Wu intelligence hub (5-10s)
└─→ Correlation & teachings
    └─→ Total: 15-40 seconds

Tier 3: Pre-Push (COMPREHENSIVE)
├─→ Run all tests (10-30s)
├─→ Check coverage (10-20s)
├─→ Feng Shui orchestrator on changed modules (10-20s)
└─→ Gu Wu coverage gap detection (5-10s)
    └─→ Total: 35-80 seconds
```

---

## 📋 Tier 1: Pre-Commit Hook (Fast Validation)

### What It Does
- **File Organization**: Validates file locations (root .md files, test locations)
- **Critical Security**: Scans for hardcoded secrets, SQL injection, command injection

### When It Runs
- **Every commit** (automatic)
- **Duration**: < 2 seconds
- **Bypass**: `git commit --no-verify` (use sparingly!)

### Implementation
```bash
# .git/hooks/pre-commit
python tools/fengshui/pre_commit_check.py       # File org
python tools/fengshui/critical_check.py          # Security
```

### What It Blocks
- ❌ .md files in project root (except allowed ones)
- ❌ Tests outside tests/ directory
- ❌ Hardcoded passwords, API keys, secrets
- ❌ SQL injection patterns (string formatting in queries)
- ❌ Command injection (os.system with concatenation)
- ❌ eval(input()) patterns

### Example Output
```
============================================================
FENG SHUI PRE-COMMIT VALIDATION
============================================================
[1/2] File Organization Check...
[OK] No file organization violations

[2/2] Critical Security Check...
[>] Scanning 3 Python file(s)...

[X] CRITICAL SECURITY ISSUES FOUND
============================================================

📄 modules/example/backend/config.py
   Line 12: Hardcoded API key detected
   → api_key = "sk-1234567890abcdef"

[!] CANNOT COMMIT - Fix security issues first
============================================================
```

---

## 📊 Tier 2: Weekly Analysis (Automatic via Shi Fu)

### What It Does
- **Feng Shui**: Multi-agent architecture analysis (6 agents in parallel)
- **Gu Wu**: Test quality intelligence (coverage, flakiness, pyramid)
- **Shi Fu**: Cross-domain correlation & pattern detection
- **Auto-Update**: Adds high-priority items to PROJECT_TRACKER.md

### When It Runs
- **Every 7 days** at session start (automatic)
- **Duration**: 15-40 seconds
- **Manual**: `python -m tools.shifu.shifu --weekly-analysis`

### What It Analyzes
1. **Architecture**: DI violations, SOLID principles, coupling
2. **Security**: Secrets, SQL injection, auth issues
3. **UX**: SAP Fiori compliance, UI patterns
4. **Performance**: N+1 queries, nested loops, caching
5. **File Organization**: Structure, obsolete files
6. **Documentation**: README quality, docstring coverage
7. **Tests**: Coverage gaps, flaky tests, pyramid violations
8. **Correlations**: DI violations → flaky tests, etc.

### Example Output
```
🧘‍♂️ Shi Fu's Weekly Analysis Complete

Celebrations! 🎉
- 🎯 Improved architecture score by 15 points this week!
- 📈 Test coverage increased from 68% to 75%

30-Day Trend:
- Ecosystem: IMPROVING (+5.2 pts/week) 📈

- 2 HIGH priority patterns detected
- Continue current work
```

---

## 🚀 Tier 3: Pre-Push Hook (Comprehensive Validation)

### What It Does
- **Run All Tests**: Execute full pytest suite
- **Coverage Check**: Ensure 70%+ coverage threshold
- **Module Analysis**: Feng Shui orchestrator on changed modules
- **Health Validation**: Modules must score 70/100+
- **Issue Limits**: 0 CRITICAL, max 5 HIGH issues

### When It Runs
- **Every push** (automatic)
- **Duration**: 35-80 seconds
- **Bypass**: `git push --no-verify` (use VERY sparingly!)

### Implementation
```bash
# .git/hooks/pre-push
python tools/fengshui/pre_push_analysis.py
```

### Quality Thresholds
```python
THRESHOLDS = {
    'min_module_health': 70,      # Health score 0-100
    'min_test_coverage': 70,      # Percentage
    'max_critical_issues': 0,     # Zero tolerance
    'max_high_issues': 5          # Max HIGH severity
}
```

### Example Output
```
======================================================================
FENG SHUI PRE-PUSH QUALITY GATE
======================================================================

⏱️  This will take 30-60 seconds - comprehensive validation

[1/4] Running Tests (pytest)...
--------------------------------------------------------------
============================= test session starts =============================
...
============================= 145 passed in 12.34s ============================
✅ All tests passed

[2/4] Checking Test Coverage...
--------------------------------------------------------------
Current coverage: 75%
✅ Coverage meets threshold: 75% >= 70%

[3/4] Analyzing Changed Modules (Feng Shui)...
--------------------------------------------------------------
Analyzing 2 module(s): knowledge_graph_v2, data_products_v2

  Analyzing: knowledge_graph_v2...
    Health: 88/100 ✅ GOOD
    Issues: 0 CRITICAL, 3 HIGH

  Analyzing: data_products_v2...
    Health: 92/100 ✅ EXCELLENT
    Issues: 0 CRITICAL, 1 HIGH

[4/4] Checking Coverage Gaps (Gu Wu)...
--------------------------------------------------------------
⚠️ Gu Wu test generation not yet implemented
Skipping automatic test generation...

======================================================================
✅ QUALITY GATE PASSED
======================================================================

All checks passed! Safe to push 🚀
```

---

## 🎓 Usage Guide

### For Developers

**Normal Workflow**:
```bash
# 1. Make changes
git add .

# 2. Commit (Tier 1 runs automatically, < 2s)
git commit -m "feature: Add new API endpoint"

# 3. Push (Tier 3 runs automatically, 35-80s)
git push origin main
```

**If Pre-Commit Blocks You**:
```bash
# Fix the issue (e.g., remove hardcoded secret)
# Then retry commit
git commit -m "..."
```

**If Pre-Push Blocks You**:
```bash
# Option 1: Fix issues
pytest --tb=short                           # Fix failing tests
python -m tools.fengshui.react_agent        # Fix architecture
git push                                     # Retry

# Option 2: Emergency bypass (RISKY!)
git push --no-verify
```

**Weekly Analysis** (Automatic):
```bash
# Shi Fu runs automatically at session start (every 7 days)
# Check PROJECT_TRACKER.md for new high-priority items
```

---

## 🔧 Configuration

### Adjust Thresholds

**Pre-Push Thresholds** (`tools/fengshui/pre_push_analysis.py`):
```python
THRESHOLDS = {
    'min_module_health': 70,      # Lower if too strict
    'min_test_coverage': 70,      # Adjust coverage requirement
    'max_critical_issues': 0,     # Never change (zero tolerance)
    'max_high_issues': 5          # Increase if needed
}
```

**Shi Fu Frequency** (`tools/shifu/cline_integration.py`):
```python
# Change analysis frequency (default: 7 days)
days_since = (datetime.now() - last_analysis).days
return days_since >= 7  # Change to 3, 14, etc.
```

### Disable Hooks Temporarily

```bash
# Disable pre-commit (one commit only)
git commit --no-verify -m "..."

# Disable pre-push (one push only)
git push --no-verify

# Disable Shi Fu weekly analysis
# (Edit .shifu_state.json, set last_analysis to today)
```

---

## 📊 Comparison Table

| Aspect | Tier 1 (Pre-Commit) | Tier 2 (Weekly) | Tier 3 (Pre-Push) |
|--------|---------------------|-----------------|-------------------|
| **Trigger** | Every commit | Every 7 days | Every push |
| **Duration** | < 2s | 15-40s | 35-80s |
| **Scope** | File org + critical security | Full ecosystem analysis | Changed modules + tests |
| **Depth** | Fast regex patterns | Multi-agent + correlation | Comprehensive validation |
| **Blocks** | Commit | Nothing (informational) | Push to remote |
| **Bypass** | `--no-verify` | N/A | `--no-verify` |
| **Goal** | Prevent obviously bad commits | Strategic insights | Comprehensive quality gate |

---

## 🎯 Benefits

### For Individual Developers
- ✅ **Fast commits**: < 2s validation doesn't slow workflow
- ✅ **Catch mistakes early**: Before they spread to team
- ✅ **Comprehensive safety**: 35-80s pre-push catches issues
- ✅ **Learn over time**: Shi Fu teachings improve skills

### For Teams
- ✅ **Prevent bad code**: Quality gate enforces standards
- ✅ **Consistent quality**: Automated, not manual review
- ✅ **Reduced tech debt**: Issues caught before merge
- ✅ **Trend visibility**: Weekly analysis tracks improvement

### For Projects
- ✅ **Architecture health**: Maintained automatically
- ✅ **Security**: Hardcoded secrets blocked immediately
- ✅ **Test coverage**: Enforced minimum threshold
- ✅ **Long-term improvement**: Shi Fu tracks trends

---

## 🚦 Workflow Examples

### Example 1: Clean Commit & Push
```bash
$ git commit -m "feature: Add caching layer"

============================================================
FENG SHUI PRE-COMMIT VALIDATION
============================================================
[1/2] File Organization Check...
[OK] No file organization violations
[2/2] Critical Security Check...
[OK] No critical security issues found!

✅ Pre-commit validation passed!
============================================================

[main 1a2b3c4] feature: Add caching layer
 3 files changed, 45 insertions(+), 2 deletions(-)

$ git push origin main

======================================================================
FENG SHUI PRE-PUSH QUALITY GATE
======================================================================

[1/4] Running Tests...
✅ All tests passed

[2/4] Checking Coverage...
✅ Coverage: 76% >= 70%

[3/4] Analyzing Modules...
✅ knowledge_graph_v2: 89/100 GOOD

[4/4] Checking Coverage Gaps...
Skipping automatic test generation...

======================================================================
✅ QUALITY GATE PASSED - Safe to push! 🚀
======================================================================
```

### Example 2: Blocked by Security Issue
```bash
$ git commit -m "fix: Update API configuration"

============================================================
FENG SHUI PRE-COMMIT VALIDATION
============================================================
[1/2] File Organization Check...
[OK] No violations

[2/2] Critical Security Check...
[>] Scanning 2 Python file(s)...

[X] CRITICAL SECURITY ISSUES FOUND
============================================================

📄 modules/api_gateway/backend/config.py
   Line 45: Hardcoded API key detected
   → api_key = "sk-1234567890abcdef1234567890abcdef"

[!] CANNOT COMMIT - Fix security issues first

[FIX] How to fix:
   1. Move secrets to environment variables (.env)
   2. Use os.getenv('API_KEY') instead
   3. Add .env to .gitignore
   4. Retry commit

[!] To bypass (DANGEROUS!): git commit --no-verify
============================================================

# Fix the issue
$ # Move API key to .env, update code
$ git commit -m "fix: Update API configuration"
✅ Pre-commit validation passed!
```

### Example 3: Shi Fu Weekly Analysis
```bash
# Session starts on Day 8 (7 days since last analysis)

🧘‍♂️ Shi Fu's Weekly Analysis Complete

Celebrations! 🎉
- 🎯 Reduced CRITICAL issues from 3 to 0!
- 📊 Flaky tests decreased from 12 to 5

- 3 HIGH priority patterns detected
- 2 patterns added to PROJECT_TRACKER.md

**Should I work on these patterns?**
1. DI Violations → Flaky Tests (8 affected modules)
2. High Complexity → Low Coverage (knowledge_graph_v2)
3. Performance Issues → Slow Tests (data_products)
```

---

## 🔮 Future Enhancements

### Phase 8.4: Gu Wu Test Auto-Generation (Planned)
- Detect coverage gaps during pre-push
- Automatically generate missing tests
- Offer to add tests to commit before push

### Phase 8.5: CI/CD Integration (Planned)
- GitHub Actions workflow
- Run quality gate on PRs
- Block merges that fail validation
- Generate quality reports

### Phase 8.6: Configurable Profiles (Planned)
- `--profile strict`: Zero tolerance for all issues
- `--profile standard`: Current thresholds (default)
- `--profile lenient`: Relaxed for legacy code

---

## 📚 Related Documentation

- [[Feng Shui Multi-Agent Architecture]] - Tier 1 & 3 architecture validation
- [[Gu Wu Testing Framework]] - Test quality intelligence
- [[Shi Fu Meta-Intelligence]] - Tier 2 weekly analysis
- [[Quality Ecosystem Vision]] - Overall quality philosophy

---

## 🎓 Summary

**The Three-Tier Quality Gate System provides**:

1. **Tier 1 (Pre-Commit)**: Fast critical validation (< 2s)
   - Prevents obviously bad commits immediately
   
2. **Tier 2 (Weekly)**: Strategic ecosystem analysis (15-40s)
   - Proactive insights, trend tracking, teachings
   
3. **Tier 3 (Pre-Push)**: Comprehensive quality gate (35-80s)
   - Ensures only high-quality code reaches team

**Result**: 
- ✅ Fast daily workflow (< 2s commits)
- ✅ Comprehensive validation before sharing (35-80s push)
- ✅ Strategic improvement over time (weekly analysis)
- ✅ Automated, consistent, learning quality enforcement

**Philosophy**:
> "Balance speed and thoroughness. Catch critical issues instantly, validate comprehensively before sharing, learn continuously over time."