"""Analyze docs/knowledge structure and provide consolidation recommendations."""
import os
from collections import defaultdict
from pathlib import Path

def analyze_knowledge_vault():
    """Analyze knowledge vault organization."""
    knowledge_dir = Path('docs/knowledge')
    
    # Get all .md files
    md_files = [f for f in knowledge_dir.glob('*.md')]
    
    print(f"📊 Knowledge Vault Analysis")
    print(f"{'='*60}")
    print(f"Total markdown files: {len(md_files)}\n")
    
    # Categorize by prefix
    categories = defaultdict(list)
    for f in md_files:
        name = f.name
        if '-' in name:
            prefix = name.split('-')[0]
        else:
            prefix = 'other'
        categories[prefix].append(name)
    
    print("📁 Files by prefix:")
    print(f"{'='*60}")
    for prefix, files in sorted(categories.items(), key=lambda x: -len(x[1])):
        print(f"\n{prefix.upper()}: {len(files)} files")
        for f in sorted(files)[:5]:  # Show first 5
            print(f"  - {f}")
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more")
    
    print(f"\n{'='*60}")
    print("\n🎯 Consolidation Opportunities:")
    print(f"{'='*60}")
    
    # AI Assistant docs (many scattered)
    ai_files = [f for f in md_files if 'ai-assistant' in f.name or 'ai-query' in f.name or 'ai-data' in f.name]
    print(f"\n1. AI ASSISTANT ({len(ai_files)} files)")
    print(f"   Could consolidate into: modules/ai_assistant/")
    for f in sorted(ai_files):
        print(f"   - {f.name}")
    
    # Knowledge Graph docs
    kg_files = [f for f in md_files if 'knowledge-graph' in f.name]
    print(f"\n2. KNOWLEDGE GRAPH V2 ({len(kg_files)} files)")
    print(f"   Could consolidate into: modules/knowledge_graph_v2/docs/")
    for f in sorted(kg_files):
        print(f"   - {f.name}")
    
    # HIGH numbered tasks
    high_files = [f for f in md_files if f.name.startswith('high-')]
    print(f"\n3. HIGH TASKS ({len(high_files)} files)")
    print(f"   Could move to: docs/knowledge/tasks/")
    for f in sorted(high_files):
        print(f"   - {f.name}")
    
    # Quality ecosystem
    quality_files = [f for f in md_files if any(x in f.name for x in ['feng-shui', 'guwu', 'shifu', 'quality'])]
    print(f"\n4. QUALITY TOOLS ({len(quality_files)} files)")
    print(f"   Already has subdirectory: docs/knowledge/quality-ecosystem/")
    for f in sorted(quality_files):
        print(f"   - {f.name}")
    
    # Module federation/architecture
    arch_files = [f for f in md_files if any(x in f.name for x in ['module-', 'app-v2', 'frontend-', 'architecture'])]
    print(f"\n5. ARCHITECTURE ({len(arch_files)} files)")
    print(f"   Could consolidate into: docs/knowledge/architecture/")
    for f in sorted(arch_files):
        print(f"   - {f.name}")
    
    # Patterns & best practices
    pattern_files = [f for f in md_files if any(x in f.name for x in ['pattern', 'cosmic', 'ddd', 'repository', 'interface', 'dependency'])]
    print(f"\n6. PATTERNS & BEST PRACTICES ({len(pattern_files)} files)")
    print(f"   Could consolidate into: docs/knowledge/patterns/")
    for f in sorted(pattern_files):
        print(f"   - {f.name}")
    
    # Integration/API docs
    api_files = [f for f in md_files if any(x in f.name for x in ['api-', 'integration', 'sap-', 'pydantic', 'groq', 'litellm'])]
    print(f"\n7. API & INTEGRATION ({len(api_files)} files)")
    print(f"   Could consolidate into: docs/knowledge/integration/")
    for f in sorted(api_files):
        print(f"   - {f.name}")
    
    # Check for potential obsolete files
    print(f"\n{'='*60}")
    print("\n⚠️  Potentially Obsolete Files:")
    print(f"{'='*60}")
    
    # Files with "audit", "analysis", "gap", "proposal" (often superseded)
    obsolete_candidates = [
        f for f in md_files 
        if any(x in f.name for x in ['-audit-', '-analysis', '-gap-', '-proposal', 'reality-check'])
        and not f.name.startswith('INDEX')
    ]
    
    print(f"\n{len(obsolete_candidates)} files that might be obsolete:")
    for f in sorted(obsolete_candidates):
        print(f"   - {f.name}")
    print("\n   Review these - they may have been superseded by implementations")
    
    print(f"\n{'='*60}")
    print("\n✅ Recommended Structure:")
    print(f"{'='*60}")
    print("""
docs/knowledge/
├── INDEX.md                          # Master index
├── README.md                         # Vault guide
│
├── modules/                          # Module-specific docs
│   ├── ai-assistant/                # All AI Assistant docs
│   ├── knowledge-graph-v2/          # All KG V2 docs  
│   ├── data-products-v2/            # Data Products docs
│   └── logger/                      # Logger docs
│
├── architecture/                     # Architecture & design
│   ├── module-federation-standard.md
│   ├── app-v2-architecture.md
│   └── frontend-architecture.md
│
├── patterns/                         # Design patterns
│   ├── cosmic-python-patterns.md
│   ├── repository-pattern.md
│   └── ddd-patterns.md
│
├── integration/                      # External APIs
│   ├── sap-ai-core.md
│   ├── pydantic-ai.md
│   └── hana-integration.md
│
├── quality-ecosystem/                # Already exists!
│   ├── feng-shui/
│   ├── guwu/
│   └── shifu/
│
├── tasks/                            # Active/completed tasks
│   └── high-*.md files
│
└── archive/                          # Historical docs
    └── audits/
    └── proposals/
    """)
    
if __name__ == '__main__':
    analyze_knowledge_vault()