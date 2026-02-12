#!/usr/bin/env python3
"""
Quality Documentation Consolidation Script

Consolidates scattered Feng Shui, Gu Wu, and Shi Fu documentation
into organized quality-ecosystem structure.

Based on: docs/knowledge/QUALITY_DOCS_CONSOLIDATION_PROPOSAL.md
"""

import shutil
from pathlib import Path
from typing import List, Dict, Tuple

# Base paths
DOCS_ROOT = Path("docs/knowledge")
QUALITY_ROOT = DOCS_ROOT / "quality-ecosystem"
ARCHIVE_ROOT = DOCS_ROOT / "archive"

# Document mappings: (source, destination, action)
# Actions: 'move', 'copy', 'merge', 'archive'

FENG_SHUI_DOCS = [
    # Architecture documents
    ("architecture/feng-shui-phase4-17-complete.md", "feng-shui/architecture.md", "move"),
    ("architecture/feng-shui-phase4-17-checkpoint.md", "../archive/implementations/feng-shui-phase4-17-checkpoint.md", "archive"),
    ("architecture/feng-shui-phase4-15-implementation-plan.md", "../archive/implementations/feng-shui-phase4-15-implementation-plan.md", "archive"),
    ("architecture/feng-shui-phase4-16-implementation-plan.md", "../archive/implementations/feng-shui-phase4-16-implementation-plan.md", "archive"),
    
    # Guidelines
    ("guidelines/feng-shui-false-positives.md", "feng-shui/false-positives-guide.md", "move"),
    ("guidelines/feng-shui-separation-of-concerns.md", "feng-shui/separation-of-concerns.md", "move"),
    
    # Clarification docs (keep at root level for visibility)
    ("feng-shui-meta-agent-vs-shifu-clarification.md", "feng-shui-meta-agent-vs-shifu-clarification.md", "keep"),
    
    # Code review
    ("fengshui-code-review-agent.md", "feng-shui/code-review-agent.md", "move"),
    
    # Proposals (archive)
    ("feng-shui-enhancement-plan-v4.12.md", "../archive/proposals/feng-shui-enhancement-plan-v4.12.md", "archive"),
]

GU_WU_DOCS = [
    # Architecture documents
    ("architecture/guwu-phase4-complete.md", "gu-wu/architecture.md", "move"),
    ("architecture/guwu-phase4-pattern-integration.md", "../archive/implementations/guwu-phase4-pattern-integration.md", "archive"),
    
    # Guidelines
    ("guidelines/guwu-lessons-learned-2026-02-05.md", "gu-wu/lessons-learned.md", "move"),
    ("guidelines/guwu-framework-audit-2026-02-05.md", "gu-wu/framework-audit.md", "move"),
    ("guidelines/gu-wu-testing-enforcement-audit.md", "gu-wu/testing-enforcement-audit.md", "move"),
    
    # Proposals (archive)
    ("guwu-phase-8-architecture-aware-e2e-testing.md", "../archive/proposals/guwu-phase-8-architecture-aware-e2e-testing.md", "archive"),
    ("guwu-frontend-testing-proposal.md", "../archive/proposals/guwu-frontend-testing-proposal.md", "archive"),
]

SHI_FU_DOCS = [
    # Main documentation
    ("shifu-meta-architecture-intelligence.md", "shi-fu/meta-architecture.md", "move"),
]

INTEGRATION_DOCS = [
    # Pre-commit (will need merging)
    ("fengshui-precommit-hook-documentation.md", "integration/pre-commit-hooks.md", "move"),
    ("fengshui-guwu-precommit-integration.md", "integration/pre-commit-integration-details.md", "move"),
    
    # Quality gates
    ("three-tier-quality-gate-system.md", "integration/quality-gates.md", "move"),
    
    # Future integration
    ("guwu-fengshui-future-integration.md", "integration/future-roadmap.md", "move"),
    ("feng-shui-guwu-integration-plan.md", "integration/integration-plan.md", "move"),
    ("autonomous-testing-debugging-architecture.md", "integration/autonomous-testing-debugging.md", "move"),
]


def ensure_directories():
    """Create all necessary directories"""
    dirs = [
        QUALITY_ROOT / "feng-shui",
        QUALITY_ROOT / "gu-wu",
        QUALITY_ROOT / "shi-fu",
        QUALITY_ROOT / "integration",
        ARCHIVE_ROOT / "implementations",
        ARCHIVE_ROOT / "proposals",
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Ensured directory: {dir_path}")


def move_document(source: Path, dest: Path, action: str) -> Tuple[bool, str]:
    """Move a document from source to destination"""
    if not source.exists():
        return False, f"Source not found: {source}"
    
    if action == "keep":
        return True, f"Kept in place: {source}"
    
    # Create destination directory if needed
    dest.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        if action == "move" or action == "archive":
            shutil.move(str(source), str(dest))
            return True, f"Moved: {source} → {dest}"
        elif action == "copy":
            shutil.copy2(str(source), str(dest))
            return True, f"Copied: {source} → {dest}"
        else:
            return False, f"Unknown action: {action}"
    except Exception as e:
        return False, f"Error moving {source}: {e}"


def process_document_list(doc_list: List[Tuple[str, str, str]], category: str):
    """Process a list of documents for a category"""
    print(f"\n{'='*60}")
    print(f"Processing {category} documents...")
    print(f"{'='*60}")
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for source_rel, dest_rel, action in doc_list:
        source = DOCS_ROOT / source_rel
        
        # Determine destination based on action
        if action == "archive":
            dest = DOCS_ROOT / dest_rel
        elif action == "keep":
            dest = source  # Don't move
        else:
            dest = QUALITY_ROOT / dest_rel
        
        success, message = move_document(source, dest, action)
        
        if success:
            print(f"✓ {message}")
            success_count += 1
        elif "not found" in message:
            print(f"⊘ {message}")
            skip_count += 1
        else:
            print(f"✗ {message}")
            error_count += 1
    
    print(f"\n{category} Summary: {success_count} moved, {skip_count} skipped, {error_count} errors")
    return success_count, skip_count, error_count


def create_subdirectory_readmes():
    """Create README files for each subdirectory"""
    
    # Feng Shui README
    feng_shui_readme = QUALITY_ROOT / "feng-shui" / "README.md"
    feng_shui_content = """# Feng Shui (风水) Documentation

**"Wind and Water" - Creating harmonious flow in code architecture**

## 📖 Overview

Feng Shui is our code quality and architecture analysis tool featuring:
- 6 specialized AI agents (parallel execution)
- ReAct autonomous agent for batch fixes
- 22-check quality gate system
- Multi-agent orchestration with conflict detection

## 🚀 Quick Start

See the comprehensive CLI guide: [tools/fengshui/README.md](../../../tools/fengshui/README.md)

```bash
# Multi-agent analysis
python -m tools.fengshui analyze

# Quality gate check
python -m tools.fengshui gate --module my_module

# Autonomous batch fixes
python -m tools.fengshui fix
```

## 📚 Documentation

### Architecture
- **[Architecture](architecture.md)** - Multi-agent system (Phase 4-17 complete)
- **[Separation of Concerns](separation-of-concerns.md)** - Design principles

### Guides
- **[False Positives Guide](false-positives-guide.md)** - Tuning and customization
- **[Code Review Agent](code-review-agent.md)** - Automated code review features

### Integration
- **[Pre-Commit Hooks](../integration/pre-commit-hooks.md)** - Git hook setup
- **[Quality Gates](../integration/quality-gates.md)** - Three-tier gate system

## 🔗 Related Documentation

- [Quality Ecosystem Vision](../quality-ecosystem-vision.md) - Overall philosophy
- [Gu Wu Documentation](../gu-wu/) - Test quality
- [Shi Fu Documentation](../shi-fu/) - Ecosystem orchestration

---

**Navigation**: [← Back to Quality Ecosystem](../README.md)
"""
    
    # Gu Wu README
    gu_wu_readme = QUALITY_ROOT / "gu-wu" / "README.md"
    gu_wu_content = """# Gu Wu (顾武) Documentation

**"Attending to Martial Affairs" - Testing with discipline and continuous improvement**

## 📖 Overview

Gu Wu is our test quality and intelligence framework featuring:
- Intelligence Hub (3 engines: Recommendations, Dashboard, Predictive)
- Test pyramid enforcement (70% unit / 20% integration / 10% E2E)
- ML-powered failure prediction
- Flaky test detection and auto-prioritization

## 🚀 Quick Start

See the comprehensive CLI guide: [tools/guwu/README.md](../../../tools/guwu/README.md)

```bash
# Run tests with optimization
python -m tools.guwu run

# Intelligence Hub (all 3 engines)
python -m tools.guwu intelligence

# Get recommendations
python -m tools.guwu recommend
```

## 📚 Documentation

### Architecture
- **[Architecture](architecture.md)** - Phase 7 intelligence hub complete

### Guides
- **[Testing Enforcement](testing-enforcement-audit.md)** - Enforcement guidelines
- **[Framework Audit](framework-audit.md)** - Framework health check
- **[Lessons Learned](lessons-learned.md)** - Historical insights

### Integration
- **[Pre-Commit Hooks](../integration/pre-commit-hooks.md)** - Git hook setup
- **[Feng Shui Integration](../integration/integration-plan.md)** - Cross-tool workflow

## 🔗 Related Documentation

- [Quality Ecosystem Vision](../quality-ecosystem-vision.md) - Overall philosophy
- [Feng Shui Documentation](../feng-shui/) - Code quality
- [Shi Fu Documentation](../shi-fu/) - Ecosystem orchestration

---

**Navigation**: [← Back to Quality Ecosystem](../README.md)
"""
    
    # Shi Fu README
    shi_fu_readme = QUALITY_ROOT / "shi-fu" / "README.md"
    shi_fu_content = """# Shi Fu (师傅) Documentation

**"The Master Teacher" - Code and tests are yin and yang**

## 📖 Overview

Shi Fu is our ecosystem orchestrator and meta-intelligence tool featuring:
- 5 correlation pattern detectors
- Cross-domain intelligence (code + tests + runtime)
- Priority-based teachings with root cause analysis
- Auto PROJECT_TRACKER.md updates

## 🚀 Quick Start

See the comprehensive CLI guide: [tools/shifu/README.md](../../../tools/shifu/README.md)

```bash
# Session start (auto weekly analysis)
python -m tools.shifu --session-start

# Manual weekly analysis
python -m tools.shifu --weekly-analysis

# Quick health check
python -m tools.shifu --health-check
```

## 📚 Documentation

### Architecture
- **[Meta-Architecture](meta-architecture.md)** - Observer design and intelligence

### Patterns
Shi Fu detects 5 cross-domain correlation patterns:
1. **DI Violations → Flaky Tests** (URGENT/HIGH)
2. **High Complexity → Low Coverage** (HIGH)
3. **Security Issues → Test Gaps** (URGENT)
4. **Performance Issues → Slow Tests** (MEDIUM)
5. **Module Health → Test Health** (HIGH)

### Integration
- **[Cline Integration](../integration/cline-integration.md)** - AI assistant workflow
- **[Weekly Analysis](../quality-ecosystem-vision.md#weekly-workflow)** - Routine usage

## 🔗 Related Documentation

- [Quality Ecosystem Vision](../quality-ecosystem-vision.md) - Overall philosophy
- [Feng Shui Documentation](../feng-shui/) - Code quality (observed by Shi Fu)
- [Gu Wu Documentation](../gu-wu/) - Test quality (observed by Shi Fu)

---

**Navigation**: [← Back to Quality Ecosystem](../README.md)
"""
    
    # Integration README
    integration_readme = QUALITY_ROOT / "integration" / "README.md"
    integration_content = """# Quality Ecosystem Integration Documentation

**Cross-tool integration guides and workflows**

## 📖 Overview

This directory contains documentation for integrating Feng Shui, Gu Wu, and Shi Fu:
- Git hook integrations (pre-commit, pre-push)
- Quality gate systems
- Future roadmap and enhancement plans
- Workflow automation

## 📚 Documentation

### Git Hooks
- **[Pre-Commit Hooks](pre-commit-hooks.md)** - Fast quality checks (< 2s)
- **[Pre-Commit Integration Details](pre-commit-integration-details.md)** - Technical implementation

### Quality Gates
- **[Quality Gates](quality-gates.md)** - Three-tier gate system

### Integration Plans
- **[Integration Plan](integration-plan.md)** - Cross-tool workflow
- **[Future Roadmap](future-roadmap.md)** - Gu Wu as 7th Feng Shui agent
- **[Autonomous Testing](autonomous-testing-debugging.md)** - Automated debugging

## 🚀 Quick Integration Workflows

### Daily Development
```bash
# 1. Session start (Shi Fu checks ecosystem)
python -m tools.shifu --session-start

# 2. Make changes, analyze
python -m tools.fengshui analyze --module my_module

# 3. Run tests
python -m tools.guwu run

# 4. Commit (hooks run automatically)
git commit -m "Your changes"
```

### Pre-Deployment
```bash
# Quality gate validation
python -m tools.fengshui gate --module my_module

# Pre-flight test check
python -m tools.guwu predict --pre-flight

# Ecosystem health
python -m tools.shifu --health-check
```

## 🔗 Related Documentation

- [Quality Ecosystem Vision](../quality-ecosystem-vision.md) - Overall philosophy
- [Feng Shui CLI](../../../tools/fengshui/README.md)
- [Gu Wu CLI](../../../tools/guwu/README.md)
- [Shi Fu CLI](../../../tools/shifu/README.md)

---

**Navigation**: [← Back to Quality Ecosystem](../README.md)
"""
    
    # Write all READMEs
    readmes = [
        (feng_shui_readme, feng_shui_content),
        (gu_wu_readme, gu_wu_content),
        (shi_fu_readme, shi_fu_content),
        (integration_readme, integration_content),
    ]
    
    print(f"\n{'='*60}")
    print("Creating subdirectory README files...")
    print(f"{'='*60}")
    
    for readme_path, content in readmes:
        readme_path.write_text(content, encoding='utf-8')
        print(f"✓ Created: {readme_path}")


def main():
    """Main consolidation workflow"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║   Quality Documentation Consolidation                        ║
║   Feng Shui (风水) + Gu Wu (顾武) + Shi Fu (师傅)             ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    # Step 1: Ensure directories exist
    ensure_directories()
    
    # Step 2: Process each category
    total_success = 0
    total_skip = 0
    total_error = 0
    
    for doc_list, category in [
        (FENG_SHUI_DOCS, "Feng Shui"),
        (GU_WU_DOCS, "Gu Wu"),
        (SHI_FU_DOCS, "Shi Fu"),
        (INTEGRATION_DOCS, "Integration"),
    ]:
        success, skip, error = process_document_list(doc_list, category)
        total_success += success
        total_skip += skip
        total_error += error
    
    # Step 3: Create subdirectory READMEs
    create_subdirectory_readmes()
    
    # Final summary
    print(f"\n{'='*60}")
    print("CONSOLIDATION COMPLETE")
    print(f"{'='*60}")
    print(f"✓ Total documents processed: {total_success}")
    print(f"⊘ Documents skipped (not found): {total_skip}")
    print(f"✗ Errors: {total_error}")
    print()
    print("Next steps:")
    print("1. Review moved documents in docs/knowledge/quality-ecosystem/")
    print("2. Update cross-references in documents")
    print("3. Update docs/knowledge/INDEX.md")
    print("4. Test all links")
    print("5. Commit changes")


if __name__ == "__main__":
    main()