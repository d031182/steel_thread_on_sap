#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migrate existing module tests to Gu Wu framework structure.

This script:
1. Finds all test files in modules/*/tests/
2. Copies them to tests/unit/modules/[module_name]/
3. Adds pytest markers (@pytest.mark.unit, @pytest.mark.fast)
4. Updates imports to work from new location
5. Preserves original files (non-destructive)
"""

import os
import re
import sys
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
MODULES_DIR = PROJECT_ROOT / "modules"
TESTS_DIR = PROJECT_ROOT / "tests"

# Test files found in modules
TEST_FILES = {
    # Python tests
    "api_playground": ["test_api_playground.py", "test_playground_service.py"],
    "csn_validation": ["test_csn_validation_api.py"],
    "data_products": ["sqlite_data_products_service.test.py", "test_sqlite_data_source.py"],
    "feature_manager": ["feature_flags.test.py", "test_feature_manager.py", "test_server_simple.py"],
    "hana_connection": ["hana_connection_service.test.py", "test_hana_data_source.py"],
    "knowledge_graph": [
        "test_api_csn_mode.py",
        "test_api_v2_integration.py",
        "test_api_v2_layouts.py",
        "test_csn_schema_graph_builder_v2.py",
        "test_csn_schema_graph_builder.py",
        "test_property_graph_service.py"
    ],
    "log_manager": ["sqlite_logger.test.py", "test_logging_service.py", "test_module_import.py"],
    "login_manager": ["test_auth_service.py"],
    "sql_execution": ["test_sql_execution_api.py"],
    "sqlite_connection": ["test_sqlite_data_source.py"],
}


def add_pytest_markers(content: str, test_file: str) -> str:
    """Add pytest markers to test functions if not already present."""
    
    # Determine test type based on filename/content
    is_integration = any(keyword in test_file.lower() for keyword in ['integration', 'api_v2'])
    marker = '@pytest.mark.integration' if is_integration else '@pytest.mark.unit'
    
    # Check if pytest is imported
    if 'import pytest' not in content:
        # Add pytest import at the top
        lines = content.split('\n')
        import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_idx = i + 1
            elif line.strip() == '' and import_idx > 0:
                break
        lines.insert(import_idx, 'import pytest')
        content = '\n'.join(lines)
    
    # Add markers to test functions
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a test function definition
        if line.strip().startswith('def test_') and '@pytest.mark' not in '\n'.join(lines[max(0, i-3):i]):
            # Add markers before the function
            indent = ' ' * (len(line) - len(line.lstrip()))
            new_lines.append(f'{indent}{marker}')
            new_lines.append(f'{indent}@pytest.mark.fast')
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def update_imports(content: str, module_name: str) -> str:
    """Update imports to work from new test location."""
    
    # Replace relative imports from modules
    # from ..backend.service import X  ->  from modules.module_name.backend.service import X
    content = re.sub(
        r'from \.\.([a-z_]+) import',
        f'from modules.{module_name}.\\1 import',
        content
    )
    
    # from backend.service import X  ->  from modules.module_name.backend.service import X
    content = re.sub(
        r'from backend\.([a-z_]+) import',
        f'from modules.{module_name}.backend.\\1 import',
        content
    )
    
    return content


def migrate_test_file(module_name: str, test_file: str) -> bool:
    """Migrate a single test file to Gu Wu structure."""
    
    source_path = MODULES_DIR / module_name / "tests" / test_file
    
    if not source_path.exists():
        print(f"[WARN] Source not found: {source_path}")
        return False
    
    # Determine destination
    if 'integration' in test_file.lower() or 'api_v2' in test_file.lower():
        dest_dir = TESTS_DIR / "integration" / "modules" / module_name
    else:
        dest_dir = TESTS_DIR / "unit" / "modules" / module_name
    
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / test_file
    
    # Read source
    content = source_path.read_text(encoding='utf-8')
    
    # Transform content
    content = add_pytest_markers(content, test_file)
    content = update_imports(content, module_name)
    
    # Write to destination
    dest_path.write_text(content, encoding='utf-8')
    
    print(f"[OK] Migrated: {module_name}/tests/{test_file} -> {dest_path.relative_to(PROJECT_ROOT)}")
    return True


def create_init_files():
    """Create __init__.py files in test directories."""
    
    for layer in ['unit', 'integration']:
        modules_dir = TESTS_DIR / layer / "modules"
        modules_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py in modules/
        (modules_dir / "__init__.py").write_text('"""Module tests."""\n', encoding='utf-8')
        
        # Create __init__.py in each module directory
        for module_dir in modules_dir.iterdir():
            if module_dir.is_dir():
                (module_dir / "__init__.py").write_text(f'"""Tests for {module_dir.name} module."""\n', encoding='utf-8')


def main():
    """Main migration function."""
    
    print("=" * 80)
    print("[Gu Wu] TEST MIGRATION")
    print("=" * 80)
    print()
    
    total = 0
    migrated = 0
    
    for module_name, test_files in TEST_FILES.items():
        print(f"\n[Module] {module_name}")
        for test_file in test_files:
            total += 1
            if migrate_test_file(module_name, test_file):
                migrated += 1
    
    print()
    print("=" * 80)
    print(f"[DONE] Migration complete: {migrated}/{total} files migrated")
    print("=" * 80)
    
    # Create __init__.py files
    create_init_files()
    print("\n[OK] Created __init__.py files in test directories")
    
    print("\n[Next Steps]:")
    print("   1. Run: pytest tests/unit/modules/ -v")
    print("   2. Fix any import errors")
    print("   3. Verify all tests pass")
    print("   4. Stage migrated tests: git add tests/")


if __name__ == "__main__":
    main()