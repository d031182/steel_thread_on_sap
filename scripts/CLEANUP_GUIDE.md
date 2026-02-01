# Project Cleanup Guide - "Feng Shui" Philosophy

**Purpose**: Holistic guide for cleaning up scripts AND knowledge vault  
**Last Updated**: 2026-02-01  
**Philosophy**: Everything in its place, clean and organized  
**Applies to**: 
- `scripts/` directory (scripts cleanup)
- `docs/knowledge/` vault (documentation maintenance)

---

## Overview

This guide provides a structured "feng shui" approach to project-wide cleanup:
1. **Scripts Cleanup**: Remove unused/old scripts from `scripts/` directory
2. **Vault Maintenance**: Clean obsolete planning docs from `docs/knowledge/` vault

The two-phase approach ensures complete project organization.

---

## Directory Structure & Cleanup Rules

### 1. **scripts/tmp/** - One-Shot Scripts 🔴 HIGH PRIORITY

**Purpose**: Temporary scripts created by AI for immediate use, unlikely to be reused

**Cleanup Rule**: ⚠️ **AGGRESSIVE** - Delete files older than 7 days
- These are disposable by definition
- Files here should be deleted regularly
- No user confirmation needed for files >7 days old

**Procedure**:
```bash
# List files older than 7 days
python scripts/python/cleanup_unused_scripts.py --threshold 7 --dry-run

# Execute cleanup automatically
python scripts/python/cleanup_unused_scripts.py --threshold 7 --execute --auto-tmp
```

**Manual Review**:
```powershell
# Windows: List files in tmp/ with dates
Get-ChildItem scripts/tmp/*.py | Select-Object Name, LastWriteTime | Sort-Object LastWriteTime
```

---

### 2. **scripts/python/** - Utility Scripts 🟡 MODERATE PRIORITY

**Purpose**: Reusable utility scripts for ongoing project use

**Cleanup Rule**: ⚠️ **CONSERVATIVE** - Review files older than 30 days
- Check if script name follows common patterns (create_, populate_, migrate_, etc.)
- Check if mentioned in PROJECT_TRACKER.md
- Manual review recommended before deletion

**Procedure**:
```bash
# Analyze for potentially unused scripts
python scripts/python/cleanup_unused_scripts.py --threshold 30 --dry-run

# Interactive cleanup (asks before each deletion)
python scripts/python/cleanup_unused_scripts.py --threshold 30 --interactive
```

**Manual Review Checklist**:
- [ ] Is script name in PROJECT_TRACKER.md?
- [ ] Does script follow naming pattern (create_*, populate_*, etc.)?
- [ ] Is script referenced in documentation?
- [ ] Could script be useful in future?

**Common Patterns to KEEP**:
- `create_*.py` - Database/data creation
- `populate_*.py` - Data population
- `migrate_*.py` - Migration scripts
- `rebuild_*.py` - Rebuild utilities
- `generate_*.py` - Data generation
- `sync_*.py` - Synchronization
- `import_*.py` - Import utilities
- `init_*.py` - Initialization

---

### 3. **scripts/test/** - Test Scripts 🟢 LOW PRIORITY

**Purpose**: Test, check, verify, and validate scripts

**Cleanup Rule**: ⚠️ **VERY CONSERVATIVE** - Keep unless explicitly obsolete
- Tests provide historical validation
- Only delete if feature tested no longer exists
- Requires explicit justification

**Procedure**:
```bash
# Only analyze, don't execute
python scripts/python/cleanup_unused_scripts.py --threshold 90 --dry-run
```

**Delete Only If**:
- [ ] Feature being tested has been completely removed
- [ ] Test has been superseded by better test
- [ ] Test references non-existent code/modules
- [ ] Explicit decision documented in PROJECT_TRACKER.md

---

### 4. **scripts/sql/** - SQL Scripts 🟢 LOW PRIORITY

**Purpose**: SQL scripts for HANA and SQLite

**Cleanup Rule**: ⚠️ **ARCHIVE** - Don't delete, archive if obsolete
- SQL scripts are documentation of schema evolution
- Move to `scripts/sql/archive/` if obsolete
- Never delete without backup

---

## FENG SHUI Cleanup Workflow 🎯

**When to Trigger**: User mentions "feng shui", "global cleanup", or "organize project"

**Three-Phase Approach**:
1. **Scripts Cleanup** (`scripts/` directory) - Remove clutter
2. **Vault Maintenance** (`docs/knowledge/` vault) - Organize documentation  
3. **Quality Validation** (all files) - Enforce guidelines

---

### Complete Feng Shui Cleanup (Recommended)

**Purpose**: Comprehensive project organization + quality enforcement

**Procedure**:
```bash
# Phase 1: Scripts Cleanup
python scripts/python/cleanup_unused_scripts.py --threshold 7 --dry-run
python scripts/python/cleanup_unused_scripts.py --threshold 7 --execute --auto-tmp

# Phase 2: Vault Maintenance
powershell -ExecutionPolicy Bypass -File scripts/vault_maintenance.ps1

# Phase 3: Quality Validation (AI-driven)
# This phase is performed by AI assistant:
# - Analyze all files for guideline compliance
# - Check module structure against quality gate
# - Validate Fiori UI components
# - Verify unit test coverage
# - Enforce architecture principles
# - Auto-correct non-compliant code where possible

# Phase 4: Commit All Changes
git add -A
git commit -m "[Maintenance] Feng shui cleanup - scripts + vault + quality"
```

**Time**: 15-30 minutes (including quality validation)  
**Frequency**: Monthly or when project feels cluttered

---

## Individual Cleanup Workflows

### Weekly Cleanup (Automated)

**Focus**: `scripts/tmp/` only

```bash
# 1. Review tmp/ scripts older than 7 days
python scripts/python/cleanup_unused_scripts.py --threshold 7 --dry-run

# 2. If no surprises, execute cleanup
python scripts/python/cleanup_unused_scripts.py --threshold 7 --execute --auto-tmp
```

**Time**: 2-5 minutes  
**Frequency**: Every Monday

---

### Monthly Cleanup (Manual Review)

**Focus**: `scripts/python/` - potentially unused utilities

```bash
# 1. Generate report of scripts older than 30 days
python scripts/python/cleanup_unused_scripts.py --threshold 30 --dry-run

# 2. Review each candidate manually
python scripts/python/cleanup_unused_scripts.py --threshold 30 --interactive

# 3. Document decisions in PROJECT_TRACKER.md
```

**Time**: 15-30 minutes  
**Frequency**: First Saturday of each month

---

### Quarterly Audit (Full Review)

**Focus**: All directories, comprehensive audit

**Procedure**:

1. **Analyze All Directories**:
   ```bash
   python scripts/python/cleanup_unused_scripts.py --threshold 90 --dry-run
   ```

2. **Review Each Category**:
   - `scripts/tmp/`: Should be empty (weekly cleanups)
   - `scripts/python/`: Identify rarely-used utilities
   - `scripts/test/`: Identify obsolete tests
   - `scripts/sql/`: Consider archiving old migrations

3. **Document Archive Decisions**:
   - Create `docs/archive/SCRIPTS_ARCHIVE_{DATE}.md`
   - List archived/deleted scripts with justification
   - Update PROJECT_TRACKER.md

**Time**: 1-2 hours  
**Frequency**: Every 3 months (Jan, Apr, Jul, Oct)

---

## Decision Matrix

| Age | Location | Pattern Match | Referenced? | Action |
|-----|----------|---------------|-------------|--------|
| <7d | tmp/ | N/A | N/A | **KEEP** |
| 7-30d | tmp/ | N/A | N/A | **DELETE** |
| >30d | tmp/ | N/A | N/A | **DELETE** |
| <30d | python/ | Any | Any | **KEEP** |
| 30-90d | python/ | Common | Yes | **KEEP** |
| 30-90d | python/ | Common | No | **REVIEW** |
| 30-90d | python/ | Uncommon | Yes | **REVIEW** |
| 30-90d | python/ | Uncommon | No | **DELETE** |
| >90d | python/ | Any | Yes | **REVIEW** |
| >90d | python/ | Any | No | **ARCHIVE** |
| Any | test/ | N/A | Feature exists | **KEEP** |
| Any | test/ | N/A | Feature removed | **DELETE** |
| Any | sql/ | N/A | N/A | **ARCHIVE** (never delete) |

---

## Common Cleanup Scenarios

### Scenario 1: Empty tmp/ directory
**Situation**: Weekly cleanup, tmp/ is empty  
**Action**: None needed, document in PROJECT_TRACKER  
**Time**: 30 seconds

### Scenario 2: 3 files in tmp/ older than 7 days
**Situation**: Weekly cleanup, found old tmp scripts  
**Action**:
```bash
python scripts/python/cleanup_unused_scripts.py --threshold 7 --execute --auto-tmp
```
**Time**: 2 minutes

### Scenario 3: Unsure if python/ script is still used
**Situation**: Monthly cleanup, found old utility script  
**Action**:
1. Check PROJECT_TRACKER.md for references
2. Search codebase: `git grep -i "script_name"`
3. Check git log: `git log --all --oneline -- scripts/python/script_name.py`
4. If no evidence of use in >90 days, archive to `scripts/archive/`

### Scenario 4: Test script for removed feature
**Situation**: Quarterly audit, found test for deleted module  
**Action**:
1. Confirm module no longer exists
2. Document in PROJECT_TRACKER.md: "Removed test_old_module.py - module deleted in v2.0"
3. Delete test script
4. Commit with clear message

---

## Tool Reference

### cleanup_unused_scripts.py

**Options**:
- `--dry-run`: Preview without deleting (default)
- `--execute`: Actually delete files
- `--auto-tmp`: Auto-delete tmp/ files (no prompts)
- `--threshold N`: Age threshold in days (default: 30)
- `--interactive`: Ask before each deletion

**Examples**:
```bash
# Preview all cleanup candidates
python scripts/python/cleanup_unused_scripts.py --dry-run

# Clean tmp/ automatically (7+ days old)
python scripts/python/cleanup_unused_scripts.py --threshold 7 --execute --auto-tmp

# Interactive cleanup of python/ (30+ days old)
python scripts/python/cleanup_unused_scripts.py --threshold 30 --interactive

# Quarterly audit (90+ days old)
python scripts/python/cleanup_unused_scripts.py --threshold 90 --dry-run
```

---

## Best Practices

### DO ✅
- Run weekly cleanup of tmp/ directory
- Use dry-run first to preview changes
- Document deletion decisions in PROJECT_TRACKER.md
- Archive rather than delete when uncertain
- Keep scripts that follow common naming patterns
- Review git history before deleting old scripts

### DON'T ❌
- Delete scripts referenced in PROJECT_TRACKER.md
- Delete SQL scripts without archiving
- Skip dry-run for large cleanups
- Delete test scripts without verifying feature removal
- Rush through monthly/quarterly reviews
- Forget to commit cleanup changes

---

## Maintenance Schedule

| Task | Frequency | Time | Priority |
|------|-----------|------|----------|
| Clean tmp/ | Weekly | 2-5 min | 🔴 HIGH |
| Review python/ | Monthly | 15-30 min | 🟡 MEDIUM |
| Full audit | Quarterly | 1-2 hours | 🟢 LOW |
| Update this guide | As needed | - | - |

---

## Change Log

| Date | Change | Reason |
|------|--------|--------|
| 2026-02-01 | Initial creation | Formalize cleanup procedures |

---

## Phase 2: Vault Maintenance

### What It Does

The vault maintenance script (`scripts/vault_maintenance.ps1`) cleans up:
- Obsolete planning documents in `docs/planning/`
- Empty folders after cleanup
- Outdated session notes

### When to Run

- Monthly as part of feng shui cleanup
- When `docs/planning/` gets cluttered
- Before major project milestones
- When vault maintenance script is updated

### Manual Execution

```powershell
# Review what will be cleaned
Get-Content scripts/vault_maintenance.ps1

# Execute cleanup
powershell -ExecutionPolicy Bypass -File scripts/vault_maintenance.ps1

# Commit results
git add -A
git commit -m "[Maintenance] Vault maintenance cleanup"
```

---

## Phase 3: Quality Validation ⭐ NEW

### What It Does

**Purpose**: Comprehensive quality audit - enforce all project guidelines

**AI-Driven Analysis**:
The AI assistant performs a systematic review of ALL project files to ensure compliance with established standards.

### Quality Checks Performed

#### 1. Module Compliance
- ✅ Check `modules/*/module.json` structure
- ✅ Verify module.json CONTRACT (backend.blueprint, module_path)
- ✅ Run `python core/quality/module_quality_gate.py [module]`
- ✅ Validate backend/__init__.py exports blueprint
- ✅ Check for DI violations (.connection, .service access)
- ✅ Verify loose coupling (no direct module imports)

**Reference**: `core/quality/README.md`, `.clinerules` (Modular Architecture section)

#### 2. SAP Fiori UI Compliance
- ✅ Standard controls used (InputListItem, not CustomListItem)
- ✅ No CSS hacks (!important, custom padding overrides)
- ✅ Pure JavaScript (easier debugging than XML)
- ✅ Proper control selection for use case
- ✅ Accessibility standards

**Reference**: `.clinerules` (SAP Fiori Compliance section), `docs/fiori/`

#### 3. Unit Testing Standards
- ✅ 100% API method coverage for business logic
- ✅ Tests run in Node.js (not browser) for backend
- ✅ Tests complete in < 5 seconds
- ✅ Mock dependencies for isolation
- ✅ Test success AND error scenarios

**Reference**: `.clinerules` (Comprehensive Testing section)

#### 4. Architecture Principles
- ✅ API-First development (logic before UI)
- ✅ Dependency injection (no hardcoded dependencies)
- ✅ Interface-based design (core/interfaces/)
- ✅ Zero UI dependencies in business logic
- ✅ Async/Promise-based APIs

**Reference**: `.clinerules` (API-First Development, Architecture sections)

#### 5. File Organization
- ✅ Scripts in correct directories (python/, test/, tmp/, sql/)
- ✅ Documentation in knowledge vault (`docs/knowledge/`)
- ✅ No orphaned .md files in root (except core docs)
- ✅ Proper use of [[wikilinks]] in documentation

**Reference**: `.clinerules` (Knowledge Vault Documentation section)

#### 6. Code Quality
- ✅ Windows encoding (UTF-8) for all Python files
- ✅ Error handling patterns followed
- ✅ No hardcoded credentials or sensitive data
- ✅ Proper logging (not print statements)
- ✅ Clear, documented code

**Reference**: `docs/knowledge/guidelines/`

### Validation Process

**When AI Performs Quality Validation**:
1. User requests "feng shui cleanup"
2. AI completes Phases 1-2 (scripts + vault)
3. AI analyzes ALL project files against guidelines
4. AI identifies non-compliant code
5. AI attempts to auto-correct violations
6. AI reports findings and corrections

**AI Actions**:
- **Auto-Correct**: Fix guideline violations automatically where safe
- **Report**: List violations that need manual review
- **Enhance**: Add missing tests, documentation, error handling
- **Refactor**: Improve code to match architecture principles

**Example Corrections**:
- Add missing `module.json` fields
- Replace CustomListItem with InputListItem
- Add unit tests for untested methods
- Extract hardcoded dependencies to DI
- Move inline business logic to API layer

### Manual Quality Validation

**You can also run quality checks manually**:

```bash
# Check specific module
python core/quality/module_quality_gate.py knowledge_graph

# Check all modules
for module in modules/*/; do 
    python core/quality/module_quality_gate.py $(basename $module)
done
```

### Quality Validation Checklist

After feng shui cleanup with quality validation, verify:

- [ ] All modules pass quality gate (exit 0)
- [ ] No DI violations in module code
- [ ] Fiori UI uses standard controls only
- [ ] Unit tests exist for all business logic APIs
- [ ] Architecture principles followed (API-first, DI, interfaces)
- [ ] Files organized per directory conventions
- [ ] No hardcoded dependencies or credentials
- [ ] Documentation updated and properly linked

### When to Skip Quality Validation

**Time-constrained scenarios**:
- Quick weekly cleanup (scripts/tmp only)
- Urgent production issue (defer to next monthly)
- No code changes since last validation

**Still run Phases 1-2** even when skipping quality validation.

---

## Related Documentation

- [[Script Directory Conventions]] - Directory structure standards
- `PROJECT_TRACKER.md` - Project history and active work
- `scripts/python/cleanup_unused_scripts.py` - Automated script cleanup
- `scripts/vault_maintenance.ps1` - Knowledge vault maintenance
- `docs/knowledge/README.md` - Vault structure and conventions

---

## Feng Shui Philosophy

**Core Principle**: Holistic project excellence - organization + quality

**Three Pillars**:
1. **Organization** - Everything in its place (scripts, docs)
2. **Maintenance** - Remove obsolete, archive old
3. **Quality** - Enforce guidelines, improve code

**Benefits**:
- ✅ Clean scripts directory (no clutter)
- ✅ Organized documentation vault (current knowledge only)
- ✅ Guideline compliance (consistent quality)
- ✅ Architecture integrity (principles enforced)
- ✅ Clear project structure (easy navigation)
- ✅ Reduced cognitive load (find things quickly)
- ✅ Better maintenance (proactive vs reactive)
- ✅ Technical debt prevention (catch issues early)

**Philosophy in Action**:
```
Feng Shui Cleanup = Organization + Maintenance + Quality Validation

Not just "clean up files"
But "elevate the entire codebase"
```

**Remember**: 
- When in doubt, ARCHIVE rather than DELETE
- Disk space is cheap, recreating lost work is expensive
- Clean project = clear mind = better code
- Quality is continuous, not a one-time event
