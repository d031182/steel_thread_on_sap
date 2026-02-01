# Feng Shui Phase 5: File Organization Validation

**Added**: February 1, 2026  
**Philosophy**: Every file should be in its proper place - organization matters everywhere  
**User Insight**: "Misplaced files check is not only applicable for root folder, but actually for all folders"

---

## Core Principle

**Each directory has a purpose** - files should match that purpose.

**Not just root cleanup** - this applies to EVERY directory in the project.

---

## Directory Organization Rules

### Root Directory `/`
**Should Contain ONLY**:
- ✅ Entry points: `server.py`, `app.py`
- ✅ Essential configs: `.clinerules`, `.gitignore`, `package.json`, `playwright.config.js`
- ✅ Core documentation: `README.md`, `PROJECT_TRACKER.md`
- ✅ Feature flags: `feature_flags.json`

**Should NOT Contain**:
- ❌ Test output: `data_*_response.json`, `*_output.json`
- ❌ Temporary files: `temp_*.py`, `old_*.py`, `test_*.py`
- ❌ Test data: `jira_issue.json`, `sample_data.json`
- ❌ Databases: `*.db` (should be in `app/database/`)
- ❌ Environment files: `*-env.json` (should be in `app/` or `.gitignore`)
- ❌ Logs: `*.log` (should be in `logs/`)

### docs/
**Should Contain**:
- ✅ Organizational: One-time setup/migration docs
- ✅ Reference: Long-term reference documentation

**Should NOT Contain**:
- ❌ Active work: Current planning/sessions → `docs/knowledge/`
- ❌ Architecture: Design decisions → `docs/knowledge/architecture/`
- ❌ Guidelines: Development standards → `docs/knowledge/guidelines/`

### docs/knowledge/
**Should Contain** (per subdirectories):
- `architecture/` - Design decisions, patterns
- `components/` - System components documentation
- `guides/` - How-to guides, procedures
- `guidelines/` - Development standards
- `requirements/` - Business/technical requirements

**Should NOT Contain**:
- ❌ Files in wrong subdirectory (guide in architecture/, etc.)
- ❌ Orphaned .md files without [[wikilinks]]
- ❌ Duplicate content (consolidate similar docs)

### docs/planning/
**Should Contain**:
- ✅ Active planning documents
- ✅ Feature proposals not yet implemented

**Should NOT Contain**:
- ❌ Completed work → Archive or move to `docs/knowledge/`
- ❌ Implementation details → `docs/knowledge/architecture/`

### scripts/tmp/
**Should Contain**:
- ✅ One-shot, disposable scripts
- ✅ Files < 7 days old

**Should NOT Contain**:
- ❌ Reusable utilities → `scripts/python/`
- ❌ Test scripts → `scripts/test/`
- ❌ Files > 7 days old → DELETE

### scripts/python/
**Should Contain**:
- ✅ Reusable utility scripts
- ✅ Named with clear patterns: `create_*.py`, `populate_*.py`, etc.

**Should NOT Contain**:
- ❌ One-shot scripts → `scripts/tmp/`
- ❌ Test/validation scripts → `scripts/test/`
- ❌ SQL scripts → `scripts/sql/`

### scripts/test/
**Should Contain**:
- ✅ Test/validation/check scripts
- ✅ Scripts prefixed: `test_*.py`, `check_*.py`, `verify_*.py`, `validate_*.py`

**Should NOT Contain**:
- ❌ Utility scripts → `scripts/python/`
- ❌ Data generation → `scripts/python/`

### app/
**Should Contain**:
- ✅ Flask application code
- ✅ Application-specific configs: `.env`, `requirements.txt`
- ✅ Backend logic: `app.py`

**Should NOT Contain**:
- ❌ Test scripts → `scripts/test/`
- ❌ Utility scripts → `scripts/python/`
- ❌ Documentation → `docs/`

### app/database/
**Should Contain**:
- ✅ SQLite database files: `*.db`
- ✅ Database schemas: `schema/`

**Should NOT Contain**:
- ❌ Python scripts → `scripts/python/`
- ❌ Documentation → `docs/`

### modules/
**Should Contain**:
- ✅ Self-contained modules with structure:
  - `module.json`, `backend/`, `tests/`, `README.md`

**Should NOT Contain**:
- ❌ Loose Python files in modules/ root
- ❌ Test scripts outside module tests/
- ❌ Shared utilities → `core/services/`

### core/
**Should Contain**:
- ✅ Shared infrastructure
- ✅ `interfaces/`, `services/`, `quality/`

**Should NOT Contain**:
- ❌ Module-specific code → `modules/`
- ❌ Application logic → `app/`
- ❌ Scripts → `scripts/`

---

## Feng Shui Phase 5 Checklist

During cleanup, AI assistant checks:

### Root Directory
- [ ] No test output files (`*_response.json`, `*_output.json`)
- [ ] No temporary files (`temp_*.py`, `old_*.py`, `test_*.py`)
- [ ] No test data (`*_issue.json`, `sample_*.json`)
- [ ] No databases (`*.db` → should be in `app/database/`)
- [ ] No environment files (`*-env.json` → should be in `app/`)
- [ ] No log files (`*.log` → should be in `logs/`)

### docs/ Hierarchy
- [ ] No .md files in wrong subdirectories
- [ ] Planning docs are current (not completed work)
- [ ] Knowledge vault properly organized by type
- [ ] No orphaned docs without [[wikilinks]]

### scripts/ Hierarchy  
- [ ] Reusable utils in `python/` not `tmp/`
- [ ] Test scripts in `test/` not `python/`
- [ ] One-shot scripts in `tmp/` not `python/`
- [ ] SQL scripts in `sql/` not `python/`

### app/ Organization
- [ ] No scripts mixed with application code
- [ ] Database files in `database/` subdirectory
- [ ] Environment configs properly placed

### modules/ Structure
- [ ] Each module follows standard structure
- [ ] No loose files in modules/ root
- [ ] Tests in module `tests/` directory

### core/ Organization
- [ ] Only shared infrastructure
- [ ] Proper separation: interfaces/, services/, quality/
- [ ] No module-specific code

---

## Automation Opportunity

**Future Enhancement**: Python script to detect misplaced files

```python
# Future: scripts/python/check_file_organization.py
# Scans entire project for misplaced files
# Reports violations with suggestions
```

**Checks**:
- File extension matches directory purpose
- File naming matches directory conventions
- File content matches directory category
- No duplicate content across directories

---

## Common Misplacement Patterns

| Misplaced File | Correct Location | Reason |
|----------------|------------------|---------|
| `test_*.py` in root | `scripts/test/` | Test scripts have dedicated directory |
| `temp_*.py` in root | `scripts/tmp/` or DELETE | Temporary files should be in tmp/ |
| `*.db` in root | `app/database/` | Databases have dedicated directory |
| Guide in `docs/` | `docs/knowledge/guides/` | Knowledge vault structure |
| Planning in `docs/knowledge/` | `docs/planning/` | Active planning has own directory |
| Util in `scripts/test/` | `scripts/python/` | Reusable utils belong in python/ |
| Test in `scripts/python/` | `scripts/test/` | Tests belong in test/ |
| Module code in `core/` | `modules/[name]/` | Module-specific should be in modules/ |

---

## Examples from This Project

### Discovered Misplacements (Feb 1, 2026)

**Root Directory**:
- ❌ `data_mode_response.json` → DELETED (test output)
- ❌ `temp_old_service.py` → DELETED (old code)
- ❌ `jira_issue.json` → DELETED (test data)
- ⚠️ `data_products.db` → Should be in `app/database/` (or .gitignore)
- ⚠️ `default-env.json` → Should be in `app/` (or .gitignore)

**Actions Taken**:
- Deleted test debris (3 files, 907 lines)
- Recorded pattern in MCP memory
- Added Phase 5 to feng shui system

---

## Integration with Other Phases

**Phase 5 complements**:
- **Phase 1** (Scripts): Checks if scripts are in correct subdirectory
- **Phase 2** (Vault): Checks if docs are in correct subdirectory
- **Phase 3** (Quality): File organization is part of code quality
- **Phase 4** (Architecture): Well-organized files = maintainable architecture

**Phase 5 is not a separate pass** - it's integrated into all phases:
- Phase 1: Check scripts are in right scripts/ subdirectory
- Phase 2: Check docs are in right docs/ subdirectory
- Root check: Special focus on root directory cleanliness

---

## Philosophy

**Like organizing physical space**:
- Kitchen items in kitchen (not bedroom)
- Books on bookshelf (not floor)
- Tools in toolbox (not living room)

**Codebase organization**:
- Tests in test directory (not root)
- Utilities in scripts/python/ (not root)
- Docs in knowledge vault (not scattered)
- Databases in database directory (not root)

**Result**: Clear project structure = clear mental model = efficient development

---

## For Future Feng Shui Cleanups

When AI runs feng shui, check:
1. ✅ Root directory clean (Phase 5 root check)
2. ✅ Each directory contains only appropriate file types
3. ✅ Files follow naming conventions for their location
4. ✅ No duplicate/similar content across directories
5. ✅ Project structure matches conventions in .clinerules

**Living Document**: This guide will evolve as new misplacement patterns are discovered.

---

**Status**: ✅ Active - Part of feng shui system  
**Scope**: All project directories, not just root  
**Frequency**: Every feng shui cleanup (monthly recommended)  
**Reference**: [[Modular Architecture]], .clinerules (file organization)