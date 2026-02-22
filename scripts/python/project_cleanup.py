"""Project cleanup automation script.

This script implements the cleanup routine documented in cleanup.md.
It archives obsolete files to /archive/[category]_[DATE]/ and deletes
temporary files (logs, coverage) that should not be version controlled.

Usage:
    python scripts/python/project_cleanup.py [--dry-run]
"""
import os
import shutil
import sys
from pathlib import Path
from datetime import datetime

# Root directory
ROOT = Path(__file__).parent.parent.parent

# Date for archive folders
DATE = datetime.now().strftime("%Y%m%d")

# Check for dry-run mode
DRY_RUN = "--dry-run" in sys.argv


def archive_file(file_path: Path, category: str):
    """Archive file to /archive/[category]_[DATE]/"""
    archive_dir = ROOT / "archive" / f"{category}_{DATE}"
    
    if not file_path.exists():
        return False
    
    if DRY_RUN:
        print(f"[DRY-RUN] Would archive: {file_path} -> {archive_dir}/{file_path.name}")
        return True
    
    archive_dir.mkdir(parents=True, exist_ok=True)
    dest = archive_dir / file_path.name
    print(f"Archiving: {file_path} -> {dest}")
    shutil.move(str(file_path), str(dest))
    return True


def delete_file(file_path: Path):
    """Delete file (for logs, coverage, etc.)"""
    if not file_path.exists():
        return False
    
    if DRY_RUN:
        print(f"[DRY-RUN] Would delete: {file_path}")
        return True
    
    print(f"Deleting: {file_path}")
    file_path.unlink()
    return True


def delete_directory(dir_path: Path):
    """Delete directory recursively"""
    if not dir_path.exists() or not dir_path.is_dir():
        return False
    
    if DRY_RUN:
        print(f"[DRY-RUN] Would delete directory: {dir_path}")
        return True
    
    print(f"Deleting directory: {dir_path}")
    shutil.rmtree(dir_path)
    return True


def main():
    """Execute cleanup routine."""
    
    if DRY_RUN:
        print("=" * 60)
        print("DRY-RUN MODE - No files will be modified")
        print("=" * 60)
        print()
    
    archived_count = 0
    deleted_count = 0
    
    # ========================================
    # 1. Root directory cleanup
    # ========================================
    print("Step 1: Root directory cleanup")
    print("-" * 60)
    
    obsolete_root_files = [
        "feng_shui_output.txt",
        "feng_shui_findings.txt",
        "feng_shui_detailed.txt",
        "feng_shui_sample.json",
        "feng_shui_css_analysis.json",
        "feng_shui_findings.json",
        "temp_old_tracker.txt",
        "check_db.py",
        "test_logger_endpoints.py",
    ]
    
    for file_name in obsolete_root_files:
        file_path = ROOT / file_name
        if archive_file(file_path, "root_cleanup"):
            archived_count += 1
    
    print()
    
    # ========================================
    # 2. Obsolete root folders
    # ========================================
    print("Step 2: Obsolete root folders")
    print("-" * 60)
    
    obsolete_root_folders = [
        "data_products_v2",  # Moved to modules/
        "integration",       # Moved to appropriate module
        "log",              # Renamed to modules/logger/
        "logs",             # Runtime logs
    ]
    
    for folder_name in obsolete_root_folders:
        folder_path = ROOT / folder_name
        if folder_path.exists() and folder_path.is_dir():
            archive_dir = ROOT / "archive" / f"folders_cleanup_{DATE}"
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            if DRY_RUN:
                print(f"[DRY-RUN] Would archive folder: {folder_path} -> {archive_dir}/{folder_name}")
                archived_count += 1
            else:
                dest = archive_dir / folder_name
                print(f"Archiving folder: {folder_path} -> {dest}")
                shutil.move(str(folder_path), str(dest))
                archived_count += 1
    
    print()
    
    # ========================================
    # 3. Migration scripts
    # ========================================
    print("Step 3: One-off migration scripts")
    print("-" * 60)
    
    migration_scripts = [
        "scripts/python/execute_knowledge_vault_refactoring.py",
        "scripts/python/execute_vault_refactoring_guwu.py",
        "scripts/python/reorganize_knowledge_vault_simple.py",
        "scripts/python/rename_log_to_logger.py",
        "scripts/python/remove_v2_from_apis.py",
        "scripts/python/fix_ai_assistant_api.py",
        "scripts/python/fix_ai_assistant_repository_pattern.py",
        "scripts/python/fix_guwu_namespace_references.py",
    ]
    
    for script_path_str in migration_scripts:
        script_path = ROOT / script_path_str
        if archive_file(script_path, "scripts_migrations"):
            archived_count += 1
    
    print()
    
    # ========================================
    # 4. Log files (DELETE, not archive)
    # ========================================
    print("Step 4: Log files cleanup")
    print("-" * 60)
    
    for log_file in ROOT.rglob("*.log"):
        # Skip archive directory
        if "archive" in log_file.parts:
            continue
        if delete_file(log_file):
            deleted_count += 1
    
    print()
    
    # ========================================
    # 5. Coverage files (DELETE, not archive)
    # ========================================
    print("Step 5: Coverage files cleanup")
    print("-" * 60)
    
    for cov_file in ROOT.rglob(".coverage"):
        # Skip archive directory
        if "archive" in cov_file.parts:
            continue
        if delete_file(cov_file):
            deleted_count += 1
    
    for htmlcov_dir in ROOT.rglob("htmlcov"):
        # Skip archive directory
        if "archive" in htmlcov_dir.parts:
            continue
        if htmlcov_dir.is_dir():
            if delete_directory(htmlcov_dir):
                deleted_count += 1
    
    # Also check for coverage.xml
    coverage_xml = ROOT / "coverage.xml"
    if delete_file(coverage_xml):
        deleted_count += 1
    
    print()
    
    # ========================================
    # Summary
    # ========================================
    print("=" * 60)
    print("Cleanup Summary")
    print("=" * 60)
    print(f"Files/folders archived: {archived_count}")
    print(f"Files/folders deleted: {deleted_count}")
    
    if DRY_RUN:
        print()
        print("This was a DRY-RUN. No files were modified.")
        print("Run without --dry-run to execute cleanup.")
    else:
        print()
        print("✅ Cleanup complete!")
        print()
        print("Next steps:")
        print("1. Review changes: git status")
        print("2. Run quality checks: python -m tools.fengshui analyze")
        print("3. Run tests: pytest tests/test_smoke.py -v")
        print("4. Commit: git add . && git commit -m 'cleanup: archived obsolete files'")


if __name__ == "__main__":
    main()