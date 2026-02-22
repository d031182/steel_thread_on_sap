# Gu Wu Resolver Expansion - Multi-Capability Issue Resolution

**Date**: 2026-02-22  
**Status**: Phase 1 - Infrastructure Complete  
**Version**: 1.0

## 🎯 Objective

Transform Gu Wu from single-purpose test generator to multi-capability resolver that can address various quality issues detected by Feng Shui agents.

**Philosophy**: "Attending to Martial Affairs" - Self-healing codebase

## 📊 Current State

### Completed (Phase 1)
✅ Base resolver infrastructure created
✅ Resolver registry implemented
✅ Safety-first design with dry-run defaults

### Files Created
1. `tools/guwu/resolvers/__init__.py` - Package exports
2. `tools/guwu/resolvers/base_resolver.py` - Abstract base class (~280 lines)
3. `tools/guwu/resolvers/resolver_registry.py` - Central registry (~95 lines)

## 🏗️ Architecture

### Base Resolver Pattern

```python
class BaseResolver(ABC):
    """
    Principles:
    - SAFETY FIRST: Dry-run by default
    - TRANSPARENCY: Log all actions
    - ROLLBACK: Support undo operations
    - SELECTIVE: User choice per finding
    """
    
    @abstractmethod
    def can_resolve(self, finding) -> bool:
        """Check if resolver handles this finding"""
    
    @abstractmethod
    def resolve_finding(self, finding, dry_run=True) -> ResolutionResult:
        """Resolve single finding"""
    
    def resolve_findings(self, findings, dry_run=True, interactive=False):
        """Batch resolution with interactive mode"""
```

### Resolution Result

```python
@dataclass
class ResolutionResult:
    status: ResolutionStatus  # SUCCESS, PARTIAL, FAILED, SKIPPED, DRY_RUN
    findings_resolved: int
    findings_failed: int
    findings_skipped: int
    actions_taken: List[str]
    errors: List[str]
    warnings: List[str]
    dry_run_actions: List[str]
```

### Resolver Registry

```python
class ResolverRegistry:
    """
    Central registry managing all resolvers
    
    Methods:
    - register(category, resolver)
    - get_resolver(category)
    - resolve_findings(findings, category, dry_run, interactive)
    - list_resolvers()
    - get_capabilities()
    """
```

## 📋 Next Steps (Phase 2)

### 1. File Organization Resolver
**File**: `tools/guwu/resolvers/file_organization_resolver.py`

**Responsibilities**:
- Parse Feng Shui file_organization_agent findings
- Move files to correct directories
- Update imports in moved files
- Update imports in files that reference moved files

**Example Finding Format** (from file_organization_agent):
```python
{
    'file': 'path/to/file.py',
    'issue': 'Wrong directory',
    'expected': 'tests/ai_assistant/',
    'actual': 'tests/'
}
```

**Resolution Actions**:
```python
# Dry-run mode
result.add_dry_run_action("WOULD move: tests/test_ai.py → tests/ai_assistant/test_ai.py")
result.add_dry_run_action("WOULD update 3 import statements")

# Execute mode
result.add_action("Moved: tests/test_ai.py → tests/ai_assistant/test_ai.py")
result.add_action("Updated imports in: conftest.py, test_helper.py, __init__.py")
```

### 2. CLI Integration
**File**: `tools/guwu/__main__.py`

**New Command**:
```bash
# List available resolvers
python -m tools.guwu resolve --list

# Dry-run (default)
python -m tools.guwu resolve --category file_organization

# Execute (requires confirmation)
python -m tools.guwu resolve --category file_organization --execute

# Interactive mode (prompt per finding)
python -m tools.guwu resolve --category file_organization --execute --interactive
```

### 3. Feng Shui Integration
**File**: `tools/guwu/feng_shui_integration.py` (update)

**Add**:
```python
def resolve_feng_shui_findings(agent_name: str, dry_run: bool = True):
    """
    Run Feng Shui agent and resolve findings
    
    Args:
        agent_name: e.g., 'file_organization', 'test_coverage'
        dry_run: Safety flag
    
    Returns:
        ResolutionResult
    """
    # 1. Run Feng Shui agent
    findings = run_feng_shui_agent(agent_name)
    
    # 2. Get appropriate resolver
    registry = get_registry()
    
    # 3. Resolve findings
    return registry.resolve_findings(findings, agent_name, dry_run)
```

### 4. Test Generator Refactoring
**File**: `tools/guwu/resolvers/test_generator_resolver.py`

**Goal**: Refactor existing test generation to use resolver pattern

**Benefits**:
- Consistent interface with other resolvers
- Shared safety features (dry-run, interactive)
- Better integration with Feng Shui test_coverage_agent

### 5. Tests
**File**: `tests/unit/tools/guwu/test_resolvers.py`

**Coverage**:
- BaseResolver contract compliance
- ResolverRegistry registration/dispatch
- File organization resolver (dry-run + execute)
- Safety mechanisms (dry-run default, interactive confirmations)
- Error handling

### 6. Documentation
**Files**:
- `tools/guwu/resolvers/README.md` - Resolver developer guide
- Update `tools/guwu/README.md` - Add resolver capabilities
- Update `.clinerules` - Document resolver workflow

## 🔄 Workflow Integration

### Developer Workflow
```bash
# 1. Run Feng Shui analysis
python -m tools.fengshui analyze

# 2. Review findings
python -m tools.fengshui analyze --agent file_organization

# 3. Dry-run resolution (see what would happen)
python -m tools.guwu resolve --category file_organization

# 4. Execute if satisfied
python -m tools.guwu resolve --category file_organization --execute
```

### CI/CD Integration
```yaml
# .github/workflows/quality-gate.yml
- name: Run Feng Shui Analysis
  run: python -m tools.fengshui analyze --json > findings.json

- name: Auto-resolve safe findings
  run: python -m tools.guwu resolve --from-file findings.json --safe-only

- name: Create PR for remaining findings
  if: ${{ steps.resolve.outputs.unresolved > 0 }}
  run: |
    python -m tools.guwu resolve --from-file findings.json --create-pr
```

## 🎨 Design Principles

### Safety-First
- **Dry-run default**: All resolvers default to simulation mode
- **Explicit confirmation**: Require `--execute` flag for real changes
- **Interactive mode**: Per-finding approval with `--interactive`
- **Rollback support**: Track actions for potential undo

### Transparency
- **Detailed logging**: Every action logged with context
- **Clear output**: Human-readable resolution reports
- **Audit trail**: Actions stored for review

### Modularity
- **Independent resolvers**: Each resolver is self-contained
- **Registry pattern**: Loose coupling via registry
- **Extensible**: Easy to add new resolver types

### User Experience
- **Progressive disclosure**: Start simple, expose power gradually
- **Sensible defaults**: Dry-run, non-interactive
- **Clear feedback**: Rich output with colors, formatting

## 📈 Future Resolver Types

### Potential Resolvers (Post-MVP)
1. **CSS Refactoring Resolver** (Feng Shui UX agent findings)
   - Consolidate duplicate styles
   - Fix color contrast violations
   - Organize CSS into modular structure

2. **Security Resolver** (Feng Shui Security agent findings)
   - Fix SQL injection vulnerabilities
   - Add input validation
   - Update dependencies

3. **Performance Resolver** (Feng Shui Performance agent findings)
   - Optimize database queries
   - Add caching layers
   - Reduce N+1 queries

4. **Documentation Resolver** (Feng Shui Documentation agent findings)
   - Generate missing docstrings
   - Update outdated docs
   - Create API documentation

## 🔗 Related Documents

- [[Feng Shui Architecture Audit 2026-02-15]]
- [[Gu Wu API Contract Testing Foundation]]
- [[Module Federation Standard]]
- [[Quality Ecosystem README]]

## 📝 Implementation Notes

### Key Learnings
1. **Interplay Pattern**: Similar to test_coverage_agent → Gu Wu test generator
2. **Feng Shui detects**, **Gu Wu resolves** - clear separation of concerns
3. **Registry pattern** enables extensibility without coupling
4. **Safety defaults** prevent accidental damage

### Technical Decisions
- Used `@dataclass` for ResolutionResult (clean, immutable-ish)
- Separate `dry_run_actions` list for clarity
- Interactive mode prompts per-finding (not batch)
- Status enum provides clear resolution states

### Challenges Addressed
- **Safety**: Dry-run default with explicit execute flag
- **Flexibility**: Category-based dispatch allows specialization
- **Usability**: Rich result objects with detailed feedback
- **Extensibility**: ABC + registry = easy to add resolvers

## ✅ Success Criteria

### Phase 1 (Complete)
- [x] Base resolver infrastructure
- [x] Resolver registry
- [x] Safety mechanisms

### Phase 2 (Next)
- [ ] File organization resolver implementation
- [ ] CLI integration with `resolve` command
- [ ] Feng Shui integration
- [ ] Comprehensive tests (80%+ coverage)
- [ ] Documentation complete

### Phase 3 (Future)
- [ ] Test generator refactored to resolver pattern
- [ ] CI/CD integration
- [ ] Additional resolver types
- [ ] Performance benchmarks

## 🎯 Summary

**Gu Wu's Evolution**: From single-purpose test generator to multi-capability resolver system

**Core Insight**: "Test the contract, trust the implementation" applies to quality fixes too - resolve the symptoms (Feng Shui findings), trust the underlying architecture.

**Next Action**: Implement file_organization_resolver.py to resolve file placement issues autonomously.

---

**Version History**:
- v1.0 (2026-02-22): Initial implementation, base infrastructure complete