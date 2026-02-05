# Feng Shui vs Gu Wu: Why Two Separate Frameworks

**Date**: February 5, 2026  
**Decision**: Keep Feng Shui (tools/fengshui/) and Gu Wu (tests/guwu/) as separate, independent frameworks  
**Rationale**: Different concerns, different domains, different purposes

---

## TL;DR

**Feng Shui**: Code organization and architecture quality  
**Gu Wu**: Test execution optimization and coverage  
**Relationship**: Complementary, not overlapping

---

## Framework Comparison

| Aspect | Feng Shui (风水) | Gu Wu (顾武) |
|--------|------------------|--------------|
| **Location** | `tools/fengshui/` | `tests/guwu/` |
| **Philosophy** | "A place for everything" | "Martial discipline" |
| **Focus** | WHERE things are | HOW tests execute |
| **Domain** | Code organization | Test optimization |
| **Scope** | Entire codebase | Test suite only |
| **Frequency** | Monthly audits | Continuous execution |
| **Tools** | Static analysis | Runtime metrics |
| **Output** | Work packages | Test insights |

---

## Feng Shui (风水): Spatial Harmony

### Purpose
Validates that code is **organized correctly** - files in right places, modules properly structured, architecture followed.

### Location
```
tools/fengshui/
├── feng_shui_score.py          # Holistic quality scoring (0-100)
└── module_quality_gate.py      # 22-check validation gate
```

### What It Checks
1. **Architecture** (40 points):
   - Dependency injection compliance
   - Interface-based programming
   - Loose coupling validation

2. **Code Quality** (30 points):
   - Module structure (module.json present)
   - Code organization (proper directory structure)
   - Documentation (README.md exists)

3. **Security** (20 points):
   - No hardcoded credentials
   - Secure configuration management
   - API endpoint security

4. **Documentation** (10 points):
   - Module documentation complete
   - API documentation exists
   - Architecture documented

### Philosophy
> "Like Feng Shui arranges physical space for harmony, this framework arranges code for maintainability"

Spatial organization metaphor - everything has its proper place.

### Usage
```bash
# Check single module
python tools/fengshui/feng_shui_score.py knowledge_graph

# Check all modules  
python tools/fengshui/feng_shui_score.py

# Enforce standards
python tools/fengshui/module_quality_gate.py [module_name]
```

### When to Use
- Before completing any module (quality gate MANDATORY)
- Monthly feng shui audits (proactive maintenance)
- After major refactoring
- Before production deployment

---

## Gu Wu (顾武): Test Excellence

### Purpose
Optimizes **test execution** - prioritizes tests, detects flaky tests, finds coverage gaps, suggests fixes.

### Location
```
tests/guwu/
├── metrics.py          # Test execution tracking (SQLite)
├── engine.py           # Test prioritization engine
├── optimizer.py        # Automatic reordering
├── insights.py         # Autonomous recommendations
├── predictor.py        # ML-based failure prediction
├── autofix.py          # Fix suggestion generator
├── gap_analyzer.py     # Coverage gap detection
├── lifecycle.py        # Test lifecycle management
└── reflection.py       # Meta-learning system
```

### What It Checks
1. **Test Execution**:
   - Failure patterns and trends
   - Flaky test detection (0.0-1.0 score)
   - Slow test identification (>5s threshold)
   - Test prioritization (run high-risk first)

2. **Test Coverage**:
   - Untested functions (AST-based scanning)
   - Complexity analysis (cyclomatic complexity)
   - Gap prioritization (CRITICAL/HIGH/MEDIUM/LOW)
   - Auto-generate test templates

3. **Test Quality**:
   - Pyramid compliance (70% unit / 20% integration / 10% E2E)
   - Coverage trending (alert on >5% drops)
   - Test redundancy detection
   - Smart test selection

4. **AI Capabilities**:
   - Predict test failures before running
   - Suggest fixes with 90% confidence
   - Manage test lifecycle automatically
   - Self-reflection and improvement

### Philosophy
> "Like martial arts training (武), tests require continuous practice and discipline to stay sharp"

Continuous improvement through execution - tests that learn and adapt.

### Usage
```bash
# Run tests with Gu Wu (automatic)
pytest

# Predict failures
python -m tests.guwu.predictor --all

# Find coverage gaps
python -m tests.guwu.gap_analyzer

# Generate test templates
python -m tests.guwu.gap_analyzer --generate-tests

# Manage lifecycle
python -m tests.guwu.lifecycle

# Self-reflection
python -m tests.guwu.reflection
```

### When to Use
- Every test execution (automatic via pytest)
- When test suite slows down (optimize)
- After adding new features (find gaps)
- When tests fail (get fix suggestions)
- Monthly reflection (improvement insights)

---

## Why Keep Them Separate?

### 1. Different Concerns
- **Feng Shui**: "Is code in the right place?" (static structure)
- **Gu Wu**: "Are tests executing optimally?" (runtime behavior)

### 2. Different Tools
- **Feng Shui**: File system scanning, AST parsing for structure
- **Gu Wu**: Execution metrics, ML predictions, runtime patterns

### 3. Different Workflows
- **Feng Shui**: Monthly audits → Work packages → Implement fixes
- **Gu Wu**: Continuous execution → Insights → Auto-optimize

### 4. Different Scopes
- **Feng Shui**: Entire project (modules/, docs/, scripts/, core/)
- **Gu Wu**: Test suite only (tests/unit/, tests/integration/, tests/e2e/)

### 5. Independent Reusability
- **Copy Feng Shui alone**: Get code organization quality (20 min setup)
- **Copy Gu Wu alone**: Get test optimization (15 min setup)
- **Copy both**: Get comprehensive quality system (35 min setup)

### 6. Different Evolution Paths

**Feng Shui Future**:
- Code smell detection
- Architecture pattern validation
- Dependency graph analysis
- Technical debt tracking

**Gu Wu Future**:
- AI test generation from requirements
- Mutation testing
- Performance regression detection
- Visual regression testing

Merging would constrain both to evolve in lockstep.

---

## How They Work Together

### Complementary Relationship

```
┌─────────────────────────────────────────────────┐
│              QUALITY ECOSYSTEM                  │
│                                                 │
│  FENG SHUI (Code Organization)                 │
│  ├─ Finds: DI violations in 10 modules         │
│  ├─ Creates: Work package WP-001               │
│  └─ Result: Architecture improvements          │
│                                                 │
│  GU WU (Test Optimization)                     │
│  ├─ Finds: 414 test gaps (16 CRITICAL)        │
│  ├─ Generates: 5 test templates               │
│  └─ Result: Better test coverage               │
│                                                 │
│  COMBINED BENEFIT:                             │
│  Better code organization + Better tests       │
│  = Production-ready quality                    │
└─────────────────────────────────────────────────┘
```

### Example Workflow

**Scenario**: New module added

1. **Feng Shui Check**:
   ```bash
   python tools/fengshui/module_quality_gate.py new_module
   # Result: 5 violations found (DI issues, missing docs)
   ```

2. **Fix Issues** (guided by Feng Shui):
   - Add proper dependency injection
   - Create module.json
   - Write README.md

3. **Gu Wu Check**:
   ```bash
   python -m tests.guwu.gap_analyzer
   # Result: 8 untested functions found (3 CRITICAL)
   ```

4. **Generate Tests** (guided by Gu Wu):
   ```bash
   python -m tests.guwu.gap_analyzer --generate-tests
   # Result: Test templates auto-created
   ```

5. **Re-validate**:
   - Feng Shui: ✅ PASSED (22/22 checks)
   - Gu Wu: ✅ 100% coverage achieved

**Outcome**: Production-ready module with both quality dimensions covered

---

## User Philosophy

> "We should not move feng shui into gu wu and dilute the feng shui framework"

### Why This Matters

**Dilution Risk**: Merging creates "quality-test-mega-framework" that:
- ❌ Loses clear identity (what does it do?)
- ❌ Harder to understand (too many concerns)
- ❌ Harder to reuse (all-or-nothing)
- ❌ Harder to maintain (complex dependencies)
- ❌ Harder to explain (what's the core concept?)

**Separation Benefit**: Two focused frameworks:
- ✅ Clear purpose (Feng Shui = organization, Gu Wu = tests)
- ✅ Easy to understand (single responsibility each)
- ✅ Easy to reuse (copy what you need)
- ✅ Easy to maintain (focused scope)
- ✅ Easy to explain (one metaphor each)

---

## Reusability Implications

### Copy Feng Shui Only (20 minutes)
```bash
cp -r tools/fengshui/ /new-project/core/
cp scripts/CLEANUP_GUIDE.md /new-project/scripts/
python tools/fengshui/feng_shui_score.py
# → Instant code organization insights
```

**Use Case**: New Python project needs code quality validation

### Copy Gu Wu Only (15 minutes)
```bash
cp -r tests/guwu/ /new-project/tests/
cp pytest.ini conftest.py /new-project/tests/
pytest
# → Instant test optimization
```

**Use Case**: Existing project needs test suite optimization

### Copy Both (35 minutes)
```bash
# Get comprehensive quality system
# Both frameworks work together but stay independent
```

**Use Case**: New SAP project needs complete quality foundation

---

## Architecture Decision

### ✅ CORRECT (Current State)

**Feng Shui**: `tools/fengshui/` (code quality infrastructure)  
**Gu Wu**: `tests/guwu/` (test quality infrastructure)

**Rationale**:
- Clear separation of concerns
- Independent reusability
- Focused evolution paths
- Easy to understand and explain

### ❌ WRONG (What to Avoid)

**Anti-Pattern 1**: Move Feng Shui into tests/  
- Problem: Feng Shui checks ALL code, not just tests
- Result: Would need to scan up to parent directories (breaks encapsulation)

**Anti-Pattern 2**: Move Gu Wu into tools/fengshui/  
- Problem: Gu Wu is test-specific, not general quality
- Result: Dilutes Feng Shui's focus on code organization

**Anti-Pattern 3**: Merge both into quality/  
- Problem: Two distinct concerns forced together
- Result: Mega-framework that's hard to understand/reuse

---

## Summary

**Two Frameworks, One Goal**:
- Feng Shui: Organize code perfectly
- Gu Wu: Execute tests optimally
- Together: Production-ready quality

**Keep Separate Because**:
- Different domains (code vs tests)
- Different tools (static vs runtime)
- Different workflows (monthly vs continuous)
- Independent reusability
- Clearer identity and purpose

**User Wisdom**: Resist the temptation to merge. Separation creates clarity.

---

## References

- [[Framework Reusability Guide]] - How to copy each framework
- [[Module Quality Gate]] - Feng Shui validation details
- [[Comprehensive Testing Strategy]] - Gu Wu capabilities
- [[Feng Shui Separation of Concerns]] - Core Feng Shui principle
- [[Gu Wu Phase 3 AI Capabilities]] - Complete Gu Wu design

**Status**: ✅ Architecture validated - frameworks remain independent