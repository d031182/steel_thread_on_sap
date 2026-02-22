"""
Execute Knowledge Vault Refactoring
====================================

This script executes the knowledge vault reorganization proposed in:
docs/knowledge/vault-reorganization-proposal-2026-02-22.md

It moves files from docs/knowledge/ to organized subdirectories based on:
1. Module-specific content → modules/[module]/
2. Quality ecosystem → quality-ecosystem/
3. Architecture → architecture/
4. Historical → archive/

SAFETY:
- Dry-run mode by default (--dry-run)
- Creates backups before moving
- Validates all paths
- Updates INDEX.md automatically
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Set
import argparse
from datetime import datetime
import re

# Base paths
REPO_ROOT = Path(__file__).parent.parent.parent
KNOWLEDGE_DIR = REPO_ROOT / "docs" / "knowledge"
INDEX_FILE = KNOWLEDGE_DIR / "INDEX.md"

# Category mappings (from proposal)
CATEGORY_MAPPING = {
    # Quality Ecosystem (already exists, consolidate)
    "quality-ecosystem": [
        "feng-shui-architecture-audit-2026-02-15.md",
        "feng-shui-guwu-integration-bridge.md",
        "feng-shui-guwu-e2e-integration-tests.md",
        "feng-shui-guwu-workflow-guide.md",
        "feng-shui-preview-mode-design.md",
        "feng-shui-preview-mode-user-guide.md",
        "feng-shui-preview-mode-validation-results.md",
        "guwu-api-contract-testing-foundation.md",
        "guwu-workflow-for-ai-assistant.md",
        "guwu-resolver-expansion-2026-02-22.md",
        "guwu-refactoring-assessment-med-25.md",
        "quality-ecosystem/README.md",
        "quality-ecosystem/ddd-pattern-tracker.md",
        "quality-ecosystem/ddd-automated-refactoring-proposal.md",
        "quality-ecosystem/gof-pattern-enhancement-proposal.md",
        "quality-ecosystem/gof-enhancement-handoff.md",
        "quality-ecosystem/eager-lazy-loading-patterns-for-quality-tools.md",
        "quality-ecosystem/shi-fu/pattern-recognition-workflow.md",
    ],
    
    # Architecture
    "architecture": [
        "module-federation-standard.md",
        "module-federation-architecture-proposal.md",
        "module-federation-formalization-proposal.md",
        "module-isolation-enforcement-standard.md",
        "frontend-modular-architecture-proposal.md",
        "app-v2-modular-architecture-plan.md",
        "app-v2-configuration-driven-architecture.md",
        "datasource-architecture-refactoring-proposal.md",
        "repository-pattern-modular-architecture.md",
        "service-locator-antipattern-solution.md",
        "configuration-based-dependency-injection.md",
        "data-products-v2-di-refactoring-proposal.md",
        "global-context-state-management-patterns.md",
        "interface-segregation-sql-execution-pattern.md",
        "cosmic-python-patterns.md",
        "ddd-patterns-quality-ecosystem-integration.md",
        "eager-vs-lazy-loading-best-practices.md",
    ],
    
    # AI Assistant Module
    "modules/ai-assistant": [
        "ai-assistant-ux-design.md",
        "ai-assistant-ux-gap-analysis.md",
        "ai-assistant-v2-pydantic-implementation.md",
        "ai-assistant-shell-overlay-implementation.md",
        "ai-assistant-phase-2-implementation.md",
        "ai-assistant-phase-3-conversation-enhancement.md",
        "ai-assistant-phase-4-advanced-features.md",
        "ai-assistant-reality-check-2026-02-15.md",
        "ai-assistant-litellm-integration.md",
        "ai-assistant-implementation-status-2026-02-21.md",
        "ai-assistant-hana-direct-query-limitations.md",
        "ai-assistant-hana-datasource-solution.md",
        "ai-assistant-hana-datasource-issue.md",
        "ai-assistant-hana-fix-summary.md",
        "ai-assistant-hana-table-name-fix.md",
        "ai-assistant-sql-service-hana-issue.md",
        "ai-assistant-module-isolation-audit.md",
        "ai-assistant-database-abstraction-analysis.md",
        "ai-assistant-repository-pattern-implementation-guide.md",
        "sap-ai-core-pydantic-ai-integration.md",
        "pydantic-ai-sap-ai-core-integration.md",
    ],
    
    # Knowledge Graph Module
    "modules/knowledge-graph": [
        "knowledge-graph-v2-architecture-proposal.md",
        "knowledge-graph-v2-api-design.md",
        "knowledge-graph-v2-services-design.md",
        "knowledge-graph-v2-phase-2-complete.md",
        "knowledge-graph-v2-phase-5-frontend-architecture.md",
        "knowledge-graph-v2-feng-shui-audit-2026-02-21.md",
        "knowledge-graph-cache-debugging-lessons.md",
        "knowledge-graph-csn-semantic-completeness-analysis.md",
        "knowledge-graph-ai-assistant-requirements.md",
        "knowledge-graph-semantic-enhancement-implementation-plan.md",
        "knowledge-graph-10k-benchmark-results.md",
    ],
    
    # Data Products Module
    "modules/data-products": [
        "p2p-dashboard-design.md",
        "p2p-database-creation-workflow.md",
    ],
    
    # Logger Module
    "modules/logger": [
        "logger-to-log-module-rename.md",
        "log-viewer-overlay-implementation.md",
        "dual-mode-logging-system.md",
    ],
    
    # UX & Frontend
    "ux-frontend": [
        "sap-fiori-color-integration.md",
        "visjs-library-reference.md",
        "chat-ui-sticky-input-best-practices.md",
        "spa-module-lifecycle-analysis.md",
        "ux-api-test-coverage-audit.md",
        "frontend-api-testing-breakthrough.md",
    ],
    
    # Implementation Tasks (HIGH-X)
    "implementation-tasks": [
        "high-19-endpoint-analysis.md",
        "high-31-advanced-graph-queries-implementation.md",
        "high-32-query-templates-implementation.md",
        "high-33-kgv2-css-refactoring-phase-3-roadmap.md",
        "high-34-kgv2-css-refactoring-phase-1-audit.md",
        "high-38-kgv2-css-refactoring-phase-2-implementation.md",
        "high-39-kgv2-css-refactoring-phase-4-grid-implementation.md",
        "high-40-kgv2-css-refactoring-phase-5-color-contrast.md",
        "high-40-kgv2-css-refactoring-phase-5b-color-redesign.md",
        "high-43-css-systematic-remediation-plan.md",
        "high-46.5-preview-mode-parser-implementation.md",
        "high-46.6-preview-mode-ai-integration.md",
        "high-46.7-preview-mode-cicd-integration.md",
    ],
    
    # APIs & Integration
    "apis-integration": [
        "api-first-contract-testing-methodology.md",
        "ai-data-query-architecture-gap-analysis.md",
        "ai-query-system-implementation-proposal.md",
        "groq-api-reference.md",
        "groq-documentation-overview.md",
        "pydantic-ai-framework.md",
    ],
    
    # Security
    "security": [
        "security-sql-injection-verification-2026-02-21.md",
    ],
    
    # Archive (historical/obsolete)
    "archive": [
        "VAULT_CLEANUP_AUDIT_2026-02-15.md",
        "QUALITY_DOCS_CONSOLIDATION_PROPOSAL.md",
        "vault-reorganization-proposal-2026-02-22.md",  # This proposal itself
        "module-categorization-analysis.md",
        "app-v2-validator-refactoring-proposal.md",
        "feng-shui-meta-agent-vs-shifu-clarification.md",
    ],
}


def create_backup(dry_run: bool = True):
    """Create backup of knowledge directory"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = REPO_ROOT / "docs" / f"knowledge_backup_{timestamp}"
    
    if dry_run:
        print(f"[DRY RUN] Would create backup at: {backup_dir}")
        return None
    
    shutil.copytree(KNOWLEDGE_DIR, backup_dir)
    print(f"✓ Created backup at: {backup_dir}")
    return backup_dir


def create_category_dirs(dry_run: bool = True):
    """Create category subdirectories"""
    categories = set()
    for category in CATEGORY_MAPPING.keys():
        if category != "quality-ecosystem":  # Already exists
            categories.add(category)
    
    for category in categories:
        target_dir = KNOWLEDGE_DIR / category
        if dry_run:
            print(f"[DRY RUN] Would create directory: {target_dir}")
        else:
            target_dir.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created directory: {target_dir}")


def move_file(source: Path, target: Path, dry_run: bool = True) -> bool:
    """Move a file with safety checks"""
    if not source.exists():
        print(f"✗ Source not found: {source}")
        return False
    
    if dry_run:
        print(f"[DRY RUN] Would move: {source.name} → {target}")
        return True
    
    # Create parent directory if needed
    target.parent.mkdir(parents=True, exist_ok=True)
    
    # Move file
    shutil.move(str(source), str(target))
    print(f"✓ Moved: {source.name} → {target}")
    return True


def update_wikilinks_in_file(file_path: Path, moves: Dict[str, str], dry_run: bool = True):
    """Update [[wikilinks]] in a file to reflect new paths"""
    if not file_path.exists():
        return
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        # Find all wikilinks
        for old_name, new_path in moves.items():
            # Extract just the filename without extension
            old_link = old_name.replace('.md', '')
            new_link = new_path.replace('.md', '')
            
            # Replace wikilinks
            content = re.sub(
                rf'\[\[{re.escape(old_link)}\]\]',
                f'[[{new_link}]]',
                content
            )
        
        if content != original:
            if dry_run:
                print(f"[DRY RUN] Would update wikilinks in: {file_path.name}")
            else:
                file_path.write_text(content, encoding='utf-8')
                print(f"✓ Updated wikilinks in: {file_path.name}")
    except Exception as e:
        print(f"✗ Error updating {file_path}: {e}")


def update_index(moves: Dict[str, str], dry_run: bool = True):
    """Update INDEX.md with new file locations"""
    if not INDEX_FILE.exists():
        print("✗ INDEX.md not found")
        return
    
    try:
        content = INDEX_FILE.read_text(encoding='utf-8')
        original = content
        
        # Update file references
        for old_name, new_path in moves.items():
            # Update markdown links
            old_link = old_name.replace('.md', '')
            new_link = new_path.replace('.md', '')
            
            content = re.sub(
                rf'\[\[{re.escape(old_link)}\]\]',
                f'[[{new_link}]]',
                content
            )
            
            # Update file paths in lists
            content = content.replace(f'- {old_name}', f'- {new_path}')
            content = content.replace(f'* {old_name}', f'* {new_path}')
        
        if content != original:
            if dry_run:
                print(f"[DRY RUN] Would update INDEX.md")
            else:
                INDEX_FILE.write_text(content, encoding='utf-8')
                print(f"✓ Updated INDEX.md")
    except Exception as e:
        print(f"✗ Error updating INDEX.md: {e}")


def execute_refactoring(dry_run: bool = True):
    """Execute the knowledge vault refactoring"""
    print("=" * 70)
    print("Knowledge Vault Refactoring")
    print("=" * 70)
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
    print()
    
    # Step 1: Create backup
    print("Step 1: Creating backup...")
    backup_dir = create_backup(dry_run)
    print()
    
    # Step 2: Create category directories
    print("Step 2: Creating category directories...")
    create_category_dirs(dry_run)
    print()
    
    # Step 3: Move files
    print("Step 3: Moving files...")
    moves = {}  # Track moves for link updates
    
    for category, files in CATEGORY_MAPPING.items():
        print(f"\n{category}:")
        for filename in files:
            source = KNOWLEDGE_DIR / filename
            
            # Handle nested paths (like quality-ecosystem/shi-fu/...)
            if '/' in filename:
                # File already in subdirectory
                target = KNOWLEDGE_DIR / category / Path(filename).name
            else:
                target = KNOWLEDGE_DIR / category / filename
            
            if move_file(source, target, dry_run):
                moves[filename] = f"{category}/{Path(filename).name}"
    
    print()
    
    # Step 4: Update wikilinks in all files
    print("Step 4: Updating wikilinks...")
    if not dry_run:
        for file in KNOWLEDGE_DIR.rglob("*.md"):
            update_wikilinks_in_file(file, moves, dry_run)
    else:
        print(f"[DRY RUN] Would update wikilinks in all .md files")
    print()
    
    # Step 5: Update INDEX.md
    print("Step 5: Updating INDEX.md...")
    update_index(moves, dry_run)
    print()
    
    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Files to move: {sum(len(files) for files in CATEGORY_MAPPING.values())}")
    print(f"Categories: {len(CATEGORY_MAPPING)}")
    if backup_dir:
        print(f"Backup location: {backup_dir}")
    
    if dry_run:
        print("\n⚠️  This was a DRY RUN. No files were moved.")
        print("Run with --execute to perform the actual refactoring.")
    else:
        print("\n✓ Refactoring complete!")


def main():
    parser = argparse.ArgumentParser(
        description="Execute knowledge vault refactoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (default, safe)
  python execute_knowledge_vault_refactoring.py
  
  # Actually execute the refactoring
  python execute_knowledge_vault_refactoring.py --execute
        """
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Actually execute the refactoring (default is dry-run)'
    )
    
    args = parser.parse_args()
    
    # Execute
    execute_refactoring(dry_run=not args.execute)


if __name__ == "__main__":
    main()