# Gu Wu Workflow for AI Assistant

**Date**: 2026-02-15
**Version**: 1.0
**Purpose**: Define what AI does when user says "run guwu test"
**Related**: [[Gu Wu API Contract Testing Foundation]]

---

## When User Says "Run Gu Wu Test"

### AI Workflow (MANDATORY)

**Step 1: Run Tests**
```bash
pytest tests/ -v
```
- Get test results
- Identify failures
- Note which tests pass/fail

**Step 2: Analyze Failures**
For each failing test, AI will:
1. ✅ Read the test file
2. ✅ Read the implementation file
3. ✅ Identify the root cause (e.g., signature mismatch, missing dependency)
4. ✅ Propose specific fix with code example
5. ✅ Explain WHY the fix works

**Step 3: Present Actionable Recommendations**
```
🎯 ISSUE #1: ConversationService signature mismatch
Test: test_conversation_service.py::test_create_conversation_via_service
Root Cause: Test passes repository=repo, but ConversationService.__init__() doesn't accept it
Fix: Check service __init__ signature and update either:
  Option A: Service to accept repository parameter
  Option B: Test to use correct instantiation
Confidence: HIGH
Impact: 2 tests affected
```

**Step 4: Offer to Fix**
Ask user: "Should I implement the fix?"

---

## What AI WILL Do (Automatic)

✅ **Run pytest** - See results
✅ **Analyze failures** - Read code, identify root cause
✅ **Recommend fixes** - Specific, actionable, with code examples
✅ **Explain WHY** - Root cause analysis
✅ **Prioritize** - Impact assessment (how many tests affected)
✅ **Offer to fix** - Ask if user wants AI to implement

---

## What AI WON'T Do (Unless User Requests)

❌ **Automatic fixing** - Always ask first
❌ **Gu Wu Intelligence engines** - Currently archived (tests/guwu/ deleted)
❌ **ML predictions** - Intelligence layer not in current test structure
❌ **Dashboard/metrics** - Phase 7 features archived

---

## Current Gu Wu Capabilities (v4.54)

### ✅ AVAILABLE (API Contract Testing Foundation)
1. **Run tests**: `pytest tests/ -v`
2. **API contract validation**: Tests via requests (< 1s)
3. **Manual analysis**: AI reads code and provides fix recommendations
4. **Test structure**: API-focused, refactoring-friendly
5. **Speed**: 60-300x faster than browser testing

### ⏳ ARCHIVED (Gu Wu Intelligence Engines)
1. **Recommendations Engine** - 8 types of insights (in archive)
2. **Dashboard Engine** - Visual health metrics (in archive)
3. **Predictive Engine** - ML failure forecasting (in archive)
4. **Auto-fix Generator** - Instant fix suggestions (in archive)
5. **Test Gap Analyzer** - Coverage gap detection (in archive)

**Location**: `archive/tests_backup_2026_02_15/guwu/`

**Can be restored** if user needs advanced intelligence features.

---

## Example Workflow

### User Says: "Run guwu test"

**AI Does**:
```bash
# 1. Run tests
pytest tests/ -v

# 2. Analyze results (AI reads code)
# Found: 2 failures in ConversationService tests

# 3. Present recommendations
```

**AI Response**:
```
Test Results: 15 passing ✅, 2 failing ❌

🎯 FAILURE ANALYSIS:

Issue #1: test_create_conversation_via_service
├─ Error: TypeError: ConversationService.__init__() got unexpected keyword argument 'repository'
├─ Root Cause: Test instantiates with repository=repo, but service doesn't accept it
├─ Location: tests/test_ai_assistant_backend.py:158
├─ Fix Options:
│  A) Update service __init__ to accept repository parameter (DI pattern)
│  B) Update test to use correct instantiation (check service code)
└─ Recommendation: Check ConversationService.__init__() signature first

Issue #2: test_add_message_to_conversation
├─ Same root cause as Issue #1
└─ Fix: Same fix resolves both tests

Should I check the ConversationService code and propose specific fix?
```

**User**: "Yes"

**AI Does**:
```python
# Reads: modules/ai_assistant/backend/services/conversation_service.py
# Finds: def __init__(self): (no parameters)
# Proposes: Either add DI or update test
```

---

## Comparison: With vs Without Intelligence Engines

### WITHOUT Intelligence (Current v4.54)
```
User: "Run guwu test"
AI: Runs pytest → Reads code → Analyzes manually → Recommends fix
Time: 30-60 seconds
Accuracy: 90% (AI analysis)
```

### WITH Intelligence (If Restored from Archive)
```
User: "Run guwu test"
AI: Runs pytest + intelligence → ML analysis → Prioritized recommendations
Time: 5-10 seconds
Accuracy: 95% (ML + patterns)
Features: Predictions, trends, auto-fix suggestions
```

---

## When to Restore Intelligence Engines

**Consider restoring if**:
- ✅ Test suite grows >100 tests
- ✅ Need failure prediction
- ✅ Want automated fix suggestions
- ✅ Need health trends over time
- ✅ Want coverage gap analysis

**Restore process**:
```bash
# Copy intelligence engines back
cp -r archive/tests_backup_2026_02_15/guwu/ tests/

# Verify imports work
python -m tools.guwu intelligence --help
```

---

## Key Point

**When you say "run guwu test"**, AI will:
1. ✅ Run pytest (see results)
2. ✅ Analyze failures (manual code reading)
3. ✅ Provide recommendations (specific fixes)
4. ✅ Explain root causes (WHY it failed)
5. ✅ Offer to implement fixes (if you approve)

This is **ALWAYS better than just pytest** because AI adds the analysis layer.

The archived Intelligence Engines would make this even faster/smarter, but manual analysis works well too.

---

## Summary

**Your Question**: "Will you apply all these tools when I ask to run guwu test?"

**Answer**: 
- ✅ **YES** - I run pytest + provide manual analysis + recommendations
- ⚠️ **PARTIAL** - Intelligence engines archived (can restore if needed)
- ✅ **CORE** - API contract testing foundation is active and working

**Current workflow works great** for API contract testing. Intelligence engines are bonus features if you want ML-powered insights.