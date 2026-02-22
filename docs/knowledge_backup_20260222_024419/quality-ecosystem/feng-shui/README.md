# Feng Shui (风水) Documentation

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
