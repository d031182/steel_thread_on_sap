"""
Execute Knowledge Vault Refactoring via Gu Wu Resolver

Bridges Feng Shui file organization findings to Gu Wu's FileOrganizationResolver
for automated execution.

Usage:
    # Dry-run (safe, shows what would happen)
    python scripts/python/execute_vault_refactoring_guwu.py
    
    # Execute (actually performs file moves)
    python scripts/python/execute_vault_refactoring_guwu.py --apply
"""

import sys
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.guwu.resolvers import get_registry
from tools.guwu.adapters.feng_shui_adapter import FengShuiAdapter


@dataclass
class Finding:
    """Simplified Finding structure matching Feng Shui output"""
    file_path: str
    category: str
    severity: str
    issue: str
    recommendation: str
    agent: str = "file_organization"


def load_vault_findings() -> List[Finding]:
    """
    Load knowledge vault refactoring findings from analysis
    
    Returns:
        List of Finding objects for vault refactoring
    """
    # Based on vault-reorganization-proposal-2026-02-22.md
    findings = [
        Finding(
            file_path="docs/knowledge/ai-assistant-ux-design.md",
            category="Knowledge Vault Structure Violation",
            severity="MEDIUM",
            issue="AI Assistant documentation not in modules/ subdirectory",
            recommendation="MOVE to docs/knowledge/modules/ai-assistant-ux-design.md"
        ),
        Finding(
            file_path="docs/knowledge/ai-assistant-ux-gap-analysis.md",
            category="Knowledge Vault Structure Violation",
            severity="MEDIUM",
            issue="AI Assistant documentation not in modules/ subdirectory",
            recommendation="MOVE to docs/knowledge/modules/ai-assistant-ux-gap-analysis.md"
        ),
        Finding(
            file_path="docs/knowledge/spa-module-lifecycle-analysis.md",
            category="Knowledge Vault Structure Violation",
            severity="MEDIUM",
            issue="Architecture documentation not in architecture/ subdirectory",
            recommendation="MOVE to docs/knowledge/architecture/spa-module-lifecycle-analysis.md"
        ),
        Finding(
            file_path="docs/knowledge/high-19-endpoint-analysis.md",
            category="Knowledge Vault Structure Violation",
            severity="LOW",
            issue="High-priority task in root, should be in implementations/",
            recommendation="MOVE to docs/knowledge/implementations/high-19-endpoint-analysis.md"
        ),
        Finding(
            file_path="docs/knowledge/api-first-contract-testing-methodology.md",
            category="Knowledge Vault Structure Violation",
            severity="MEDIUM",
            issue="Testing methodology not in quality-ecosystem/ subdirectory",
            recommendation="MOVE to docs/knowledge/quality-ecosystem/api-first-contract-testing-methodology.md"
        ),
        Finding(
            file_path="docs/knowledge/knowledge-graph-10k-benchmark-results.md",
            category="Knowledge Vault Structure Violation",
            severity="MEDIUM",
            issue="Module documentation not in modules/ subdirectory",
            recommendation="MOVE to docs/knowledge/modules/knowledge-graph-10k-benchmark-results.md"
        ),
        Finding(
            file_path="docs/knowledge/ai-assistant-v2-pydantic-implementation.md",
            category="Knowledge Vault Structure Violation",
            severity="MEDIUM",
            issue="AI Assistant documentation not in modules/ subdirectory",
            recommendation="MOVE to docs/knowledge/modules/ai-assistant-v2-pydantic-implementation.md"
        ),
        Finding(
            file_path="docs/knowledge/ai-assistant-shell-overlay-implementation.md",
            category="Knowledge Vault Structure Violation",
            severity="MEDIUM",
            issue="AI Assistant documentation not in modules/ subdirectory",
            recommendation="MOVE to docs/knowledge/modules/ai-assistant-shell-overlay-implementation.md"
        ),
        Finding(
            file_path="docs/knowledge/ai-assistant-phase-2-implementation.md",
            category="Knowledge Vault Structure Violation",
            severity="MEDIUM",
            issue="AI Assistant documentation not in modules/ subdirectory",
            recommendation="MOVE to docs/knowledge/modules/ai-assistant-phase-2-implementation.md"
        ),
        Finding(
            file_path="docs/knowledge/ai-assistant-phase-3-conversation-enhancement.md",
            category="Knowledge Vault Structure Violation",
            severity="MEDIUM",
            issue="AI Assistant documentation not in modules/ subdirectory",
            recommendation="MOVE to docs/knowledge/modules/ai-assistant-phase-3-conversation-enhancement.md"
        ),
        Finding(
            file_path="docs/knowledge/ai-assistant-phase-4-advanced-features.md",
            category="Knowledge Vault Structure Violation",
            severity="MEDIUM",
            issue="AI Assistant documentation not in modules/ subdirectory",
            recommendation="MOVE to docs/knowledge/modules/ai-assistant-phase-4-advanced-features.md"
        ),
        Finding(
            file_path="docs/knowledge/sap-fiori-color-integration.md",
            category="Knowledge Vault Structure Violation",
            severity="MEDIUM",
            issue="Architecture documentation not in architecture/ subdirectory",
            recommendation="MOVE to docs/knowledge/architecture/sap-fiori-color-integration.md"
        ),
        Finding(
            file_path="docs/knowledge/visjs-library-reference.md",
            category="Knowledge Vault Structure Violation",
            severity="LOW",
            issue="Third-party library reference should be in references/",
            recommendation="MOVE to docs/knowledge/references/visjs-library-reference.md"
        ),
        Finding(
            file_path="docs/knowledge/ai-assistant-reality-check-2026-02-15.md",
            category="Knowledge Vault Structure Violation",
            severity="MEDIUM",
            issue="AI Assistant documentation not in modules/ subdirectory",
            recommendation="MOVE to docs/knowledge/modules/ai-assistant-reality-check-2026-02-15.md"
        ),
        Finding(
            file_path="docs/knowledge/ai-assistant-litellm-integration.md",
            category="Knowledge Vault Structure Violation",
            severity="MEDIUM",
            issue="AI Assistant documentation not in modules/ subdirectory",
            recommendation="MOVE to docs/knowledge/modules/ai-assistant-litellm-integration.md"
        ),
    ]
    
    return findings


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Execute vault refactoring via Gu Wu")
    parser.add_argument('--apply', action='store_true', 
                       help='Apply changes (default: dry-run)')
    args = parser.parse_args()
    
    # Determine mode
    dry_run = not args.apply
    
    print("=" * 70)
    print("  Knowledge Vault Refactoring - Gu Wu Resolver")
    print("=" * 70)
    print()
    
    if dry_run:
        print("🔍 DRY-RUN MODE - No files will be moved")
    else:
        print("⚠️  APPLY MODE - Files will be moved to new locations")
    print()
    
    # Load findings
    print("📋 Loading vault refactoring findings...")
    findings = load_vault_findings()
    print(f"   Found {len(findings)} files to reorganize")
    print()
    
    # Get resolver registry
    print("🔧 Initializing Gu Wu resolver...")
    registry = get_registry()
    
    # Show available resolvers
    capabilities = registry.get_capabilities()
    print(f"   Available resolvers: {len(capabilities)}")
    for resolver_name, caps in capabilities.items():
        print(f"     • {resolver_name}: {len(caps)} capabilities")
    print()
    
    # Group findings by category
    from collections import defaultdict
    findings_by_category = defaultdict(list)
    for finding in findings:
        findings_by_category[finding.category].append(finding)
    
    print(f"📋 Findings grouped into {len(findings_by_category)} categories:")
    for category, cat_findings in findings_by_category.items():
        print(f"   • {category}: {len(cat_findings)} findings")
    print()
    
    # Process each category
    print(f"🚀 Processing findings...")
    print()
    
    all_results = []
    total_resolved = 0
    total_failed = 0
    total_skipped = 0
    
    for category, cat_findings in findings_by_category.items():
        print(f"Processing category: {category}")
        result = registry.resolve_findings(cat_findings, category, dry_run=dry_run)
        all_results.append((category, result))
        
        total_resolved += result.findings_resolved
        total_failed += result.findings_failed
        total_skipped += result.findings_skipped
        print()
    
    # Aggregate results
    from tools.guwu.resolvers.base_resolver import ResolutionResult, ResolutionStatus
    result = ResolutionResult(
        status=ResolutionStatus.SUCCESS if total_failed == 0 else ResolutionStatus.PARTIAL
    )
    result.findings_resolved = total_resolved
    result.findings_failed = total_failed
    result.findings_skipped = total_skipped
    
    # Collect all actions (use correct attribute names)
    for category, cat_result in all_results:
        result.actions_taken.extend(cat_result.actions_taken)
        result.dry_run_actions.extend(cat_result.dry_run_actions)
        result.warnings.extend(cat_result.warnings)
        result.errors.extend(cat_result.errors)
    
    # Display results
    print()
    print("=" * 70)
    print("  RESULTS")
    print("=" * 70)
    print()
    print(f"Status: {result.status.value}")
    print(f"Findings Resolved: {result.findings_resolved}")
    print(f"Findings Failed: {result.findings_failed}")
    print(f"Findings Skipped: {result.findings_skipped}")
    print()
    
    if result.actions_taken:
        print("✅ Actions Taken:")
        for action in result.actions_taken:
            print(f"   {action}")
        print()
    
    if result.dry_run_actions:
        print("🔍 Would Perform (Dry-Run):")
        for action in result.dry_run_actions:
            print(f"   {action}")
        print()
    
    if result.warnings:
        print("⚠️  Warnings:")
        for warning in result.warnings:
            print(f"   {warning}")
        print()
    
    if result.errors:
        print("❌ Errors:")
        for error in result.errors:
            print(f"   {error}")
        print()
    
    # Summary
    print("=" * 70)
    if dry_run:
        print("💡 To execute these changes, run with --apply flag:")
        print("   python scripts/python/execute_vault_refactoring_guwu.py --apply")
    else:
        print("✅ Knowledge vault refactoring complete!")
        print("   Files have been reorganized into proper subdirectories")
        print()
        print("📝 Next Steps:")
        print("   1. Update INDEX.md to reflect new locations")
        print("   2. Update [[wikilinks]] in moved files")
        print("   3. Verify all cross-references still work")
    print("=" * 70)


if __name__ == "__main__":
    main()