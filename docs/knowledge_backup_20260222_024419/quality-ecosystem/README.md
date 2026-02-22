# Quality Ecosystem Documentation

**Central hub for Feng Shui, Gu Wu, and Shi Fu documentation**

---

## 🚀 Quick Start (New Users Start Here!)

### Tool READMEs (Comprehensive CLI Guides)
1. **[Feng Shui CLI Guide](../../../tools/fengshui/README.md)** - Code quality & architecture analysis
2. **[Gu Wu CLI Guide](../../../tools/guwu/README.md)** - Test quality & intelligence
3. **[Shi Fu CLI Guide](../../../tools/shifu/README.md)** - Ecosystem orchestration

### Quick Commands
```bash
# Feng Shui: Architecture analysis
python -m tools.fengshui analyze

# Gu Wu: Test intelligence
python -m tools.guwu intelligence

# Shi Fu: Ecosystem health
python -m tools.shifu --session-start
```

---

## 📖 Understanding the Ecosystem

### Core Philosophy
- **[Quality Ecosystem Vision](quality-ecosystem-vision.md)** ⭐ START HERE
  - The three pillars (Feng Shui, Gu Wu, Shi Fu)
  - Self-learning mechanisms
  - Collaboration patterns
  - Philosophy & principles

### Quick Reference
| Tool | Purpose | When to Use |
|------|---------|-------------|
| **Feng Shui (风水)** | Code quality | Architecture analysis, DI violations, security |
| **Gu Wu (顾武)** | Test quality | Running tests, coverage gaps, flaky detection |
| **Shi Fu (师傅)** | Ecosystem health | Weekly reviews, root cause analysis, correlations |

---

## 🏛️ By Tool

### Feng Shui (风水) - "Wind and Water"
**Philosophy**: Create harmonious flow in code architecture

**Documentation**:
- [CLI Guide](../../../tools/fengshui/README.md) - Complete command reference
- [Architecture](feng-shui/architecture.md) - Multi-agent system (Phase 4-17)
- [Pre-Commit Integration](integration/pre-commit-hooks.md) - Git hook setup
- [False Positives Guide](feng-shui/false-positives-guide.md) - Tuning & customization

**Key Features**:
- 6 specialized agents (parallel execution)
- ReAct autonomous agent
- Quality gate (22 checks)
- Batch auto-fixes

### Gu Wu (顾武) - "Attending to Martial Affairs"
**Philosophy**: Execute testing with discipline and continuous improvement

**Documentation**:
- [CLI Guide](../../../tools/guwu/README.md) - Complete command reference
- [Architecture](gu-wu/architecture.md) - Phase 7 intelligence hub
- [Testing Guide](gu-wu/testing-guide.md) - Best practices & patterns
- [Lessons Learned](gu-wu/lessons-learned.md) - Historical insights

**Key Features**:
- Intelligence Hub (3 engines)
- Test pyramid enforcement (70/20/10)
- Flaky test detection
- ML-powered failure prediction

### Shi Fu (师傅) - "The Master Teacher"
**Philosophy**: Code and tests are yin and yang - observe the whole, heal the root

**Documentation**:
- [CLI Guide](../../../tools/shifu/README.md) - Complete command reference
- [Meta-Architecture](shi-fu/meta-architecture.md) - Observer design
- [Correlation Patterns](shi-fu/correlation-patterns.md) - 5 root cause patterns
- [Cline Integration](shi-fu/cline-integration.md) - AI assistant workflow

**Key Features**:
- 5 correlation patterns
- Cross-domain intelligence
- Priority-based teachings
- Auto PROJECT_TRACKER.md updates

---

## 🔧 Integration Guides

### Git Hooks & CI/CD
- **[Pre-Commit Hooks](integration/pre-commit-hooks.md)** - Feng Shui + Gu Wu validation
- **[Pre-Push Analysis](integration/pre-push-analysis.md)** - Full quality check
- **[Quality Gates](integration/quality-gates.md)** - Three-tier system

### Future Roadmap
- **[Orchestrator Integration](integration/future-roadmap.md)** - Gu Wu as 7th agent
- **[Unified Analysis](integration/unified-analysis.md)** - Single command pipeline

---

## 📚 Guidelines & Best Practices

### Feng Shui Guidelines
- [Separation of Concerns](feng-shui/separation-of-concerns.md)
- [False Positives Tuning](feng-shui/false-positives-guide.md)
- [GoF Pattern Checks](feng-shui/gof-pattern-checks.md)

### Gu Wu Guidelines
- [Testing Enforcement](gu-wu/testing-enforcement.md)
- [Framework Audit](gu-wu/framework-audit.md)
- [Lessons Learned](gu-wu/lessons-learned.md)

### Shi Fu Guidelines
- [Meta-Agent vs Consultant Clarification](feng-shui-meta-agent-vs-shifu-clarification.md)
- [When to Use Each Tool](quality-ecosystem-vision.md#when-to-use-each-tool)

---

## 📂 Archive

### Completed Implementation Plans
- [Feng Shui Phase 4-15](../archive/implementations/feng-shui-phase4-15-implementation-plan.md)
- [Feng Shui Phase 4-16](../archive/implementations/feng-shui-phase4-16-implementation-plan.md)
- [Feng Shui Phase 4-17](../archive/implementations/feng-shui-phase4-17-implementation-plan.md)
- [Gu Wu Phase 4](../archive/implementations/guwu-phase4-pattern-integration.md)

### Old Proposals
- [Feng Shui Enhancement Plan v4.12](../archive/proposals/feng-shui-enhancement-plan-v4.12.md)
- [Gu Wu Frontend Testing](../archive/proposals/guwu-frontend-testing-proposal.md)
- [App V2 Validator Refactoring](../archive/proposals/app-v2-validator-refactoring-proposal.md)

---

## 🎯 Common Tasks

### Daily Development
```bash
# 1. Start session (check ecosystem health)
python -m tools.shifu --session-start

# 2. Make changes, then analyze
python -m tools.fengshui analyze --module my_module

# 3. Run tests
python -m tools.guwu run

# 4. Commit (pre-commit hooks run automatically)
git commit -m "Your changes"
```

### Weekly Quality Review
```bash
# Run Shi Fu weekly analysis
python -m tools.shifu --weekly-analysis

# Check recommendations
python -m tools.guwu recommend

# Review PROJECT_TRACKER.md for new priorities
```

### Before Deployment
```bash
# Quality gate check
python -m tools.fengshui gate --module my_module

# Pre-flight test check
python -m tools.guwu predict --pre-flight

# Full ecosystem health
python -m tools.shifu --health-check
```

---

## 🔍 Finding Information

### By Topic
- **Architecture violations**: Feng Shui docs → Architecture.md
- **Test failures**: Gu Wu docs → Testing Guide
- **Root causes**: Shi Fu docs → Correlation Patterns
- **Integration**: Integration docs → specific guide

### By Question
- "How do I run quality checks?" → Tool READMEs (Quick Start)
- "Why are my tests flaky?" → Shi Fu Correlation Patterns
- "What's the philosophy?" → Quality Ecosystem Vision
- "How do tools work together?" → Integration guides

### Search Tips
```bash
# Find all Feng Shui documentation
grep -r "Feng Shui" docs/knowledge/quality-ecosystem/

# Find integration guides
ls docs/knowledge/quality-ecosystem/integration/

# Find archived proposals
ls docs/knowledge/archive/proposals/
```

---

## 📊 Documentation Structure

```
quality-ecosystem/
├── README.md (this file)
├── quality-ecosystem-vision.md (central philosophy)
│
├── feng-shui/ (Code quality documentation)
│   ├── architecture.md
│   ├── false-positives-guide.md
│   └── [other Feng Shui docs]
│
├── gu-wu/ (Test quality documentation)
│   ├── architecture.md
│   ├── testing-guide.md
│   └── [other Gu Wu docs]
│
├── shi-fu/ (Ecosystem documentation)
│   ├── meta-architecture.md
│   ├── correlation-patterns.md
│   └── [other Shi Fu docs]
│
└── integration/ (Cross-tool documentation)
    ├── pre-commit-hooks.md
    ├── future-roadmap.md
    └── [other integration docs]
```

---

## 🤝 Contributing

When adding new quality ecosystem documentation:

1. **Determine scope**: Feng Shui, Gu Wu, Shi Fu, or Integration?
2. **Check existing**: Search before creating duplicates
3. **Follow structure**: Place in appropriate subdirectory
4. **Update this index**: Add link in relevant section
5. **Cross-reference**: Link to related docs

### Document Naming Convention
- `[tool]-[topic].md` - Tool-specific documentation
- `[feature]-[aspect].md` - Feature documentation
- `[concept].md` - Conceptual/philosophical documentation

---

## 📖 Related Resources

### External Documentation
- [.clinerules](../../.clinerules) - Development standards (sections 5, 7, 8)
- [PROJECT_TRACKER.md](../../PROJECT_TRACKER.md) - Active quality work packages
- [tests/README.md](../../../tests/README.md) - Testing structure guide

### Tool Documentation
- [docs/FENG_SHUI_ROUTINE_REQUIREMENTS.md](../../FENG_SHUI_ROUTINE_REQUIREMENTS.md) - Routine checks
- [tests/guwu/](../../../tests/guwu/) - Gu Wu implementation
- [tools/shifu/](../../../tools/shifu/) - Shi Fu implementation

---

**Version**: 1.0.0  
**Last Updated**: 2026-02-12  
**Maintained by**: P2P Development Team

**Navigation**: [← Back to Knowledge Vault](../INDEX.md) | [↑ Quality Ecosystem Vision](quality-ecosystem-vision.md)