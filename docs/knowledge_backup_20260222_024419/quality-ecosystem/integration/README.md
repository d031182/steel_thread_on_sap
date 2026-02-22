# Quality Ecosystem Integration Documentation

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
