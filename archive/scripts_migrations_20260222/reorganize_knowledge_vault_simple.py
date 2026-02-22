"""
Simple Knowledge Vault Reorganization Script

Reorganizes docs/knowledge/ files into topic-based subdirectories
based on the vault reorganization proposal.

NO dependencies on Feng Shui or Gu Wu - just direct file operations.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List

# Topic-based organization (from vault reorganization proposal)
FILE_MAPPINGS = {
    # Architecture & Patterns
    "architecture": [
        "module-federation-standard.md",
        "module-federation-architecture-proposal.md", 
        "module-federation-formalization-proposal.md",
        "module-isolation-enforcement-standard.md",
        "frontend-modular-architecture-proposal.md",
        "app-v2-modular-architecture-plan.md",
        "app-v2-configuration-driven-architecture.md",
        "repository-pattern-modular-architecture.md",
        "datasource-architecture-refactoring-proposal.md",
        "global-context-state-management-patterns.md",
        "configuration-based-dependency-injection.md",
        "service-locator-antipattern-solution.md",
        "data-products-v2-di-refactoring-proposal.md",
        "interface-segregation-sql-execution-pattern.md",
        "eager-vs-lazy-loading-best-practices.md",
    ],
    
    # AI Assistant
    "ai-assistant": [
        "ai-assistant-implementation-status-2026-02-21.md",
        "ai-assistant-ux-design.md",
        "ai-assistant-ux-gap-analysis.md",
        "ai-assistant-v2-pydantic-implementation.md",
        "ai-assistant-shell-overlay-implementation.md",
        "ai-assistant-phase-2-implementation.md",
        "ai-assistant-phase-3-conversation-enhancement.md",
        "ai-assistant-phase-4-advanced-features.md",
        "ai-assistant-reality-check-2026-02-15.md",
        "ai-assistant-litellm-integration.md",
        "ai-assistant-hana-direct-query-limitations.md",
        "ai-assistant-hana-datasource-solution.md",
        "ai-assistant-hana-datasource-issue.md",
        "ai-assistant-hana-fix-summary.md",
        "ai-assistant-hana-table-name-fix.md",
        "ai-assistant-database-abstraction-analysis.md",
        "ai-assistant-repository-pattern-implementation-guide.md",
        "ai-assistant-module-isolation-audit.md",
        "ai-assistant-sql-service-hana-issue.md",
    ],
    
    # Knowledge Graph
    "knowledge-graph": [
        "knowledge-graph-v2-architecture-proposal.md",
        "knowledge-graph-v2-api-design.md",
        "knowledge-graph-v2-services-design.md",
        "knowledge-graph-v2-phase-2-complete.md",
        "knowledge-graph-v2-phase-5-frontend-architecture.md",
        "knowledge-graph-v2-feng-shui-audit-2026-02-21.md",
        "knowledge-graph-cache-debugging-lessons.md",
        "knowledge-graph-csn-semantic-completeness-analysis.md",
        "knowledge-graph-semantic-enhancement-implementation-plan.md",
        "knowledge-graph-ai-assistant-requirements.md",
        "knowledge-graph-10k-benchmark-results.md",
    ],
    
    # Testing & Quality
    "testing": [
        "guwu-api-contract-testing-foundation.md",
        "api-first-contract-testing-methodology.md",
        "guwu-workflow-for-ai-assistant.md",
        "frontend-api-testing-breakthrough.md",
        "ux-api-test-coverage-audit.md",
        "guwu-resolver-expansion-2026-02-22.md",
        "guwu-refactoring-assessment-med-25.md",
        "feng-shui-guwu-integration-bridge.md",
        "feng-shui-guwu-e2e-integration-tests.md",
    ],
    
    # Feng Shui
    "feng-shui": [
        "feng-shui-architecture-audit-2026-02-15.md",
        "feng-shui-guwu-workflow-guide.md",
        "feng-shui-meta-agent-vs-shifu-clarification.md",
        "feng-shui-preview-mode-design.md",
        "feng-shui-preview-mode-validation-results.md",
        "feng-shui-preview-mode-user-guide.md",
    ],
    
    # Implementation Tasks
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
    
    # Technical References
    "technical-references": [
        "groq-api-reference.md",
        "groq-documentation-overview.md",
        "pydantic-ai-framework.md",
        "pydantic-ai-sap-ai-core-integration.md",
        "sap-ai-core-pydantic-ai-integration.md",
        "sap-fiori-color-integration.md",
        "visjs-library-reference.md",
        "chat-ui-sticky-input-best-practices.md",
        "cosmic-python-patterns.md",
        "ddd-patterns-quality-ecosystem-integration.md",
    ],
    
    # Project Management
    "project-management": [
        "spa-module-lifecycle-analysis.md",
        "module-categorization-analysis.md",
        "p2p-dashboard-design.md",
        "p2p-database-creation-workflow.md",
        "ai-data-query-architecture-gap-analysis.md",
        "ai-query-system-implementation-proposal.md",
        "app-v2-validator-refactoring-proposal.md",
        "logger-to-log-module-rename.md",
        "log-viewer-overlay-implementation.md",
        "dual-mode-logging-system.md",
        "vault-reorganization-proposal-2026-02-22.md",
        "VAULT_CLEANUP_AUDIT_2026-02-15.md",
        "QUALITY_DOCS_CONSOLIDATION_PROPOSAL.md",
    ],
    
    # Security
    "security": [
        "security-sql-injection-verification-2026-02-21.md",
    ],
    
    # Encoding Standards
    "standards": [
        "windows-encoding-standard.md",
    ],
}


def reorganize_vault(dry_run: bool = True) -> Dict[str, List[str]]:
    """
    Reorganize knowledge vault files into topic subdirectories.
    
    Args:
        dry_run: If True, only print what would be done
        
    Returns:
        Dict of actions taken by category
    """
    vault_path = Path("docs/knowledge")
    actions = {
        "moved": [],
        "skipped": [],
        "errors": [],
    }
    
    print(f"\n{'='*60}")
    print(f"Knowledge Vault Reorganization")
    print(f"Mode: {'DRY-RUN (simulation)' if dry_run else 'EXECUTE (real changes)'}")
    print(f"{'='*60}\n")
    
    # Process each topic category
    for topic, files in FILE_MAPPINGS.items():
        topic_dir = vault_path / topic
        
        print(f"\n📁 Topic: {topic}")
        print(f"   Target: {topic_dir}")
        
        # Create topic directory
        if not dry_run:
            topic_dir.mkdir(exist_ok=True)
            print(f"   ✓ Created directory")
        else:
            print(f"   ⚡ WOULD create directory")
        
        # Move files
        for filename in files:
            source = vault_path / filename
            target = topic_dir / filename
            
            if not source.exists():
                msg = f"   ⚠️  Source not found: {filename}"
                print(msg)
                actions["skipped"].append(filename)
                continue
            
            if target.exists():
                msg = f"   ⚠️  Target exists: {filename}"
                print(msg)
                actions["skipped"].append(filename)
                continue
            
            try:
                if not dry_run:
                    shutil.move(str(source), str(target))
                    msg = f"   ✓ Moved: {filename}"
                    print(msg)
                    actions["moved"].append(f"{filename} → {topic}/")
                else:
                    msg = f"   ⚡ WOULD move: {filename}"
                    print(msg)
                    actions["moved"].append(f"{filename} → {topic}/")
            
            except Exception as e:
                msg = f"   ❌ Error moving {filename}: {e}"
                print(msg)
                actions["errors"].append(f"{filename}: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Moved: {len(actions['moved'])} files")
    print(f"  Skipped: {len(actions['skipped'])} files")
    print(f"  Errors: {len(actions['errors'])} errors")
    print(f"{'='*60}\n")
    
    return actions


if __name__ == "__main__":
    import sys
    
    # Check for --execute flag
    execute = "--execute" in sys.argv
    
    if not execute:
        print("🔍 DRY-RUN MODE - No files will be changed")
        print("   To execute: python scripts/python/reorganize_knowledge_vault_simple.py --execute\n")
    else:
        print("⚠️  EXECUTE MODE - Files will be moved!")
        response = input("   Continue? (yes/no): ")
        if response.lower() != "yes":
            print("   Cancelled.")
            sys.exit(0)
    
    actions = reorganize_vault(dry_run=not execute)
    
    if not execute:
        print("\n✅ Dry-run complete. Review the output above.")
        print("   To execute: python scripts/python/reorganize_knowledge_vault_simple.py --execute")