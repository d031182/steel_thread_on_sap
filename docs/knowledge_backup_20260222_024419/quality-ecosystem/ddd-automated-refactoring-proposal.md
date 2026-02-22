# DDD Automated Refactoring - Phase 8 Proposal

**Status**: 📋 PROPOSED (Feb 13, 2026)  
**Depends On**: DDD Tracker (Phases 1-7) ✅ COMPLETE  
**Estimated Effort**: 6-8 hours  
**Priority**: MEDIUM (Nice-to-have, not critical)

## Overview

Extend the DDD Recommendations Engine (Phase 7) with **automated code generation** that can implement DDD patterns with minimal user intervention.

## Philosophy

**"The Master doesn't just show the path. The Master walks beside you on the journey."**

## Current State (Phase 7 Complete)

✅ **AI Recommendations Engine**:
- Intelligent pattern prioritization
- Step-by-step guidance
- Code examples (copy-paste)
- Effort estimation
- Impact prediction

**Gap**: User must manually implement recommendations

## Proposed: Automated Refactoring

### Goal

Generate PR-ready code changes that implement DDD patterns automatically, with safety checks and rollback capability.

### Scope

**In Scope**:
1. **Code Generation** - Create new files (UnitOfWork, Service classes)
2. **Import Injection** - Update import statements
3. **DI Refactoring** - Add dependency injection
4. **Test Generation** - Create basic test scaffolding
5. **Safety Checks** - Pre-flight validation, backup, rollback

**Out of Scope**:
- Complex logic extraction (too risky)
- Cross-module refactoring (too complex)
- Breaking changes (user must approve)

## Technical Approach

### 1. AST Manipulation

Use Python's `ast` module for safe code transformation:

```python
import ast
import astor

class CodeRefactorer:
    """
    Safe code transformation using AST
    """
    def add_dependency_injection(self, class_node: ast.ClassDef):
        # Transform class to accept injected dependencies
        pass
    
    def extract_to_service_layer(self, route_function: ast.FunctionDef):
        # Extract business logic to service class
        pass
```

### 2. Template Engine

Use Jinja2 for code generation:

```python
from jinja2 import Template

UOW_TEMPLATE = """
class UnitOfWork:
    def __init__(self, connection):
        self._connection = connection
    # ... rest of template
"""

def generate_unit_of_work(module_name: str) -> str:
    return Template(UOW_TEMPLATE).render(module=module_name)
```

### 3. Safety System

**Pre-flight Checks**:
- ✅ Git status clean (no uncommitted changes)
- ✅ All tests passing
- ✅ Backup created (`.bak` files)
- ✅ Dry-run mode (preview changes)

**Rollback**:
- ✅ Git reset if generation fails
- ✅ Restore from `.bak` files
- ✅ Clear rollback instructions

### 4. User Workflow

```bash
# Step 1: Get recommendation
python -m tools.shifu.ddd_recommendations --top 1

# Step 2: Generate code (dry-run)
python -m tools.shifu.ddd_refactorer --pattern "Unit of Work" --dry-run

# Step 3: Review proposed changes
# (Shows diff, lists files to be created/modified)

# Step 4: Apply if satisfied
python -m tools.shifu.ddd_refactorer --pattern "Unit of Work" --apply

# Step 5: Run tests
pytest tests/unit/core/services/test_unit_of_work.py

# Step 6: Commit
git add . && git commit -m "feat: Add Unit of Work pattern"
```

## Implementation Plan

### Phase 8.1: Code Generation (2 hours)

**Deliverables**:
- `tools/shifu/ddd_refactorer.py` (core engine)
- File creation (UnitOfWork, Service classes)
- Template system (Jinja2)
- Dry-run mode

### Phase 8.2: AST Refactoring (2 hours)

**Deliverables**:
- Import statement injection
- DI parameter addition
- Simple method extraction
- Safe transformations only

### Phase 8.3: Test Generation (1 hour)

**Deliverables**:
- Test file scaffolding
- Basic test cases (happy path)
- pytest integration

### Phase 8.4: Safety System (2 hours)

**Deliverables**:
- Pre-flight validation
- Git status check
- Backup/restore
- Rollback mechanism

### Phase 8.5: Integration (1 hour)

**Deliverables**:
- CLI integration
- Dashboard "Apply" button (terminal)
- User documentation

## Example Output

```bash
$ python -m tools.shifu.ddd_refactorer --pattern "Unit of Work" --dry-run

🔍 Analyzing codebase...
✅ Pre-flight checks passed

📝 Proposed Changes:

CREATE: core/services/unit_of_work.py (42 lines)
  - UnitOfWork class with context manager
  - Connection handling
  - Transaction management

CREATE: tests/unit/core/services/test_unit_of_work.py (67 lines)
  - Test commit scenario
  - Test rollback scenario
  - Test nested contexts

MODIFY: modules/data_products_v2/backend/service.py
  - Add UnitOfWork import
  - Wrap multi-step operations in context
  - Line 45-62 (18 lines changed)

Maturity Gain: +19 points (25 → 44)
Estimated Time: 0.5 hours (vs 4-6 hours manual)

Apply changes? [y/N]
```

## Benefits

### For Developers
1. **95% Time Savings** - 30 min vs 6 hours
2. **Zero Typos** - Generated code perfect
3. **Consistent Style** - Project standards enforced
4. **Safe** - Rollback if issues

### For Teams
1. **Faster Adoption** - Lower barrier to entry
2. **Quality** - Best practices automatic
3. **Learning** - Review generated code
4. **Velocity** - Ship features faster

## Risks & Mitigation

### Risk 1: Code Generation Bugs

**Mitigation**:
- Dry-run mode (preview first)
- Extensive test suite for refactorer
- Safe AST transformations only
- User review before apply

### Risk 2: Project-Specific Patterns

**Mitigation**:
- Configurable templates
- Pattern detection (learn from codebase)
- Manual override options
- Incremental adoption

### Risk 3: Complex Refactoring

**Mitigation**:
- Start with simple patterns (UnitOfWork)
- Explicitly state limitations
- Human review for complex cases
- Fail gracefully with clear messages

## Decision Factors

### Build Phase 8 If:

1. ✅ DDD adoption is blocker for team
2. ✅ Manual implementation taking too long
3. ✅ Need to refactor many modules (10+)
4. ✅ Team has 6-8 hours to invest
5. ✅ High confidence in rollback safety

### Skip Phase 8 If:

1. ✅ Only 4 modules need refactoring (can do manually)
2. ✅ Team prefers understanding over automation
3. ✅ Time-constrained (already 10.5 hours invested)
4. ✅ Phase 7 recommendations sufficient
5. ✅ Want to validate Phases 1-7 first

## My Recommendation

**⏸️ PAUSE - Validate Phases 1-7 First**

**Rationale**:
1. We've already invested 10.5 hours (vs 4-6 estimate)
2. Phase 7 (AI Recommendations) is excellent and sufficient
3. Only 4 modules need refactoring (manageable manually)
4. Phase 8 adds complexity (AST, code gen, safety)
5. Better to **use** the system before **extending** it

**Alternative Approach**:
- Use Phases 1-7 for 2-4 weeks
- Manually implement 1-2 patterns (Unit of Work, Service Layer)
- Assess if automation actually needed
- Revisit Phase 8 if clear value demonstrated

**If automation truly needed**: Consider simpler approaches first:
- File templates (cookiecutter style)
- Code snippets (VS Code extensions)
- Interactive wizards (CLI prompts)
- Before full AST-based refactoring

## Estimated ROI

**Phase 8 Investment**: 6-8 hours development

**Payback Calculation**:
- Manual implementation: 4-6 hours per pattern per module
- Automated: 0.5 hours per pattern per module
- Savings per module: 3.5-5.5 hours

**Break-even**: 2-3 modules (already have only 4 modules)

**Conclusion**: Marginal ROI for current project size

## Next Steps

**Option A**: Proceed with Phase 8 (6-8 hours)
- Full automated refactoring system
- AST-based code generation
- Safety + rollback mechanisms

**Option B**: Pause and validate (RECOMMENDED)
- Use Phases 1-7 for 2-4 weeks
- Manually implement patterns
- Gather user feedback
- Revisit if needed

**Option C**: Lightweight alternative (2-3 hours)
- File templates only (no AST)
- Code snippets
- Interactive wizard
- Less powerful but safer

---

**What would you like to do?**