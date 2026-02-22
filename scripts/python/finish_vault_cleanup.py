"""
Finish Knowledge Vault Cleanup
================================

Move remaining orphaned files from docs/knowledge/ root to proper categories.
"""

import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
KNOWLEDGE_DIR = REPO_ROOT / "docs" / "knowledge"

# Remaining files and their destinations
MOVES = {
    "debugging-strategy.md": "guidelines/debugging-strategy.md",
    "HANA_CSN_COMPLIANCE_REPORT.md": "archive/HANA_CSN_COMPLIANCE_REPORT.md",
    "high-40-color-contrast-report.json": "implementation-tasks/high-40-color-contrast-report.json",
    "log-integration-proposal.md": "archive/log-integration-proposal.md",
}

def main():
    print("=" * 70)
    print("Finish Knowledge Vault Cleanup")
    print("=" * 70)
    
    moved = 0
    for source_name, target_path in MOVES.items():
        source = KNOWLEDGE_DIR / source_name
        target = KNOWLEDGE_DIR / target_path
        
        if source.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(target))
            print(f"✓ Moved: {source_name} → {target_path}")
            moved += 1
        else:
            print(f"✗ Not found: {source_name}")
    
    print("\n" + "=" * 70)
    print(f"Summary: {moved} files moved")
    print("=" * 70)
    print("\nKnowledge vault cleanup complete!")
    print("\nNext steps:")
    print("1. Review: git status")
    print("2. Run Feng Shui: python -m tools.fengshui analyze")
    print("3. Commit: git add . && git commit -m 'docs: finish knowledge vault cleanup'")

if __name__ == "__main__":
    main()