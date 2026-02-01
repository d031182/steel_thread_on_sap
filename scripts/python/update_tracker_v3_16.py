"""Update PROJECT_TRACKER.md for v3.16 release"""

def update_tracker():
    filepath = 'PROJECT_TRACKER.md'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update current version
    content = content.replace(
        '**Current**: v3.14-clean-graph-cache (Feb 1, 2026)',
        '**Current**: v3.16-kg-di-refactoring (Feb 1, 2026)'
    )
    
    # Update current work status
    content = content.replace(
        '- [ ] **WP-KG-002**: Refactor DataGraphService per Separation of Concerns (3-4 hours)',
        '- [x] **WP-KG-002**: Refactor DataGraphService per Separation of Concerns (COMPLETE)'
    )
    
    content = content.replace(
        '**Current Focus**: Architecture improvement (SoC refactoring + CSN-driven architecture) -> Production readiness',
        '**Current Focus**: WP-KG-002 complete with 100% DRY compliance + better naming -> Production readiness'
    )
    
    # Add archive link (insert after v3.3 line)
    old_archive = """- [v3.3 (Jan 31)](docs/archive/TRACKER-v3.3-2026-01-31.md) - Knowledge Graph Visualization

**See**: [docs/archive/ARCHIVE_STRATEGY.md]"""
    
    new_archive = """- [v3.3 (Jan 31)](docs/archive/TRACKER-v3.3-2026-01-31.md) - Knowledge Graph Visualization
- [v3.14-v3.15 (Feb 1)](docs/archive/TRACKER-v3.14-v3.15-2026-02-01.md) - Graph Cache + Feng Shui

**See**: [docs/archive/ARCHIVE_STRATEGY.md]"""
    
    content = content.replace(old_archive, new_archive)
    
    # Add new tag
    old_tags = """- `v3.11` (Jan 31, 9:48 PM) - Knowledge Graph Cache Management (103x speedup) <- **CURRENT**"""
    
    new_tags = """- `v3.11` (Jan 31, 9:48 PM) - Knowledge Graph Cache Management (103x speedup)
- `v3.14` (Feb 1, 2:05 PM) - Clean Graph Cache Architecture (59.9x speedup)
- `v3.15` (Feb 1, 3:29 PM) - Feng Shui Self-Healing System
- `v3.16` (Feb 1, 5:20 PM) - Knowledge Graph DRY Refactoring (100% compliance) <- **CURRENT**"""
    
    content = content.replace(old_tags, new_tags)
    
    # Update last updated time
    content = content.replace(
        '**Last Updated**: February 1, 2026, 4:19 PM',
        '**Last Updated**: February 1, 2026, 5:20 PM'
    )
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("[OK] Updated PROJECT_TRACKER.md for v3.16")
    print("     - Current version: v3.16-kg-di-refactoring")
    print("     - WP-KG-002 marked complete")
    print("     - Added archive link for v3.14-v3.15")
    print("     - Added tag entry for v3.16")

if __name__ == '__main__':
    update_tracker()