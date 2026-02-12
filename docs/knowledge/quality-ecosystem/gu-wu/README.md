# Gu Wu (顾武) Documentation

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
