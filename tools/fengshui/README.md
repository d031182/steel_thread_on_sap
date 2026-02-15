# Feng Shui (风水) - Multi-Agent Architecture Intelligence

**Version**: 4.6  
**Philosophy**: "Wind and Water" - Harmonious flow in codebase architecture

## 🎯 Overview

Feng Shui is a multi-agent system for analyzing and improving code architecture quality. Like its namesake - the Chinese practice of harmonizing energy flow - Feng Shui ensures clean, maintainable code through automated detection and repair of architectural violations.

### Key Features

- **7 Specialized AI Agents** working in parallel
- **ReAct Architecture** (Reason → Act → Observe → Reflect)
- **Multi-Agent Orchestration** with conflict detection
- **Autonomous Batch Fixes** via intelligent planning
- **Pre-commit/Pre-push Hooks** for quality gates
- **Infinite Loop Protection** (max 10K file scan limit)

## 🚀 Quick Start

### Installation

No installation needed - Feng Shui is part of the project tools.

### Basic Usage

```bash
# Show help and available commands
python -m tools.fengshui

# Run comprehensive analysis (all modules)
python -m tools.fengshui analyze

# Analyze specific module
python -m tools.fengshui analyze --module knowledge_graph_v2

# Run quality gate (before deployment)
python -m tools.fengshui gate --module data_products_v2

# Quick security check
python -m tools.fengshui critical
```

## 📋 Commands

### `analyze` - Multi-Agent Comprehensive Analysis

Runs all 7 specialized agents in parallel for comprehensive code quality analysis.

```bash
# Analyze all modules (parallel execution)
python -m tools.fengshui analyze

# Analyze specific module
python -m tools.fengshui analyze --module knowledge_graph_v2

# Sequential execution (for debugging)
python -m tools.fengshui analyze --sequential
```

**What it does**:
- Runs 7 agents: Architecture, Security, UX, Performance, FileOrg, Documentation, TestCoverage
- Detects conflicts between agent recommendations
- Synthesizes unified action plan
- Generates health score (0-100)
- Saves report to `feng_shui_report_*.json`

**Speed**: Up to 7x faster with parallel execution

### `fix` - Autonomous ReAct Agent

Autonomously detects and fixes architecture violations using intelligent planning.

```bash
# Run with default settings (target score: 95)
python -m tools.fengshui fix

# Custom target score and iterations
python -m tools.fengshui fix --target-score 90 --max-iterations 5
```

**What it does**:
1. Analyzes current architecture state
2. Creates dependency-aware execution plan
3. Executes fixes in parallel (up to 3x faster)
4. Learns from outcomes, improves strategy
5. Reports detailed metrics

⚠️ **Caution**: Modifies files automatically. Commit current work first!

### `gate` - Module Quality Gate

Validates a module before deployment. Must pass (exit 0) to deploy.

```bash
# Validate specific module
python -m tools.fengshui gate --module data_products_v2
```

**Checks**:
- ✅ No DI violations (.connection, .service access)
- ✅ No direct module imports
- ✅ Blueprint self-registers via module.json
- ✅ Uses interfaces from core.interfaces
- ✅ Tests in correct location

**Exit codes**:
- `0` = PASSED (ready for deployment)
- `1` = FAILED (fix violations first)

### `critical` - Security-Only Check

Fast security scan for critical issues only.

```bash
# Run security check
python -m tools.fengshui critical
```

**Detects**:
- 🔒 Hardcoded secrets/passwords
- 🔒 SQL injection vulnerabilities
- 🔒 Authentication issues
- 🔒 Insecure data handling

**Speed**: < 5 seconds (fast)

### `pre-commit` - Pre-Commit Validation

Runs automatically on `git commit`. Fast validation (< 2s target).

```bash
# Manual execution
python -m tools.fengshui pre-commit

# Bypass (emergency only)
git commit --no-verify
```

**Checks**:
- File organization
- Critical security issues
- Basic architecture compliance

### `pre-push` - Pre-Push Validation

Runs automatically on `git push`. Comprehensive validation (35-80s).

```bash
# Manual execution
python -m tools.fengshui pre-push
```

**Checks**:
- Full Feng Shui orchestrator analysis
- All 7 agents run
- Complete quality assessment

## 🤖 The 7 Specialized Agents

### 1. ArchitectAgent - Code Structure
**Detects**:
- Dependency Injection violations
- SOLID principle violations
- Tight coupling issues
- Module boundary violations

**Priority**: HIGH

### 2. SecurityAgent - Security Issues
**Detects**:
- Hardcoded secrets
- SQL injection risks
- Authentication flaws
- Insecure data handling

**Priority**: URGENT

### 3. UXArchitectAgent - UI/UX Quality
**Detects**:
- SAP Fiori compliance issues
- UI/UX pattern violations
- Accessibility problems
- Design system deviations

**Priority**: MEDIUM

### 4. FileOrganizationAgent - Structure
**Detects**:
- Misplaced files
- Obsolete code
- Directory structure issues
- Naming convention violations

**Priority**: LOW

### 5. PerformanceAgent - Performance
**Detects**:
- N+1 query problems
- Nested loop inefficiencies
- Missing caching opportunities
- Resource leaks

**Priority**: MEDIUM

### 6. DocumentationAgent - Documentation
**Detects**:
- Missing README files
- Poor docstring coverage
- Outdated documentation
- Missing code comments

**Priority**: LOW

### 7. TestCoverageAgent - Test Quality & API Contracts
**Detects**:
- Missing API contract tests (Gu Wu methodology)
- Missing `@pytest.mark.api_contract` markers
- Internal import anti-patterns (should use HTTP requests)
- Missing backend/frontend API test coverage
- Test quality issues

**Priority**: HIGH

**Integration**: Enforces [[Gu Wu API Contract Testing Foundation]]

## 📊 Output & Reports

### Console Output

```
======================================================================
  风水 FENG SHUI - Multi-Agent Architecture Intelligence
  'Wind and Water' - Harmonious Code Flow
======================================================================

📦 Target: knowledge_graph_v2

🔍 Running 7 specialized agents in parallel...
   1. Architecture Agent ✅ (0 issues)
   2. Security Agent ✅ (0 issues)
   3. UX Architect Agent ⚠️ (2 issues)
   4. File Organization Agent ✅ (0 issues)
   5. Performance Agent ⚠️ (1 issue)
   6. Documentation Agent ✅ (0 issues)
   7. Test Coverage Agent ✅ (0 issues)

✅ Analysis Complete!
   Overall Health: 92/100
   Report saved to: feng_shui_report_knowledge_graph_v2.json
```

### JSON Report

```json
{
  "overall_health": {
    "score": 92,
    "status": "healthy"
  },
  "agent_results": {
    "architecture": { "score": 100, "issues": [] },
    "security": { "score": 100, "issues": [] },
    "ux": { "score": 85, "issues": [...] },
    "performance": { "score": 90, "issues": [...] },
    "file_org": { "score": 100, "issues": [] },
    "documentation": { "score": 100, "issues": [] }
  },
  "conflicts": [],
  "action_plan": [...]
}
```

## 🔧 Integration

### Git Hooks (Automatic)

Feng Shui integrates with git automatically:

```bash
# Pre-commit (< 2s) - runs on 'git commit'
.git/hooks/pre-commit

# Pre-push (35-80s) - runs on 'git push'
.git/hooks/pre-push
```

### CI/CD Pipeline

```yaml
# Example GitHub Actions
- name: Feng Shui Quality Gate
  run: python -m tools.fengshui gate --module ${{ matrix.module }}
```

### Manual Workflow

```bash
# 1. Analyze current state
python -m tools.fengshui analyze --module my_module

# 2. Review report
cat feng_shui_report_my_module.json

# 3. Run quality gate
python -m tools.fengshui gate --module my_module

# 4. If failed, fix issues or run autonomous agent
python -m tools.fengshui fix --target-score 95
```

## 🎓 Best Practices

### When to Use Each Command

| Scenario | Command | Frequency |
|----------|---------|-----------|
| Daily development | `pre-commit` | Automatic |
| Before git push | `pre-push` | Automatic |
| Feature completion | `analyze` | Per feature |
| Pre-deployment | `gate` | Always |
| Security audit | `critical` | Weekly |
| Batch fixes | `fix` | As needed |

### Interpreting Health Scores

- **90-100**: Excellent (production-ready)
- **75-89**: Good (minor improvements needed)
- **60-74**: Fair (address issues before deploy)
- **< 60**: Poor (significant refactoring needed)

### Fixing Common Issues

**DI Violations**:
```python
# ❌ Wrong
def my_function():
    db = get_app().connection  # Hardwired dependency

# ✅ Correct
def my_function(db_connection):
    db = db_connection  # Injected dependency
```

**Module Imports**:
```python
# ❌ Wrong
from modules.other_module import function

# ✅ Correct
from core.interfaces import IService
```

**Blueprint Registration**:
```json
// module.json
{
  "backend": {
    "blueprint": "modules.my_module.backend.api:blueprint"
  }
}
```

## 🔍 Troubleshooting

### Agent Errors

If agents show errors (`analyze_file` attribute missing):
- Check agent implementation updated
- Verify orchestrator integration
- Review Phase 4-17 implementation

### Slow Performance

If analysis takes > 2 minutes:
- Use `--sequential` flag to debug
- Check for infinite loops (max 10K files)
- Review file scan patterns

### False Positives

If Feng Shui flags valid code:
- Add to `.feng_shui_ignore` file
- See `docs/knowledge/guidelines/feng-shui-false-positives.md`
- Update agent sensitivity thresholds

## 📚 Advanced Usage

### Legacy Commands (Still Supported)

```bash
# Direct ReAct agent (legacy)
python -m tools.fengshui.react_agent --target-score 95

# Direct quality gate (legacy)
python tools/fengshui/module_quality_gate.py knowledge_graph_v2
```

### Custom Configuration

```python
# Via Python API
from tools.fengshui.react_agent import FengShuiReActAgent

agent = FengShuiReActAgent()
report = agent.run_with_multiagent_analysis(
    Path('modules/my_module'),
    parallel=True
)
```

## 📖 Related Documentation

- [[Feng Shui Phase 4-17 Multi-Agent]] - Implementation details
- `docs/FENG_SHUI_ROUTINE_REQUIREMENTS.md` - Requirements
- `docs/knowledge/guidelines/feng-shui-false-positives.md` - False positive handling
- `.clinerules` - Development standards (Section 5)

## 🤝 Contributing

Feng Shui is part of the quality ecosystem:

```
Feng Shui → Analyzes code architecture
    ↓
Gu Wu → Analyzes test quality
    ↓
Shi Fu → Finds correlations (meta-intelligence)
```

When extending Feng Shui:
1. Add new agent in `tools/fengshui/agents/`
2. Register in orchestrator
3. Update documentation
4. Add tests in `tests/unit/tools/fengshui/`

## 📜 Philosophy

> "In Feng Shui, energy must flow harmoniously. In code, dependencies must flow cleanly. Blocked energy causes stagnation; hardwired dependencies cause technical debt. The master maintains balance through proper structure."

**Core Principles**:
- 🌊 **Flow**: Dependencies should flow naturally (Dependency Injection)
- 💨 **Clarity**: Code structure should be self-evident
- 🏔️ **Stability**: Architecture should resist erosion
- 🌳 **Growth**: Design should accommodate future change

---

**Version**: 4.6  
**Last Updated**: 2026-02-15  
**License**: MIT
