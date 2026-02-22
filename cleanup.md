# Project Cleanup Routine

**Version**: 1.0  
**Last Updated**: 2026-02-22  
**Purpose**: Systematic identification and removal of obsolete files/folders

---

## 🎯 Cleanup Philosophy

**RULE**: Before deleting, ALWAYS archive to `/archive` with dated folder name.

**Safety First**:
1. ✅ Git checkpoint before cleanup (`git add . && git commit -m "checkpoint: before cleanup"`)
2. ✅ Move to `/archive/[category]_YYYYMMDD/` (not delete directly)
3. ✅ Verify no active dependencies
4. ✅ Git commit after cleanup (`git add . && git commit -m "cleanup: archived [category]"`)

---

## 📋 Step 1: Identify Obsolete Files/Folders

### 1.1 Root Directory Clutter

**Scan for**:
```bash
# List root-level files (should be minimal)
powershell -Command "Get-ChildItem -Path . -File | Select-Object Name"
```

**Valid Root Files** (Keep):
- `.clinerules`
- `.gitignore`
- `.env.example`
- `pytest.ini`
- `pyproject.toml`
- `package.json`
- `setup.py`
- `README.md`
- `PROJECT_TRACKER.md`
- `server.py`
- `run_tests.py`
- `feature_flags.json`

**Archive These** (If Found):
- `*.txt` files (e.g., `feng_shui_output.txt`, `temp_old_tracker.txt`)
- `*.json` files (except `package.json`, `feature_flags.json`)
- `check_db.py` (one-off script)
- `test_logger_endpoints.py` (one-off test)

**Action**:
```bash
# Archive obsolete root files
mkdir -p archive/root_cleanup_20260222
move feng_shui_output.txt archive/root_cleanup_20260222/
move feng_shui_findings.txt archive/root_cleanup_20260222/
move feng_shui_detailed.txt archive/root_cleanup_20260222/
move feng_shui_sample.json archive/root_cleanup_20260222/
move feng_shui_css_analysis.json archive/root_cleanup_20260222/
move temp_old_tracker.txt archive/root_cleanup_20260222/
move check_db.py archive/root_cleanup_20260222/
move test_logger_endpoints.py archive/root_cleanup_20260222/
```

---

### 1.2 Obsolete Folders in Root

**Scan for**:
```bash
# Check for deprecated folders
powershell -Command "Get-ChildItem -Path . -Directory | Select-Object Name"
```

**Valid Root Folders** (Keep):
- `app_v2/` (current frontend)
- `archive/` (historical preservation)
- `core/` (shared services)
- `database/` (SQLite databases)
- `docs/` (documentation)
- `modules/` (modular backend)
- `scripts/` (automation scripts)
- `tests/` (test suites)
- `tools/` (Feng Shui, Gu Wu, Shi Fu)
- `.github/` (CI/CD workflows)

**Archive These** (If Found):
- `data_products_v2/` (moved to `modules/data_products_v2/`)
- `integration/` (moved to appropriate module)
- `log/` (renamed to `modules/logger/`)
- `logs/` (runtime logs, not version controlled)

**Action**:
```bash
# Archive obsolete root folders
mkdir -p archive/folders_cleanup_20260222
move data_products_v2 archive/folders_cleanup_20260222/ 2>$null
move integration archive/folders_cleanup_20260222/ 2>$null
move log archive/folders_cleanup_20260222/ 2>$null
```

---

### 1.3 Scripts Directory Cleanup

**Scan for obsolete scripts**:
```bash
# List all Python scripts
powershell -Command "Get-ChildItem -Path scripts\python -File | Select-Object Name, LastWriteTime"
```

**Categories**:

**Keep (Active)**:
- `rebuild_sqlite_from_csn.py` (database management)
- `validate_hana_csn_compliance.py` (validation)
- `benchmark_knowledge_graph_10k.py` (performance testing)
- `analyze_knowledge_vault.py` (vault analysis)
- `cleanup_*.py` (database cleanup)

**Archive (One-off migrations)**:
- `execute_knowledge_vault_refactoring.py` (vault already reorganized)
- `execute_vault_refactoring_guwu.py` (vault already reorganized)
- `reorganize_knowledge_vault_simple.py` (vault already reorganized)
- `rename_log_to_logger.py` (migration complete)
- `remove_v2_from_apis.py` (migration complete)
- `fix_*_api.py` (one-time fixes)

**Action**:
```bash
# Archive one-off migration scripts
mkdir -p archive/scripts_migrations_20260222
move scripts\python\execute_knowledge_vault_refactoring.py archive\scripts_migrations_20260222\
move scripts\python\execute_vault_refactoring_guwu.py archive\scripts_migrations_20260222\
move scripts\python\reorganize_knowledge_vault_simple.py archive\scripts_migrations_20260222\
move scripts\python\rename_log_to_logger.py archive\scripts_migrations_20260222\
move scripts\python\remove_v2_from_apis.py archive\scripts_migrations_20260222\
move scripts\python\fix_ai_assistant_api.py archive\scripts_migrations_20260222\
move scripts\python\fix_ai_assistant_repository_pattern.py archive\scripts_migrations_20260222\
move scripts\python\fix_guwu_namespace_references.py archive\scripts_migrations_20260222\
```

---

### 1.4 Documentation Cleanup

**Scan docs/ root**:
```bash
powershell -Command "Get-ChildItem -Path docs -File | Select-Object Name"
```

**Valid Root Docs** (Keep):
- None! All docs should be in subdirectories

**Archive These**:
- Any `.md` files in `docs/` root (move to appropriate subdirectory)

**Valid Subdirectories**:
- `docs/knowledge/` (knowledge vault - 7 subdirectories)
- `docs/archive/` (historical docs)
- `docs/planning/` (planning docs)
- `docs/csn/` (SAP CSN specs)
- `docs/fiori/` (SAP Fiori specs)
- `docs/hana-cloud/` (HANA Cloud specs)
- `docs/feng-shui-proposals/` (Feng Shui proposals)
- `docs/guwu-proposals/` (Gu Wu proposals)

**Action**:
```bash
# Move any root docs to appropriate subdirectories
# (Manual review required - depends on content)
```

---

### 1.5 Test Files Cleanup

**Scan for misplaced tests**:
```bash
powershell -Command "Get-ChildItem -Path . -Recurse -Filter 'test_*.py' | Where-Object {$_.DirectoryName -notlike '*tests*' -and $_.DirectoryName -notlike '*archive*'} | Select-Object FullName"
```

**Valid Test Locations**:
- `tests/[module]/` (organized by module)
- `modules/[module]/tests/` (module-specific)

**Archive These**:
- Any `test_*.py` in root directory
- Any `test_*.py` in `scripts/` (except `scripts/test/`)

**Action**:
```bash
# Archive misplaced tests
mkdir -p archive/tests_misplaced_20260222
# (Use search results to move specific files)
```

---

### 1.6 Database Files Cleanup

**Scan for orphaned databases**:
```bash
powershell -Command "Get-ChildItem -Path . -Recurse -Filter '*.db' | Select-Object FullName, Length"
```

**Valid Databases** (Keep):
- `database/p2p_data.db` (main P2P data)
- `database/p2p_graph.db` (knowledge graph)

**Archive These**:
- Any `.db` files outside `database/` folder
- Any backup `.db` files (e.g., `*.db.backup`)

**Action**:
```bash
# Archive orphaned databases
mkdir -p archive/databases_orphaned_20260222
# (Use search results to move specific files)
```

---

### 1.7 Log Files Cleanup

**Scan for log files**:
```bash
powershell -Command "Get-ChildItem -Path . -Recurse -Filter '*.log' | Select-Object FullName"
```

**Valid Locations**:
- None! Logs should not be version controlled

**Action**:
```bash
# Delete all .log files (not archived)
powershell -Command "Get-ChildItem -Path . -Recurse -Filter '*.log' | Remove-Item -Force"

# Add to .gitignore if not present
echo "*.log" >> .gitignore
```

---

### 1.8 Coverage Files Cleanup

**Scan for coverage files**:
```bash
powershell -Command "Get-ChildItem -Path . -Recurse -Filter '.coverage' | Select-Object FullName"
powershell -Command "Get-ChildItem -Path . -Recurse -Filter 'htmlcov' | Select-Object FullName"
```

**Action**:
```bash
# Delete coverage files (not archived)
powershell -Command "Get-ChildItem -Path . -Recurse -Filter '.coverage' | Remove-Item -Force"
powershell -Command "Get-ChildItem -Path . -Recurse -Directory -Filter 'htmlcov' | Remove-Item -Recurse -Force"

# Add to .gitignore if not present
echo ".coverage" >> .gitignore
echo "htmlcov/" >> .gitignore
echo "coverage.xml" >> .gitignore
```

---

## 📋 Step 2: Execute Cleanup

### 2.1 Automated Cleanup Script

Create `scripts/python/project_cleanup.py`:

```python
"""Project cleanup automation script."""
import os
import shutil
from pathlib import Path
from datetime import datetime

# Root directory
ROOT = Path(__file__).parent.parent.parent

# Date for archive folders
DATE = datetime.now().strftime("%Y%m%d")

def archive_file(file_path: Path, category: str):
    """Archive file to /archive/[category]_[DATE]/"""
    archive_dir = ROOT / "archive" / f"{category}_{DATE}"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    dest = archive_dir / file_path.name
    print(f"Archiving: {file_path} -> {dest}")
    shutil.move(str(file_path), str(dest))

def delete_file(file_path: Path):
    """Delete file (for logs, coverage, etc.)"""
    print(f"Deleting: {file_path}")
    file_path.unlink()

def main():
    """Execute cleanup routine."""
    
    # 1. Root directory cleanup
    obsolete_root_files = [
        "feng_shui_output.txt",
        "feng_shui_findings.txt",
        "feng_shui_detailed.txt",
        "feng_shui_sample.json",
        "feng_shui_css_analysis.json",
        "temp_old_tracker.txt",
        "check_db.py",
        "test_logger_endpoints.py",
    ]
    
    for file_name in obsolete_root_files:
        file_path = ROOT / file_name
        if file_path.exists():
            archive_file(file_path, "root_cleanup")
    
    # 2. Log files cleanup (DELETE, not archive)
    for log_file in ROOT.rglob("*.log"):
        delete_file(log_file)
    
    # 3. Coverage files cleanup (DELETE, not archive)
    for cov_file in ROOT.rglob(".coverage"):
        delete_file(cov_file)
    
    for htmlcov_dir in ROOT.rglob("htmlcov"):
        if htmlcov_dir.is_dir():
            print(f"Deleting: {htmlcov_dir}")
            shutil.rmtree(htmlcov_dir)
    
    print("\n✅ Cleanup complete!")

if __name__ == "__main__":
    main()
```

**Run**:
```bash
python scripts/python/project_cleanup.py
```

---

### 2.2 Manual Review Required

**Before archiving, manually review**:

1. **scripts/python/** - Check if migration scripts still needed
2. **docs/** - Verify no important docs in root
3. **tests/** - Confirm all tests properly organized
4. **modules/** - Check for obsolete module versions

**Command to review**:
```bash
# Review scripts
powershell -Command "Get-ChildItem -Path scripts\python -File | Sort-Object LastWriteTime | Select-Object Name, LastWriteTime"

# Review docs
powershell -Command "Get-ChildItem -Path docs -File -Recurse | Where-Object {$_.DirectoryName -like '*docs'} | Select-Object FullName"

# Review tests
powershell -Command "Get-ChildItem -Path tests -File -Recurse | Sort-Object DirectoryName | Select-Object FullName"
```

---

## 📋 Step 3: Verify & Commit

### 3.1 Verification

**Run quality checks**:
```bash
# Feng Shui analysis
python -m tools.fengshui analyze

# Gu Wu test coverage
pytest tests/ -v --cov

# Smoke tests
pytest tests/test_smoke.py -v
```

**Verify no broken imports**:
```bash
python -c "import modules; import core; import tools"
```

---

### 3.2 Git Commit

**Commit cleanup**:
```bash
git add .
git commit -m "cleanup: archived obsolete files and folders (v5.32.0)

WHAT: Systematic cleanup of obsolete files/folders per cleanup.md routine

ARCHIVED:
- Root clutter: feng_shui_*.txt/json, temp_old_tracker.txt, check_db.py
- Migration scripts: execute_vault_refactoring_*.py, rename_log_to_logger.py
- Log files: *.log (deleted, not archived)
- Coverage files: .coverage, htmlcov/ (deleted, not archived)

VERIFIED:
- Feng Shui analysis passing
- All tests passing
- No broken imports"

git tag -a v5.32.0 -m "Project cleanup complete"
git push origin main --tags
```

---

## 🎯 Ongoing Maintenance

### Weekly Cleanup Checklist

- [ ] Run `python scripts/python/project_cleanup.py`
- [ ] Review `git status` for untracked files
- [ ] Check root directory for new clutter
- [ ] Verify `.gitignore` up to date
- [ ] Run Feng Shui analysis

### Monthly Cleanup Checklist

- [ ] Review `/archive` for very old archives (>6 months)
- [ ] Review `/scripts/python` for obsolete scripts
- [ ] Review `/docs` for outdated documentation
- [ ] Review `/tests` for redundant tests
- [ ] Update this cleanup.md with new patterns

---

## 📚 References

- [[Module Federation Standard]] - Module organization rules
- `docs/knowledge/quality-ecosystem/README.md` - Quality tools overview
- `.gitignore` - Version control exclusions
- `PROJECT_TRACKER.md` - Active tasks

---

**Last Cleanup**: 2026-02-22  
**Next Cleanup**: 2026-03-01 (weekly routine)