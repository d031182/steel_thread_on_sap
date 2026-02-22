# Feng Shui & Gu Wu: User Guide

**Audience**: Developers (YOU)  
**Purpose**: How to benefit from autonomous architecture + test intelligence  
**Last Updated**: 2026-02-06

---

## 🎯 Quick Answer: How Do I Benefit?

**Short Answer**: Mostly automatic! The AI assistant uses Feng Shui & Gu Wu autonomously. You just need to know 3 simple commands.

**Your Involvement**:
- ✅ **Gu Wu**: 100% automatic (runs on every `pytest`)
- ✅ **Feng Shui Pre-commit**: 100% automatic (runs on every `git commit`)
- ✅ **Manual Commands**: Only when you want detailed insights

---

## 🤖 What Happens Automatically

### 1. Gu Wu (Tests) - Zero Setup Needed

**Automatic on Every `pytest` Run**:
```bash
# You just run pytest as normal
pytest

# Gu Wu automatically:
# ✅ Tracks test execution metrics (time, outcome, flakiness)
# ✅ Prioritizes likely-to-fail tests (runs them first)
# ✅ Detects flaky tests (transition-based algorithm)
# ✅ Identifies slow tests (>5s threshold)
# ✅ Calculates coverage gaps
# ✅ Learns from execution history
# ✅ Stores insights in SQLite database
```

**You Don't Need To**:
- ❌ Configure anything (conftest.py already set up)
- ❌ Remember special flags
- ❌ Track metrics manually
- ❌ Analyze test patterns yourself

### 2. Feng Shui Pre-commit Hook - Zero Setup Needed

**Automatic on Every `git commit`**:
```bash
# You just commit as normal
git commit -m "Add new feature"

# Feng Shui pre-commit hook automatically:
# ✅ Validates architecture compliance (< 1s)
# ✅ Checks DI violations
# ✅ Validates module.json configurations
# ✅ Prevents bad code from entering repository
# ✅ Blocks commit if violations found (with clear error message)
```

**You Don't Need To**:
- ❌ Remember to run quality checks
- ❌ Manually validate module structure
- ❌ Check for DI violations yourself
- ❌ Wait for CI/CD to catch issues

---

## 🎓 Optional Commands: When You Want Insights

### Gu Wu Intelligence (3 Commands)

**1. Intelligence Hub** (Recommended - All-in-One):
```bash
python -m tests.guwu.intelligence.intelligence_hub
```
**Output**: Comprehensive report combining all 3 engines
- Health Dashboard (score, trends)
- Top Recommendations (prioritized by impact)
- Failure Predictions (ML-powered)
- **Use When**: Weekly check, before major commits, debugging sessions

**2. Dashboard** (Visual Health Metrics):
```bash
python -m tests.guwu.intelligence.dashboard
```
**Output**: Test suite health overview
- Health Score (0-100)
- Total/Passing/Flaky/Slow tests
- Coverage percentage
- 7-day trends (if historical data exists)
- **Use When**: Morning routine, sprint planning

**3. Recommendations** (Actionable Fixes):
```bash
python -m tests.guwu.intelligence.recommendations
```
**Output**: 8 types of prioritized recommendations
- CRITICAL: Flaky tests (highest impact)
- HIGH: Coverage gaps, slow tests
- MEDIUM: Test organization, patterns
- **Use When**: Test failures, refactoring planning

**4. Pre-flight Check** (Before Committing):
```bash
python -m tests.guwu.intelligence.predictive
```
**Output**: Failure predictions for current code
- Lists likely-to-fail tests
- Confidence scores (0-100%)
- Risk level (LOW/MEDIUM/HIGH)
- **Use When**: Before pushing to repo, before demos

---

### Feng Shui Architecture (3 Commands)

**1. Autonomous Agent** (Let It Fix Everything):
```bash
python -m tools.fengshui.react_agent --target-score 95
```
**Output**: Autonomous improvement session
- Analyzes architecture violations
- Creates optimal execution plan
- Fixes violations autonomously (with learning)
- Reports detailed metrics
- **Use When**: Batch architecture cleanup, before releases

**2. Quality Gate** (Validate Specific Module):
```bash
python tools/fengshui/module_quality_gate.py knowledge_graph
```
**Output**: PASSED/FAILED with detailed report
- DI violations
- module.json issues
- Blueprint registration problems
- **Use When**: Before deploying module, after refactoring

**3. Pre-commit Hook** (Already Active):
```bash
# Runs automatically on every commit
git commit -m "Your message"
# Hook validates automatically (< 1s)
```
**Output**: OK or FAILED with violations list
- **Use When**: Every commit (automatic)
- **Bypass (emergency only)**: `git commit --no-verify`

---

## 🚀 Real-World Scenarios: How You Benefit

### Scenario 1: Monday Morning - Check Test Health

**What You Do**:
```bash
python -m tests.guwu.intelligence.intelligence_hub
```

**What You Get**:
```
[HEALTH DASHBOARD]
Health Score: 87/100 (GOOD)
Total Tests: 245
Passing: 238 (97%)
Flaky: 3 (1.2%)
Slow: 4 (1.6%)

[TOP RECOMMENDATIONS]
1. [CRITICAL] Fix flaky test: test_graph_cache_refresh
   Impact: Blocks CI/CD 30% of time
   
2. [HIGH] Add integration test for data_products module
   Coverage gap: Only unit tests exist
```

**How You Benefit**:
- Know test suite health in 2 seconds
- Prioritized action items (not raw data)
- Focus on high-impact issues first

---

### Scenario 2: Before Pushing Code - Pre-flight Check

**What You Do**:
```bash
python -m tests.guwu.intelligence.predictive
```

**What You Get**:
```
[PRE-FLIGHT CHECK]
Risk Level: MEDIUM

Likely to Fail (3 tests):
1. test_knowledge_graph_api (85% confidence)
   Reason: Recent changes to graph_query_service.py
   
2. test_csn_parser (72% confidence)
   Reason: Historical flakiness pattern
```

**How You Benefit**:
- Catch failures BEFORE pushing (not after CI/CD)
- Know exactly which tests to verify
- Avoid breaking main branch

---

### Scenario 3: Commit Code - Auto-Validation

**What You Do**:
```bash
git add modules/my_module/
git commit -m "Add new feature"
```

**What Happens** (Automatic):
```
[FENG SHUI] Pre-Commit Check
============================================================
Checking 5 staged file(s)...

[ERROR] Found 2 violations:

1. DI Violation in modules/my_module/backend/api.py
   Line 25: Direct .connection access
   Fix: Use dependency injection

2. Missing module.json configuration
   File: modules/my_module/module.json
   
Commit blocked. Fix violations and try again.
============================================================
```

**How You Benefit**:
- Violations caught BEFORE commit (not after push)
- Clear error messages with fix guidance
- Prevents technical debt from accumulating

---

### Scenario 4: Architecture Cleanup - Let Agent Handle It

**What You Do**:
```bash
python -m tools.fengshui.react_agent --target-score 95
```

**What Happens** (Autonomous):
```
[ITERATION 1] Fixing DI violations in knowledge_graph...
Score: 78 → 85 (+7 points) ✅

[ITERATION 2] Updating module.json configurations...
Score: 85 → 92 (+7 points) ✅

[ITERATION 3] Moving misplaced test files...
Score: 92 → 96 (+4 points) ✅

GOAL ACHIEVED! Final Score: 96/100
Successful Fixes: 3
Strategy Switches: 0
Total Time: 4.2 minutes
```

**How You Benefit**:
- Architecture fixes done in 5 minutes (vs 30-60 min manual)
- Learns from past fixes (gets smarter over time)
- Comprehensive validation (catches issues you might miss)

---

## 📋 When Should You Manually Run Commands?

### Daily/Weekly Routine

**Every Morning** (2 minutes):
```bash
# Check test suite health
python -m tests.guwu.intelligence.intelligence_hub
```

**Before Every Commit** (automatic):
```bash
# Pre-commit hook runs automatically
git commit -m "Your message"
```

**Before Pushing to GitHub** (1 minute):
```bash
# Pre-flight check for failure predictions
python -m tests.guwu.intelligence.predictive
```

**Weekly** (5 minutes):
```bash
# Architecture health check
python tools/fengshui/module_quality_gate.py [module_name]
```

**Monthly** (10 minutes):
```bash
# Batch architecture cleanup
python -m tools.fengshui.react_agent --target-score 95
```

---

## 🤝 How AI Assistant Uses These Tools

### AI's Automatic Usage (You Don't Need To Do Anything)

**When AI Writes Tests**:
1. AI runs `pytest` → Gu Wu automatically tracks metrics
2. AI checks Intelligence Hub → Gets insights on test quality
3. AI fixes issues based on Recommendations → Gu Wu learns

**When AI Refactors Code**:
1. AI commits changes → Feng Shui pre-commit validates automatically
2. If violations found → AI fixes them based on error messages
3. AI re-commits → Hook validates again

**When AI Debugs Failures**:
1. AI runs Intelligence Hub → Gets root cause analysis
2. AI checks Recommendations → Gets prioritized fixes
3. AI applies fixes → Gu Wu tracks improvement

---

## 💡 Key Insights: Your Benefits

### Gu Wu Benefits (For YOU as Developer)

**Automatic**:
- ✅ Test metrics tracked on every run (zero effort)
- ✅ Flaky tests detected automatically (saves debugging time)
- ✅ Slow tests identified (optimize what matters)
- ✅ Coverage gaps highlighted (know what's not tested)

**On-Demand**:
- ✅ Intelligence Hub → Comprehensive health report (2 seconds)
- ✅ Pre-flight check → Predict failures before push (1 minute)
- ✅ Recommendations → Prioritized action items (not raw data)

**Result**: 
- Spend 2 minutes checking health vs 30 minutes manually analyzing
- Catch issues before they hit CI/CD
- Data-driven decisions (not guesses)

### Feng Shui Benefits (For YOU as Developer)

**Automatic**:
- ✅ Pre-commit hook blocks bad code (prevents tech debt)
- ✅ Clear error messages (know exactly what to fix)
- ✅ Fast validation (< 1s per commit)

**On-Demand**:
- ✅ Quality Gate → Validate module before deploy (10 seconds)
- ✅ ReAct Agent → Batch architecture fixes (5-10 minutes vs 60 min)
- ✅ Learns from history → Gets smarter over time

**Result**:
- Architecture issues caught at commit (not in code review)
- 6x faster cleanup (5-10 min vs 30-60 min)
- Confidence in code quality before deploy

---

## 🎓 Summary: Your Workflow

### Daily Development (Mostly Automatic)

**What You Do**:
```bash
# 1. Write code (as normal)
# 2. Run tests (as normal)
pytest

# 3. Commit (as normal)
git commit -m "Add feature"
# → Feng Shui validates automatically

# 4. Push (with confidence)
git push origin main
```

**What Happens Automatically**:
- Gu Wu tracks test metrics (every pytest run)
- Feng Shui validates architecture (every commit)
- AI assistant uses insights autonomously

### Weekly Health Check (2 minutes)

```bash
# Check test suite health
python -m tests.guwu.intelligence.intelligence_hub

# Act on top 2-3 CRITICAL/HIGH recommendations
```

### Monthly Architecture Cleanup (5-10 minutes)

```bash
# Let Feng Shui agent handle batch fixes
python -m tools.fengshui.react_agent --target-score 95

# Review report, done!
```

---

## ❓ FAQ

**Q: Do I need to configure anything?**  
A: No! conftest.py and pre-commit hooks already set up.

**Q: Will this slow down my workflow?**  
A: No! Pre-commit hook is < 1s. Gu Wu runs during pytest anyway.

**Q: What if I'm in a hurry and need to bypass?**  
A: `git commit --no-verify` (emergency only - not recommended)

**Q: How often should I check Intelligence Hub?**  
A: Weekly for proactive maintenance, or when test failures occur.

**Q: Does this work on Windows?**  
A: Yes! All tools tested on Windows 11.

**Q: What if I don't understand a recommendation?**  
A: Ask AI assistant - it can explain and help implement the fix.

**Q: Can I see historical trends?**  
A: Yes! Dashboard shows 7-day trends if historical data exists.

**Q: What's the minimum I need to do?**  
A: Nothing! Just code normally. Tools work automatically. Check Intelligence Hub weekly for insights.

---

## 🎉 Bottom Line

**You benefit from Feng Shui & Gu Wu through**:

1. **Automation**: 90% works automatically (pre-commit hook, pytest integration)
2. **Intelligence**: 3 simple commands give you actionable insights
3. **Time Savings**: 6x faster architecture fixes, instant test health checks
4. **Quality**: Catch issues at commit (not in production)
5. **AI Partnership**: AI assistant uses tools autonomously to help you

**Your effort**: 2 minutes weekly for health check. Everything else is automatic! 🚀

---

## 📚 Related Documentation

- [[Feng Shui Phase 4-16]] - Technical implementation details
- [[Gu Wu Phase 7 Intelligence]] - Intelligence engines architecture
- `tests/README.md` - Complete Gu Wu documentation
- `docs/FENG_SHUI_ROUTINE_REQUIREMENTS.md` - Feng Shui capabilities
- `.clinerules` - AI assistant usage guidelines